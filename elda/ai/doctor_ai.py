"""
Doctor AI — Separate Ollama-powered assistant for clinicians.
Provides detailed physiological and psychological diagnostic support.
"""
import ollama

OLLAMA_MODEL = "qwen2.5:3b"

DOCTOR_SYSTEM_PROMPT = """You are a highly analytical clinical AI assistant acting as a consultant to a physician treating an Alzheimer's patient.

Your role:
- Discuss patient symptoms, clinical progression, and medication efficacy.
- Give evidence-based, medically structured insights using professional clinical terminology.
- You are not speaking to the patient; you are speaking peer-to-peer with a doctor.

Maintain a clinical, objective, and analytical tone."""


def get_doctor_response(question: str, history: list = None) -> str:
    """Get a response from the doctor AI assistant."""
    sys_prompt = DOCTOR_SYSTEM_PROMPT
    
    from elda.ai.elda_core import elda_ai
    from elda.ai.state import app_state
    
    med_summary = elda_ai.get_active_medical_summary()
    
    sys_prompt += "\n\n--- LIVE PATIENT STATUS ---\n"
    sys_prompt += f"Patient Name: {app_state.username or 'Unknown'}\n"
    sys_prompt += f"Current Emotion: {app_state.latest_emotion or 'Neutral'}\n"
    sys_prompt += f"Current Risk Level: {app_state.latest_risk_level or 'Low'}\n"
    sys_prompt += f"Recent Behavior Context: {app_state.risk_reason or 'None'}\n"

    if med_summary:
        sys_prompt += f"\n\n--- CRITICAL CLINICAL DOSSIER ---\n{med_summary}\n\nYou MUST incorporate the diagnostic context above when answering."

    messages = [{"role": "system", "content": sys_prompt}]

    # Include chat history for continuity
    if history:
        messages.extend(history[-10:])

    messages.append({"role": "user", "content": question})

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": 0.3, "num_predict": 400}
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Clinical Core unavailable: {e}"
