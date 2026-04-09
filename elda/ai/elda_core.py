"""
ELDA AI Core — Ollama/Qwen2.5:3b
Clean, fast, no blocking imports on first request.
"""
import threading
import pyttsx3
import ollama
import json
import re


OLLAMA_MODEL = "qwen2.5:3b"

PATIENT_SYSTEM_PROMPT = """You are ELDA, a deeply compassionate caregiver for Alzheimer's patients.
Your personality is warm, gentle, and understanding.
- Keep responses SHORT (2-3 sentences max) — never overwhelm them.
- If they repeat themselves, gently flow with their reality. Never point it out.
- Validate their feelings always.
- If they seem confused, gently re-orient them with kindness.
- Use simple words. Speak like you are talking to a dear grandparent."""

RISK_SYSTEM_PROMPT = """Analyze the patient message for distress, confusion, or emergency.
Return ONLY valid JSON with no extra text: {"risk_level": "Low", "reason": "..."}
risk_level must be exactly one of: Low, Medium, High"""

CLINICAL_SYSTEM_PROMPT = """You are a clinical AI analyst for Alzheimer's doctors.
Analyze patient interaction history and provide a structured clinical summary.
Be factual, concise, and medically appropriate. Keep under 200 words."""

MEDICAL_REPORT_ANALYSIS_PROMPT = """You are an expert clinical AI analyzing a patient medical report or history.
Generate a structured, concise medical dossier. Your output MUST use the following headers:
- Diagnoses
- Key Risks & Allergies
- Medications
- Critical Care Guidelines

Do NOT include pleasantries, just the structured medical summary. Keep it strictly factual, clear, and under 200 words."""


class EldaCore:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.is_speaking = False
        self._tts_lock = threading.Lock()
        self.tts_rate = 150
        self._chat_history = []   # multi-turn in-memory context
        print(f"[AI] ELDA Core ready — using Ollama {self.model}")

    # ── TTS ────────────────────────────────────────────────────────────────
    def speak(self, text: str):
        def _do():
            try:
                with self._tts_lock:
                    self.is_speaking = True
                engine = pyttsx3.init()
                engine.setProperty('rate', self.tts_rate)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[TTS] Error: {e}")
            finally:
                self.is_speaking = False
        threading.Thread(target=_do, daemon=True).start()

    # ── Main Response — fast path, no blocking I/O ─────────────────────────
    def generate_response(self, user_input: str, language: str = "en") -> str:
        from elda.ai.state import app_state
        app_state.last_interaction = user_input

        # Quick keyword emotion detection (no model load needed)
        self._run_emotion_analysis_sync(user_input)

        # Build prompt from in-memory chat history (no FAISS on hot path)
        sys_prompt = PATIENT_SYSTEM_PROMPT
        
        # Inject Active Medical Summary if available
        med_summary = self.get_active_medical_summary()
        if med_summary:
            sys_prompt += f"\n\nCRITICAL CONTEXT (Patient Medical File):\n{med_summary}\n\nPlease adapt your care and caution according to this medical file."

        messages = [{"role": "system", "content": sys_prompt}]
        messages.extend(self._chat_history[-8:])   # last 4 turns
        messages.append({"role": "user", "content": user_input})

        try:
            resp = ollama.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.7, "num_predict": 120}
            )
            bot_reply = resp['message']['content'].strip()
        except Exception as e:
            print(f"[AI] Ollama error: {e}")
            bot_reply = "I'm here with you. I may be having a little trouble right now, but I'm always listening."

        # Update in-memory conversation history
        self._chat_history.append({"role": "user",      "content": user_input})
        self._chat_history.append({"role": "assistant",  "content": bot_reply})
        if len(self._chat_history) > 20:
            self._chat_history = self._chat_history[-20:]

        # Non-blocking DB save + risk analysis
        threading.Thread(target=self._save_to_db,     args=(user_input, bot_reply), daemon=True).start()
        threading.Thread(target=self._run_risk_analysis, args=(user_input,),         daemon=True).start()

        return bot_reply

    # ── DB Save ────────────────────────────────────────────────────────────
    def _save_to_db(self, user_text: str, elda_reply: str):
        try:
            from elda.db.session import get_session
            from elda.db.models import Interaction
            from elda.ai.state import app_state
            session = get_session()
            try:
                session.add(Interaction(
                    content=user_text,
                    response_content=elda_reply,
                    sender="Patient",
                    emotion=app_state.latest_emotion,
                    interaction_type="voice"
                ))
                session.commit()
            except Exception as e:
                print(f"[DB] Save error: {e}")
                session.rollback()
            finally:
                session.close()
        except Exception as e:
            print(f"[DB] Session error: {e}")

    # ── Emotion Analysis (keyword-based, instant) ──────────────────────────
    def _run_emotion_analysis_sync(self, text: str):
        t = text.lower()
        emotion = "Neutral"
        if any(w in t for w in ["happy", "great", "wonderful", "joy", "love", "good", "fine"]):
            emotion = "Happy"
        elif any(w in t for w in ["sad", "cry", "miss", "lost", "alone", "lonely", "hurt"]):
            emotion = "Sad"
        elif any(w in t for w in ["anxious", "worried", "scared", "fear", "afraid", "panic", "nervous"]):
            emotion = "Anxious"
        elif any(w in t for w in ["confused", "don't know", "where", "who", "what is", "forget", "lost"]):
            emotion = "Confused"
        elif any(w in t for w in ["angry", "mad", "furious", "hate", "stop", "leave"]):
            emotion = "Angry"

        try:
            from elda.ai.state import app_state
            app_state.latest_emotion = emotion
        except Exception:
            pass

    # ── Risk Analysis (background, Ollama) ────────────────────────────────
    def _run_risk_analysis(self, text: str):
        try:
            resp = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": RISK_SYSTEM_PROMPT},
                    {"role": "user",   "content": text}
                ],
                options={"temperature": 0.1, "num_predict": 60}
            )
            content = resp['message']['content'].strip()
            from elda.ai.state import app_state
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                risk   = data.get("risk_level", "Low")
                reason = data.get("reason", "No anomalies.")
                app_state.risk_reason      = reason
                app_state.latest_risk_level = risk
                app_state.patient_status = {
                    "High": "Attention Needed",
                    "Medium": "Monitoring",
                    "Low": "Stable"
                }.get(risk, "Stable")
        except Exception as e:
            print(f"[Risk] Error: {e}")

    # ── Clinical Summary (for Doctor Dashboard) ────────────────────────────
    def generate_clinical_summary(self) -> str:
        try:
            from elda.db.session import get_session
            from elda.db.models import Interaction
            session = get_session()
            try:
                records = session.query(Interaction).order_by(
                    Interaction.timestamp.desc()
                ).limit(30).all()
                history_text = "\n".join([
                    f"[{r.timestamp.strftime('%Y-%m-%d %H:%M')}] Patient ({r.emotion}): {r.content}"
                    for r in records if r.content
                ])
            finally:
                session.close()
        except Exception:
            history_text = ""

        if not history_text:
            return "No interaction history available for clinical analysis."

        from elda.ai.state import app_state
        try:
            resp = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": CLINICAL_SYSTEM_PROMPT},
                    {"role": "user",   "content": (
                        f"Patient Interaction History:\n{history_text}\n\n"
                        f"Current Status: {app_state.patient_status}\n"
                        f"Risk Reason: {app_state.risk_reason}\n\n"
                        "Provide clinical summary covering:\n"
                        "1. Mood and emotional trends\n"
                        "2. Recurring cognitive issues\n"
                        "3. Risk assessment"
                    )}
                ],
                options={"temperature": 0.3, "num_predict": 300}
            )
            return resp['message']['content'].strip()
        except Exception as e:
            return f"AI Analysis Error: {e}"

    # ── Ensure Memory (optional background enrichment) ─────────────────────
    def _ensure_memory(self):
        """Load FAISS memory model in background — completely optional."""
        if hasattr(self, '_memory_loaded'):
            return
        self._memory_loaded = True
        try:
            from elda.ai.memory_model import MemoryModel
            self.memory = MemoryModel()
            print("[AI] FAISS memory model loaded.")
        except Exception as e:
            print(f"[AI] Memory model skipped: {e}")
            self.memory = None

    # ── Medical RAG Analysis (Processing Uploaded Reports) ─────────────────
    def analyze_medical_report(self, raw_text: str) -> str:
        """Process a raw text medical report and generate a concise dossier."""
        try:
            resp = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": MEDICAL_REPORT_ANALYSIS_PROMPT},
                    {"role": "user",   "content": f"Raw Medical Report:\n\n{raw_text}"}
                ],
                options={"temperature": 0.2, "num_predict": 300}
            )
            dossier = resp['message']['content'].strip()
            
            import os
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            summary_path = os.path.join(data_dir, "active_patient_summary.md")
            
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(dossier)
                
            return dossier
        except Exception as e:
            return f"Error analyzing report: {e}"

    def get_active_medical_summary(self) -> str:
        import os
        summary_path = os.path.join(os.path.dirname(__file__), "..", "data", "active_patient_summary.md")
        if os.path.exists(summary_path):
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except:
                pass
        return ""


# Singleton
elda_ai = EldaCore()
