import sys
import threading
import uvicorn
from PySide6.QtWidgets import QApplication
from elda.gui.login import LoginWindow


def start_api():
    uvicorn.run("elda.api.main:app", host="0.0.0.0", port=8000, log_level="error")


def main():
    # ── 0. Init DB ────────────────────────────────────────────────────────
    try:
        from elda.db.init_db import init_db
        init_db()
    except Exception as e:
        print(f"[DB] Init warning: {e}")

    # ── 1. Start FastAPI (patient + caregiver API) ────────────────────────
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # ── 2. Start Medication Scheduler ────────────────────────────────────
    try:
        from elda.background.scheduler import MedicationReminder
        MedicationReminder().start()
    except Exception as e:
        print(f"[Scheduler] Could not start: {e}")

    # ── 3. Warmup — ping Ollama in background ────────────────────────────
    def warmup():
        print("[Warmup] Connecting to Ollama…")
        try:
            import ollama
            ollama.chat(
                model="qwen2.5:3b",
                messages=[{"role": "user", "content": "hi"}],
                options={"num_predict": 5}
            )
            print("[Warmup] ✅ Ollama/Qwen ready.")
        except Exception as e:
            print(f"[Warmup] Ollama ping failed: {e}")

        print("[Warmup] Loading memory model…")
        try:
            from elda.ai.elda_core import elda_ai
            elda_ai._ensure_memory()
            print("[Warmup] ✅ Memory ready.")
        except Exception as e:
            print(f"[Warmup] Memory error: {e}")

    threading.Thread(target=warmup, daemon=True).start()

    # ── 4. Launch Qt GUI ──────────────────────────────────────────────────
    app = QApplication(sys.argv)
    app.setApplicationName("ELDA")
    app.setOrganizationName("ELDA Healthcare")

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
