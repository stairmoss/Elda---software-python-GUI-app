class EmotionModel:
    """
    Lightweight keyword-based emotion detector.
    Falls back to this if sentence-transformers can't load a model quickly.
    """

    EMOTION_KEYWORDS = {
        "Anxious":  ["worried", "scared", "afraid", "nervous", "panic", "anxious", "fear", "help"],
        "Sad":      ["sad", "cry", "miss", "lonely", "alone", "tired", "hurt", "pain", "unhappy"],
        "Confused": ["where", "who", "what", "lost", "don't know", "forget", "forgot", "confused"],
        "Happy":    ["happy", "good", "great", "thank", "love", "nice", "wonderful", "fine"],
        "Angry":    ["angry", "mad", "upset", "no", "stop", "leave", "hate"],
    }

    def detect_emotion(self, text: str) -> str:
        text_lower = text.lower()
        scores = {emotion: 0 for emotion in self.EMOTION_KEYWORDS}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[emotion] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "Neutral"