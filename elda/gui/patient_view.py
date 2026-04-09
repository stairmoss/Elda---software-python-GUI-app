import time
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit,
                               QLineEdit, QPushButton, QHBoxLayout, QFrame,
                               QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from elda.ai.elda_core import elda_ai
from elda.gui.theme import Theme


# ── AI Worker ──────────────────────────────────────────────────────────────

class AIWorker(QThread):
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, user_text: str):
        super().__init__()
        self.user_text = user_text

    def run(self):
        try:
            response = elda_ai.generate_response(self.user_text)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


# ── Voice Listener Thread ──────────────────────────────────────────────────

class ContinuousListenThread(QThread):
    text_ready = Signal(str)
    stopped = Signal()

    def __init__(self):
        super().__init__()
        self._running = False
        self.handler = None
        self.setTerminationEnabled(True)

    def run(self):
        self._running = True
        try:
            from elda.ai.voice_handler import VoiceHandler
            self.handler = VoiceHandler()
        except Exception as e:
            print(f"[Voice] Init failed: {e}")
            self._running = False
            return

        while self._running:
            try:
                if getattr(elda_ai, 'is_speaking', False):
                    time.sleep(0.4)
                    continue
                txt = self.handler.listen_once()
                if txt and txt.strip() and self._running:
                    self.text_ready.emit(txt.strip())
            except Exception as e:
                print(f"[Voice] Listen error: {e}")
                time.sleep(1)

        self.stopped.emit()

    def stop_listening(self):
        self._running = False


# ── Pulse Indicator ────────────────────────────────────────────────────────

class PulseIndicator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(64, 64)
        self.color = Theme.SECONDARY
        self._pulse_up = True
        self._apply_style()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(800)

    def _apply_style(self):
        r = self.width() // 2
        self.setStyleSheet(f"background-color: {self.color}; border-radius: {r}px; border: none;")

    def set_color(self, color: str):
        self.color = color
        self._apply_style()

    def _animate(self):
        target = 70 if self._pulse_up else 64
        self.setFixedSize(target, target)
        self._apply_style()
        self._pulse_up = not self._pulse_up


# ── Patient View ───────────────────────────────────────────────────────────

class PatientView(QWidget):
    def __init__(self):
        super().__init__()

        from elda.ai.state import app_state
        self.name = app_state.username or "Friend"
        self._processing = False
        self._ai_worker = None
        self._listen_thread = None

        self.setWindowTitle("ELDA Assistant")
        self.setGeometry(100, 80, 520, 780)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG_WHITE};
                font-family: 'Ubuntu', 'Inter', 'Arial';
            }}
            QLabel {{ color: {Theme.TEXT_DARK}; border: none; background: transparent; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        # ── Date/Time ──────────────────────────────────────────
        self._dt_lbl = QLabel()
        self._dt_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #555;")
        self._dt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._dt_lbl)
        self._dt_timer = QTimer(self)
        self._dt_timer.timeout.connect(self._tick)
        self._dt_timer.start(1000)
        self._tick()

        # ── Greeting ──────────────────────────────────────────
        greet = QLabel(f"Hello, {self.name}! 👋")
        greet.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {Theme.PRIMARY};")
        greet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(greet)

        # ── Pulse & Status ────────────────────────────────────
        pr = QHBoxLayout()
        pr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pulse = PulseIndicator()
        pr.addWidget(self.pulse)
        root.addLayout(pr)

        self.status_lbl = QLabel("🎤  Listening…")
        self.status_lbl.setStyleSheet(f"font-size: 14px; color: {Theme.SECONDARY}; font-weight: bold;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.status_lbl)

        # ── Chat Area ─────────────────────────────────────────
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.BG_LIGHT};
                border-radius: 16px;
                border: 1px solid {Theme.BORDER};
                padding: 14px;
                font-size: 16px;
                color: #000;
            }}
        """)
        root.addWidget(self.chat, stretch=1)

        # ── Input Row ─────────────────────────────────────────
        inp_row = QHBoxLayout()
        inp_row.setSpacing(8)

        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Type here or just speak…")
        self.inp.setMinimumHeight(48)
        self.inp.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 20px; border-radius: 24px;
                border: 1.5px solid {Theme.BORDER};
                background-color: #fff; color: #000; font-size: 15px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {Theme.PRIMARY}; }}
        """)
        self.inp.returnPressed.connect(self.send)
        inp_row.addWidget(self.inp)

        self.send_btn = QPushButton("↑")
        self.send_btn.setFixedSize(48, 48)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY}; color: white;
                border-radius: 24px; font-weight: bold;
                font-size: 22px; border: none;
            }}
            QPushButton:hover {{ background-color: #2980b9; }}
            QPushButton:disabled {{ background-color: #e5e5e5; color: #aaa; }}
        """)
        self.send_btn.clicked.connect(self.send)
        inp_row.addWidget(self.send_btn)
        root.addLayout(inp_row)

        # ── Action Buttons ────────────────────────────────────
        act = QHBoxLayout()
        act.setSpacing(8)

        med_btn = QPushButton("💊  Take Medication")
        med_btn.setMinimumHeight(44)
        med_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT}; color: white;
                font-weight: bold; font-size: 13px;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background-color: #d35400; }}
        """)
        med_btn.clicked.connect(self._medication_reminder)
        act.addWidget(med_btn)

        sos_btn = QPushButton("🚨  HELP / SOS")
        sos_btn.setMinimumHeight(44)
        sos_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                font-weight: bold; font-size: 16px;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        sos_btn.clicked.connect(self._sos)
        act.addWidget(sos_btn)
        root.addLayout(act)

        # ── Broadcast Poller ──────────────────────────────────
        self._bc_timer = QTimer(self)
        self._bc_timer.timeout.connect(self._poll_broadcast)
        self._bc_timer.start(3000)

        # ── Welcome + Delayed Voice Start ─────────────────────
        welcome = f"Hello, {self.name}! I am ELDA, your assistant. I am always here for you. Just speak or type naturally."
        self._add_bubble("ELDA", welcome)
        elda_ai.speak(welcome)

        # Start voice thread 3 seconds after window shows
        QTimer.singleShot(3000, self._start_voice)

    # ── Voice ─────────────────────────────────────────────────────────────

    def _start_voice(self):
        self._listen_thread = ContinuousListenThread()
        self._listen_thread.text_ready.connect(self._on_voice)
        self._listen_thread.stopped.connect(lambda: print("[Voice] Thread stopped."))
        self._listen_thread.start()

    def _on_voice(self, text: str):
        if not self._processing:
            self.inp.setText(text)
            self.send()

    # ── Broadcast Polling ──────────────────────────────────────────────────

    def _poll_broadcast(self):
        import threading
        def check():
            try:
                r = requests.get("http://127.0.0.1:8000/patient/broadcast_pending", timeout=2)
                if r.ok:
                    d = r.json()
                    if d.get("has_message") and d.get("message"):
                        msg = d["message"]
                        QTimer.singleShot(0, lambda m=msg: self._show_broadcast(m))
            except Exception:
                pass
        threading.Thread(target=check, daemon=True).start()

    def _show_broadcast(self, msg: str):
        self._add_bubble("Caregiver 💬", msg)
        elda_ai.speak(f"Message from your caregiver: {msg}")

    # ── Actions ───────────────────────────────────────────────────────────

    def _medication_reminder(self):
        self._add_bubble("System", "💊 Medication Reminder: Time to take your medicine with a glass of water.")
        elda_ai.speak("It is time to take your medication. Please take it with a glass of water.")

    def _sos(self):
        from elda.ai.state import app_state
        from elda.background.alerts import alert_manager
        app_state.patient_status = "EMERGENCY"
        app_state.latest_risk_level = "Critical"
        app_state.risk_reason = "Patient triggered manual SOS."
        alert_manager.send_alert("SOS", f"Patient {self.name} needs immediate help!")
        self._add_bubble("System", "🚨 Emergency signal sent! Help is on the way!")
        elda_ai.speak("Emergency help has been called. Please stay calm.")
        QMessageBox.warning(self, "SOS Sent", "✅ Alert sent to your caregiver!\nBreathe deeply. Help is coming.")

    def _tick(self):
        from datetime import datetime
        self._dt_lbl.setText(datetime.now().strftime("%A, %B %d  —  %I:%M %p"))

    # ── Chat Bubbles ──────────────────────────────────────────────────────

    def _add_bubble(self, sender: str, text: str):
        if sender == "ELDA":
            html = f"""<table width="100%"><tr>
                <td style="background:#eaf4fb;padding:12px 16px;border-radius:14px;
                    border:1px solid #d6eaf8;font-size:16px;color:#000;">
                    <b style="color:{Theme.PRIMARY};">ELDA:</b><br>{text}
                </td><td width="18%"></td>
            </tr></table><br>"""
        elif sender == "Caregiver 💬":
            html = f"""<table width="100%"><tr>
                <td style="background:#fff3e0;padding:12px 16px;border-radius:14px;
                    border:2px solid #f39c12;font-size:15px;color:#000;">
                    <b style="color:#e67e22;">💬 Caregiver:</b><br>{text}
                </td><td width="18%"></td>
            </tr></table><br>"""
        elif sender == "System":
            html = f"""<p style="text-align:center;color:#e74c3c;
                font-weight:bold;font-size:14px;">{text}</p><br>"""
        else:
            html = f"""<table width="100%"><tr>
                <td width="18%"></td>
                <td style="background:#e8f8e8;padding:12px 16px;border-radius:14px;
                    border:1px solid #d5f5e3;font-size:16px;color:#000;">
                    <b style="color:{Theme.SECONDARY};">You:</b><br>{text}
                </td>
            </tr></table><br>"""
        self.chat.append(html)
        self.chat.verticalScrollBar().setValue(
            self.chat.verticalScrollBar().maximum()
        )

    # ── Send ──────────────────────────────────────────────────────────────

    def send(self):
        text = self.inp.text().strip()
        if not text or self._processing:
            return
        self._processing = True
        self.inp.clear()

        self.send_btn.setDisabled(True)
        self.status_lbl.setText("🤔  Thinking…")
        self.status_lbl.setStyleSheet(f"font-size:14px;color:{Theme.ACCENT};font-weight:bold;")
        self.pulse.set_color(Theme.ACCENT)
        self._add_bubble("You", text)

        self._ai_worker = AIWorker(text)
        self._ai_worker.response_ready.connect(self._on_response)
        self._ai_worker.error_occurred.connect(self._on_ai_error)
        self._ai_worker.start()

    def _on_response(self, reply: str):
        self._add_bubble("ELDA", reply)
        elda_ai.speak(reply)
        self._done_processing()

    def _on_ai_error(self, err: str):
        self._add_bubble("ELDA", "I'm having a little trouble. Let's try again.")
        print(f"[AI] Worker error: {err}")
        self._done_processing()

    def _done_processing(self):
        self._processing = False
        self.send_btn.setDisabled(False)
        self.status_lbl.setText("🎤  Listening…")
        self.status_lbl.setStyleSheet(f"font-size:14px;color:{Theme.SECONDARY};font-weight:bold;")
        self.pulse.set_color(Theme.SECONDARY)
        self.inp.setFocus()

    # ── Cleanup ───────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # Stop all timers
        self._bc_timer.stop()
        self._dt_timer.stop()

        # Properly stop voice thread before Qt destroys it
        if self._listen_thread is not None and self._listen_thread.isRunning():
            self._listen_thread.stop_listening()
            if not self._listen_thread.wait(2000):  # wait up to 2s
                self._listen_thread.terminate()
                self._listen_thread.wait(500)

        # Stop AI worker if running
        if self._ai_worker is not None and self._ai_worker.isRunning():
            self._ai_worker.wait(1000)

        event.accept()
