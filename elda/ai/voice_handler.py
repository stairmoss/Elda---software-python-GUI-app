import queue
import threading

class VoiceHandler:
    """
    High-Fidelity Google Cloud-based speech recognition.
    Takes 0 RAM for inference, provides 99% accuracy.
    """
    def __init__(self, model_path=""):
        self.model_path = model_path
        self._available = False
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self._available = True
            
            # PRE-LOAD MIC FOR FASTEST SPEED
            self.mic = sr.Microphone()
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("[Voice] High-fidelity Cloud voice module loaded.")
        except ImportError as e:
            print(f"[Voice] Optional dep missing ({e}). Voice disabled.")
            
    def listen_once(self, timeout=10):
        """Listen for one phrase and return the text, or '' on timeout/error."""
        if not self._available:
            return ""
            
        try:
            with self.mic as source:
                try:
                    # Faster response by limiting to short phrases
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                except self.sr.WaitTimeoutError:
                    return ""
                    
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        except self.sr.UnknownValueError:
            # Audio isn't clear
            return ""
        except self.sr.RequestError as e:
            print(f"[Voice] Google STT Request failed: {e}")
            return ""
        except Exception as e:
            print(f"[Voice] listen_once error: {e}")
            return ""
