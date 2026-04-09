class RiskEngine:
    """
    Analyzes behavior data against the 10 Warning Signs of Alzheimer's.
    Returns a SUPPORT SCORE (not a diagnosis).
    """
    def __init__(self):
        self.risk_factors = {
            "memory_loss": 0,
            "confusion_time_place": 0,
            "trouble_images": 0,
            "mood_changes": 0
        }

    def assess(self, session_data):
        """
        Input: Dict of session events (e.g., {"confusion_count": 2, "emotion_volatility": 0.5})
        Output: JSON risk report
        """
        score = 0
        reasons = []

        if session_data.get("confusion_count", 0) > 3:
            score += 2
            reasons.append("Frequent confusion detected in last session.")
        
        if session_data.get("negative_emotion_ratio", 0) > 0.6:
            score += 1
            reasons.append("Sustained negative emotion.")

        return {
            "support_score": min(score, 10), # Max 10
            "level": "High" if score > 5 else "Medium" if score > 2 else "Low",
            "flags": reasons,
            "disclaimer": "This is an AI support tool, not a medical device. Consult a doctor."
        }

risk_engine = RiskEngine()
