from fastapi import APIRouter
from elda.ai.state import app_state
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()

# In-memory caregiver chat history (per server session)
_caregiver_chat_history: List[dict] = []


class BroadcastMessage(BaseModel):
    message: str


class ScheduleMessage(BaseModel):
    message: str
    time: str  # Format: "HH:MM"


class AskMessage(BaseModel):
    question: str
    history: List[dict] = []  # optional client-side history


@router.get("/dashboard")
async def get_dashboard() -> Dict[str, Any]:
    """Returns live patient status for caregiver apps."""
    return {
        "status": app_state.patient_status,
        "risk_level": app_state.latest_risk_level,
        "emotion": app_state.latest_emotion,
        "last_interaction": app_state.last_interaction,
        "risk_reason": app_state.risk_reason,
        "username": app_state.username,
        "heart_rate": app_state.vitals.get("heart_rate", 72),
        "oxygen": app_state.vitals.get("oxygen", 98),
    }


@router.post("/broadcast")
async def broadcast_to_patient(payload: BroadcastMessage):
    """Caregiver sends a message that appears/speaks on patient terminal."""
    if not payload.message:
        return {"error": "Message cannot be empty."}

    # Set pending broadcast — patient polls and picks it up
    app_state.pending_broadcast = payload.message
    app_state.last_interaction = f"[Caregiver] {payload.message}"

    # Also speak it on the server-side patient terminal
    try:
        from elda.ai.elda_core import elda_ai
        elda_ai.speak(f"Message from your caregiver: {payload.message}")
    except Exception as e:
        print(f"[Broadcast] TTS error: {e}")

    return {"status": "success", "message": "Broadcast sent to patient."}


@router.post("/schedule_broadcast")
async def schedule_broadcast(payload: ScheduleMessage):
    """Schedules a broadcast message at a specific time."""
    try:
        hours, minutes = map(int, payload.time.split(":"))
        msg = payload.message

        from datetime import datetime, timedelta
        import threading
        from elda.ai.elda_core import elda_ai

        now = datetime.now()
        target = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if target < now:
            target += timedelta(days=1)

        delay = (target - now).total_seconds()

        def run_job():
            app_state.pending_broadcast = msg
            app_state.last_interaction = f"[Scheduled] {msg}"
            elda_ai.speak(f"Scheduled message from your caregiver: {msg}")

        threading.Timer(delay, run_job).start()
        return {"status": "success", "scheduled_for": payload.time}
    except Exception as e:
        return {"error": str(e)}


@router.post("/ask")
def ask_caregiver_ai(payload: AskMessage):
    """Caregiver AI chat — uses dedicated caregiver AI (Ollama/Qwen)."""
    from elda.ai.caregiver_ai import get_caregiver_response

    # Use history from payload or server-side history
    history = payload.history if payload.history else _caregiver_chat_history[-10:]

    reply = get_caregiver_response(payload.question, history)

    # Update server-side history
    _caregiver_chat_history.append({"role": "user", "content": payload.question})
    _caregiver_chat_history.append({"role": "assistant", "content": reply})
    if len(_caregiver_chat_history) > 20:
        _caregiver_chat_history[:] = _caregiver_chat_history[-20:]

    return {"response": reply}


@router.get("/emotion_history")
async def get_emotion_history(limit: int = 50) -> Dict[str, Any]:
    """Returns timestamped emotion history from DB for the caregiver dashboard."""
    try:
        from elda.db.session import get_session
        from elda.db.models import Interaction
        session = get_session()
        try:
            records = session.query(Interaction).order_by(
                Interaction.timestamp.desc()
            ).limit(limit).all()
            history = []
            for r in records:
                if r.content:
                    history.append({
                        "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M") if r.timestamp else "",
                        "content": r.content[:80] + ("…" if len(r.content) > 80 else ""),
                        "emotion": getattr(r, "emotion", "Neutral") or "Neutral",
                        "response": (getattr(r, "response_content", "") or "")[:80],
                    })
            return {"history": list(reversed(history))}
        finally:
            session.close()
    except Exception as e:
        return {"history": [], "error": str(e)}

from typing import Optional

class ReportRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None

@router.post("/upload_report")
async def upload_report(req: ReportRequest) -> Dict[str, Any]:
    """Receives a medical report (text or base64 image), performs OCR if needed, and saves it, generating an AI summary."""
    try:
        import os
        from elda.ai.elda_core import elda_ai
        
        extracted_text = ""
        
        if req.image_base64:
            import base64
            import numpy as np
            import cv2
            import easyocr
            
            # Decode base64 image to numpy array
            img_data = base64.b64decode(req.image_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # OCR the image
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(img)
            extracted_text = "\n".join([r[1] for r in results])
        elif req.text:
            extracted_text = req.text
        else:
            return {"status": "error", "message": "No text or image provided."}
            
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        raw_path = os.path.join(data_dir, "last_raw_report.txt")
        
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
            
        summary = elda_ai.analyze_medical_report(extracted_text)
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}
