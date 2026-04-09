from fastapi import APIRouter
from pydantic import BaseModel
from elda.ai.state import app_state

router = APIRouter()


class InteractRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/interact")
async def interact(request: InteractRequest):
    """Patient chat endpoint — calls ELDA AI and returns response + speaks it."""
    from elda.ai.elda_core import elda_ai
    response_text = elda_ai.generate_response(request.text, request.language)
    return {"response": response_text}


@router.get("/vitals")
async def get_vitals():
    """Returns current vitals (from hardware sensor or simulated)."""
    return {
        "heart_rate": app_state.vitals.get("heart_rate", 72),
        "oxygen": app_state.vitals.get("oxygen", 98),
        "hardware_connected": app_state.hardware_connected,
    }


@router.get("/broadcast_pending")
async def get_broadcast_pending():
    """Patient terminal polls this endpoint to receive caregiver broadcasts.
    Returns the pending message and clears it (one-time delivery).
    """
    msg = app_state.pending_broadcast
    if msg:
        app_state.pending_broadcast = ""  # clear after delivery
        return {"message": msg, "has_message": True}
    return {"message": "", "has_message": False}
