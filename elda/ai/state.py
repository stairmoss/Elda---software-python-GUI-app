class AppState:
    """Global singleton holding real-time patient state."""

    def __init__(self):
        self.username: str = ""
        self.patient_status: str = "Stable"
        self.latest_risk_level: str = "Low"
        self.latest_emotion: str = "Neutral"
        self.last_interaction: str = ""
        self.risk_reason: str = "No anomalies detected."
        self.hardware_connected: bool = False
        self.vitals: dict = {"heart_rate": 72, "oxygen": 98}
        self.config: dict = {"tts_rate": 150, "dark_mode": False}

        # Broadcast queue: caregiver → patient
        # Cleared by patient after reading
        self.pending_broadcast: str = ""


app_state = AppState()
