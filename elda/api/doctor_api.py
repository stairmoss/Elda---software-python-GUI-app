from fastapi import APIRouter
from elda.db.session import get_session
from elda.db.models import Interaction
from elda.ai.state import app_state
from typing import Dict, Any
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    history: List[dict] = []

@router.post("/ask")
def ask_doctor_ai(req: AskRequest) -> Dict[str, Any]:
    from elda.ai.doctor_ai import get_doctor_response
    response = get_doctor_response(req.question, req.history)
    return {"reply": response}


@router.get("/summary")
async def get_clinical_summary() -> Dict[str, str]:
    """Triggers the Elda AI to analyze the memory database and generate a clinical diagnosis paragraph remotely."""
    try:
        from elda.ai.elda_core import elda_ai
        summary = elda_ai.generate_clinical_summary()
        return {"summary": summary}
    except Exception as e:
        return {"summary": f"Summary unavailable: {e}"}


@router.get("/interactions")
async def get_interactions(limit: int = 50) -> Dict[str, Any]:
    """Retrieves standard database logs for external doctor/caregiver portals."""
    try:
        session = get_session()
        try:
            records = session.query(Interaction).order_by(Interaction.timestamp.desc()).limit(limit).all()
            history = []
            for r in records:
                entry = {
                    "id": r.id,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                    "sender": getattr(r, "sender", "Patient") or "Patient",
                    "content": r.content or "",
                    "response": getattr(r, "response_content", "") or "",
                    "emotion": getattr(r, "emotion", "Neutral") or "Neutral",
                    "type": getattr(r, "interaction_type", "") or "",
                }
                history.append(entry)
            return {"interactions": history}
        finally:
            session.close()
    except Exception as e:
        print(f"[Doctor API] Interactions error: {e}")
        return {"interactions": []}


@router.get("/status")
async def get_patient_status() -> Dict[str, Any]:
    """Quick live status endpoint for doctor portal."""
    return {
        "status": app_state.patient_status,
        "risk_level": app_state.latest_risk_level,
        "emotion": app_state.latest_emotion,
        "risk_reason": app_state.risk_reason,
        "username": app_state.username,
    }
