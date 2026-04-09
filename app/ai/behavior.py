class BehaviorTracker:
    """
    Tracks routine and detects drift.
    """
    def __init__(self):
        self.routine = {
            "wake_time": "08:00",
            "lunch_time": "13:00"
        }
        self.daily_log = []

    def log_event(self, event_type, timestamp):
        self.daily_log.append({"type": event_type, "time": timestamp})

    def analyze_drift(self):
        # Mock logic
        return {
            "drift_detected": False,
            "inactivity_alert": False
        }

behavior_tracker = BehaviorTracker()
