"""
ELDA Alert Manager — sends desktop notifications and logs alerts.
Email can be configured in settings in the future.
"""
import threading
from datetime import datetime


class AlertManager:
    def __init__(self):
        self.log_file = "email_outbox.log"

    def send_alert(self, subject: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] ALERT — {subject}: {message}"
        print(full_msg)

        # Log to file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(full_msg + "\n")
        except Exception as e:
            print(f"[Alert] Log error: {e}")

        # Desktop notification (best-effort, non-blocking)
        threading.Thread(target=self._desktop_notify, args=(subject, message), daemon=True).start()

    def _desktop_notify(self, subject: str, message: str):
        try:
            import subprocess
            subprocess.run(
                ["notify-send", f"ELDA Alert: {subject}", message, "--urgency=critical", "--expire-time=8000"],
                timeout=3, capture_output=True
            )
        except Exception:
            pass  # notify-send not available — silently skip


alert_manager = AlertManager()
