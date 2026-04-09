"""
Caregiver AI — Separate Ollama-powered assistant for caregivers.
Gives practical medical/care advice, completely independent from patient AI.
"""
import ollama

OLLAMA_MODEL = "qwen2.5:3b"

CAREGIVER_SYSTEM_PROMPT = """You are a knowledgeable, compassionate medical assistant supporting caregivers of Alzheimer's patients.

Your role:
- Give clear, practical, step-by-step care advice
- In emergencies (fainting, falls, choking, confusion), give immediate first aid steps
- Suggest communication strategies for difficult Alzheimer's situations
- Be warm but professional — you are their support pillar

Keep responses well-structured and actionable. Use bullet points when listing steps."""


def get_caregiver_response(question: str, history: list = None) -> str:
    """Get a response from the caregiver AI assistant."""
    sys_prompt = CAREGIVER_SYSTEM_PROMPT
    
    from elda.ai.elda_core import elda_ai
    med_summary = elda_ai.get_active_medical_summary()
    if med_summary:
        sys_prompt += f"\n\nCRITICAL CONTEXT (Patient Medical File):\n{med_summary}\n\nYou MUST use this information to provide tailored advice to the caregiver."

    messages = [{"role": "system", "content": sys_prompt}]

    # Include chat history for continuity
    if history:
        messages.extend(history[-10:])  # last 5 turns

    messages.append({"role": "user", "content": question})

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": 0.6, "num_predict": 400}
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"⚠️ AI temporarily unavailable: {e}\n\nFor emergencies, call 112 / local emergency services immediately."
