"""
Medication reminder scheduler using APScheduler.
"""
import threading
from datetime import datetime


class MedicationReminder(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            scheduler = BackgroundScheduler()
            # Remind at 8am, 1pm, 8pm daily
            for hour in [8, 13, 20]:
                scheduler.add_job(self._remind, 'cron', hour=hour, minute=0)
            scheduler.start()
        except Exception as e:
            print(f"[Scheduler] Could not start: {e}")

    def _remind(self):
        from elda.ai.elda_core import elda_ai
        msg = "Reminder: It's time to take your medication. Please drink a glass of water too."
        print(f"[Reminder] {datetime.now().strftime('%H:%M')} — {msg}")
        elda_ai.speak(msg)

    def trigger_now(self):
        """For manual testing from the caregiver dashboard."""
        self._remind()
