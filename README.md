# 🧠 ELDA — COMPLETE PROJECT BLUEPRINT

## 1️⃣ SYSTEM OVERVIEW (BIG PICTURE)
ELDA is a localized AI caregiving system designed to run silently in the background, assisting Alzheimer's patients via voice/chat while providing intelligent dashboards for caregivers and doctors.

### Architecture
- **Patient**: Interacts via Voice/Text (No complex UI)
- **ELDA AI**: Powered by Qwen 2.5 3B (via Ollama), handling memory, emotion, and risk detection.
- **Caregiver**: Receives insights, daily guides, and risk alerts.
- **Doctor**: Views long-term trends and adjusts care plans.

## 2️⃣ TECH STACK
- **Language**: Python 3.10+
- **AI**: Ollama (Qwen2.5-3B), Sentence-Transformers (RAG), FAISS
- **Backend**: FastAPI, SQLAlchemy
- **GUI**: PySide6 (Qt)
- **Voice**: Vosk (STT), Coqui TTS (TTS)
- **DB**: SQLite (Async)

## 3️⃣ FOLDER STRUCTURE
See `elda/` directory.

## 4️⃣ SETUP
1. Install Ollama and pull `qwen2.5:3b`.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python run_elda.py`
