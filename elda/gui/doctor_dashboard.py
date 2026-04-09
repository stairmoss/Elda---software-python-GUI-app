import threading
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit,
                               QPushButton, QHBoxLayout, QMessageBox,
                               QDialog, QPlainTextEdit, QFrame, QSplitter,
                               QScrollArea, QLineEdit)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from elda.gui.theme import Theme

class AIWorker(QThread):
    result = Signal(str)
    def __init__(self, url: str, question: str, history: list):
        super().__init__()
        self.url = url
        self.question = question
        self.history = history

    def run(self):
        try:
            resp = requests.post(
                self.url,
                json={"question": self.question, "history": self.history},
                timeout=300
            )
            reply = resp.json().get("reply", "(no response)") if resp.ok else f"Server error {resp.status_code}"
        except Exception as e:
            reply = f"⚠️ Could not reach AI: {e}"
        self.result.emit(reply)


class DoctorDashboard(QWidget):
    _ai_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELDA — Doctor Clinical Portal")
        self.setGeometry(80, 80, 900, 680)
        self.base_url = "http://localhost:8000"
        self._ai_history = []
        self._ai_workers = []

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG_LIGHT};
                font-family: 'Ubuntu', 'Inter', 'Arial';
            }}
            QLabel {{
                color: {Theme.TEXT_DARK};
                border: none;
                background: transparent;
            }}
            QTextEdit {{
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid {Theme.BORDER};
                padding: 12px;
                color: #1a1a2e;
                font-size: 13px;
            }}
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        # ── Header ───────────────────────────────────────────
        header_row = QHBoxLayout()

        title_lbl = QLabel("🩺  Clinical Review Portal")
        title_lbl.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {Theme.PRIMARY};")
        header_row.addWidget(title_lbl)
        header_row.addStretch()

        self.live_emotion_lbl = QLabel("Emotion: —")
        self.live_emotion_lbl.setStyleSheet(f"font-size: 13px; color: {Theme.ACCENT}; font-weight: bold; "
                                            f"padding: 6px 14px; background-color: #fff3e0; "
                                            f"border-radius: 12px; border: 1px solid #ffd180;")
        header_row.addWidget(self.live_emotion_lbl)

        self.live_risk_lbl = QLabel("Risk: —")
        self.live_risk_lbl.setStyleSheet(f"font-size: 13px; color: {Theme.SECONDARY}; font-weight: bold; "
                                         f"padding: 6px 14px; background-color: #e8f8f5; "
                                         f"border-radius: 12px; border: 1px solid #a9dfbf;")
        header_row.addWidget(self.live_risk_lbl)

        root_layout.addLayout(header_row)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background-color: {Theme.BORDER}; border: none;")
        root_layout.addWidget(div)

        # ── Main Splitter ─────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        # LEFT — Interaction History
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        hist_lbl = QLabel("📋  Patient Interaction History")
        hist_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Theme.TEXT_DARK};")
        left_layout.addWidget(hist_lbl)

        self.report_area = QTextEdit()
        self.report_area.setReadOnly(True)
        self.report_area.setPlaceholderText("Click 'Refresh' to load interaction history...")
        left_layout.addWidget(self.report_area, stretch=1)

        # Buttons
        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(8)

        self.refresh_btn = QPushButton("🔃  Refresh Data")
        self.refresh_btn.setMinimumHeight(38)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SECONDARY};
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                padding: 0 14px;
            }}
            QPushButton:hover {{ background-color: #27ae60; }}
        """)
        self.refresh_btn.clicked.connect(self.load_data)
        btn_row1.addWidget(self.refresh_btn)

        self.dossier_btn = QPushButton("📄  View Active Dossier")
        self.dossier_btn.setMinimumHeight(38)
        self.dossier_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #8e44ad;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                padding: 0 14px;
            }}
            QPushButton:hover {{ background-color: #9b59b6; }}
        """)
        self.dossier_btn.clicked.connect(self.view_dossier)
        btn_row1.addWidget(self.dossier_btn)

        left_layout.addLayout(btn_row1)

        # Emotion Bar Chart (moved to left layout)
        graph_lbl = QLabel("📊  Emotion Frequency (All Sessions)")
        graph_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Theme.TEXT_DARK};")
        left_layout.addWidget(graph_lbl)

        from elda.gui.widgets.static_graph import StaticGraph
        self.emotion_graph = StaticGraph(title="Emotion Distribution", y_label="Episodes", color="#8e44ad")
        self.emotion_graph.setMinimumHeight(180)
        left_layout.addWidget(self.emotion_graph)

        splitter.addWidget(left_widget)

        # RIGHT — AI Chat
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(10)

        ai_lbl = QLabel("🤖  Clinical AI Assistant")
        ai_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Theme.TEXT_DARK};")
        right_layout.addWidget(ai_lbl)

        self.ai_display = QTextEdit()
        self.ai_display.setReadOnly(True)
        self.ai_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: #ffffff; border-radius: 10px;
                border: 1px solid {Theme.BORDER}; padding: 12px;
            }}
        """)
        right_layout.addWidget(self.ai_display, stretch=1)

        ai_row = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask a clinical query regarding the patient...")
        self.ai_input.setMinimumHeight(48)
        self.ai_input.setStyleSheet(f"font-size: 14px; padding: 0 16px; border-radius: 24px; border: 1.5px solid {Theme.BORDER}; background-color: #ffffff; color: #000000;")
        self.ai_input.returnPressed.connect(self.ask_ai)
        ai_row.addWidget(self.ai_input)

        self.ai_btn = QPushButton("➤")
        self.ai_btn.setFixedSize(48, 48)
        self.ai_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY}; color: white;
                border-radius: 24px; font-weight: bold;
                font-size: 22px; border: none;
            }}
            QPushButton:hover {{ background-color: #0d8f6f; }}
            QPushButton:disabled {{ background-color: #d5d5d5; color: #9e9e9e; border: none; }}
        """)
        self.ai_btn.clicked.connect(self.ask_ai)
        ai_row.addWidget(self.ai_btn)
        right_layout.addLayout(ai_row)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        self._ai_signal.connect(self._on_ai_response)
        self._add_ai_bubble("AI", "Hello Doctor. I am your Clinical AI Assistant.<br><br>I have full access to the patient's interaction history and their active medical dossier.<br>How may I assist you?")

        root_layout.addWidget(splitter)

        # Auto-update timer for live labels
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._update_live_labels)
        self.refresh_timer.start(3000)

        self.load_data()

    def _update_live_labels(self):
        from elda.ai.state import app_state
        emotion = app_state.latest_emotion or "Neutral"
        risk = app_state.latest_risk_level or "Low"
        self.live_emotion_lbl.setText(f"Emotion: {emotion}")
        color_map = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#27ae60", "Critical": "#8e44ad"}
        risk_color = color_map.get(risk, "#27ae60")
        self.live_risk_lbl.setText(f"Risk: {risk}")
        self.live_risk_lbl.setStyleSheet(
            f"font-size: 13px; color: white; font-weight: bold; "
            f"padding: 6px 14px; background-color: {risk_color}; "
            f"border-radius: 12px; border: none;"
        )

    def ask_ai(self):
        q = self.ai_input.text().strip()
        if not q:
            return
        self.ai_input.clear()
        self.ai_input.setDisabled(True)
        self.ai_btn.setDisabled(True)
        self.ai_input.setPlaceholderText("AI is thinking…")
        self._add_ai_bubble("You", q)
        self._ai_history.append({"role": "user", "content": q})

        w = AIWorker(f"{self.base_url}/doctor/ask", q, self._ai_history[:-1])
        w.result.connect(self._ai_signal)
        w.start()
        self._ai_workers.append(w)

    def _on_ai_response(self, reply: str):
        self.ai_input.setDisabled(False)
        self.ai_btn.setDisabled(False)
        self.ai_input.setPlaceholderText("Ask a clinical query regarding the patient...")
        self.ai_input.setFocus()
        self._ai_history.append({"role": "assistant", "content": reply})
        if len(self._ai_history) > 20:
            self._ai_history = self._ai_history[-20:]
        self._add_ai_bubble("AI", reply)

    def _add_ai_bubble(self, sender: str, text: str):
        import markdown
        try:
            html_text = markdown.markdown(text, extensions=['nl2br'])
            html_text = html_text.replace("<p>", "<p style='color:#000000; margin-bottom:6px;'>")
            html_text = html_text.replace("<ul>", "<ul style='color:#000000; margin-bottom:6px;'>")
            html_text = html_text.replace("<ol>", "<ol style='color:#000000; margin-bottom:6px;'>")
            html_text = html_text.replace("<li>", "<li style='color:#000000; margin-bottom:4px;'>")
            html_text = html_text.replace("<strong>", "<strong style='color:#000000;'>")
        except Exception:
            html_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        if sender == "You":
            html = f"""<table width="100%"><tr>
                <td width="15%"></td>
                <td style="background:#e5e5ea;padding:12px 16px;border-radius:14px;border:1px solid #d1d5db;">
                    <p style="margin:0;color:#000;font-size:14px;">{html_text}</p>
                </td></tr></table><br>"""
        else:
            html = f"""<table width="100%"><tr>
                <td style="background:#f0fff8;padding:14px 16px;border-radius:14px;border:1.5px solid #a9dfbf;">
                    <div style="margin:0;color:#000;font-size:14px;">
                        <b style="color:#10a37f;">✨ AI:</b><br><br>{html_text}
                    </div>
                </td><td width="5%"></td></tr></table><br>"""
        self.ai_display.append(html)
        self.ai_display.verticalScrollBar().setValue(
            self.ai_display.verticalScrollBar().maximum()
        )

    def load_data(self):
        self.report_area.clear()
        from elda.db.session import get_session
        from elda.db.models import Interaction
        session = get_session()
        try:
            interactions = session.query(Interaction).order_by(Interaction.id.desc()).limit(100).all()
            if not interactions:
                self.report_area.setText("No history found in Database.\nStart a patient session to populate interaction logs.")
                return

            report = ""
            emotion_counts = {'Happy': 0, 'Sad': 0, 'Anxious': 0, 'Confused': 0, 'Neutral': 0, 'Angry': 0}

            for interact in interactions:
                ts = interact.timestamp.strftime("%Y-%m-%d %H:%M") if interact.timestamp else "?"
                sender = getattr(interact, 'sender', 'Patient') or 'Patient'
                emotion_tag = getattr(interact, 'emotion', 'Neutral') or 'Neutral'
                report += f"[{ts}] {sender} ({emotion_tag}):\n  {interact.content}\n"
                if interact.response_content:
                    report += f"  ELDA: {interact.response_content}\n"
                report += "─" * 44 + "\n"

                emo = emotion_tag
                if emo in emotion_counts:
                    emotion_counts[emo] += 1
                else:
                    emotion_counts[emo] = 1

            self.report_area.setPlainText(report)

            # Filter out zero-count emotions for cleaner graph
            filtered = {k: v for k, v in emotion_counts.items() if v > 0}
            if filtered:
                self.emotion_graph.plot_bar(filtered)

        except Exception as e:
            self.report_area.setText(f"Error loading DB records: {e}")
        finally:
            session.close()

    def view_dossier(self):
        import os
        summary_path = os.path.join(os.path.dirname(__file__), "..", "data", "active_patient_summary.md")
        text = "No Medical Dossier found.\nPlease upload a report from the Caregiver Dashboard."
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding="utf-8") as f:
                text = f.read()

        try:
            dlg = QDialog(self)
            dlg.setWindowTitle("Active Medical Dossier")
            dlg.resize(600, 600)
            dlg.setStyleSheet(f"background-color: {Theme.BG_LIGHT};")
            dlg_layout = QVBoxLayout(dlg)
            txt = QTextEdit(text)
            txt.setReadOnly(True)
            txt.setStyleSheet(f"font-size: 14px; background-color: #ffffff; color: #1a1a2e; border: 1px solid {Theme.BORDER}; padding: 12px; border-radius: 8px;")
            dlg_layout.addWidget(txt)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load dossier: {e}")
