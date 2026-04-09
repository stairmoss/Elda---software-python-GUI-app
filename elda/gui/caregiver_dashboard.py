"""
ELDA Caregiver Command Center
Remote monitoring, AI assistance, and patient messaging.
"""
import requests
import threading
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                               QFrame, QHBoxLayout, QPushButton, QLineEdit,
                               QListWidget, QSplitter, QTextEdit, QTimeEdit,
                               QTabWidget)
from PySide6.QtCore import QTimer, Qt, QTime, Signal, QThread
from elda.gui.theme import Theme


# ── AI Worker Thread ───────────────────────────────────────────────────────

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
            reply = resp.json().get("response", "(no response)") \
                if resp.ok else f"Server error {resp.status_code}"
        except Exception as e:
            reply = f"⚠️ Could not reach AI: {e}"
        self.result.emit(reply)


# ── Caregiver Dashboard ────────────────────────────────────────────────────

class CaregiverDashboard(QMainWindow):
    _ai_signal      = Signal(str)
    _poll_signal    = Signal(dict)
    _report_signal  = Signal(str)

    def __init__(self, master_ip: str = "127.0.0.1", username: str = "Guest"):
        super().__init__()
        self.master_ip = master_ip
        self.username  = username
        self.base_url  = f"http://{master_ip}:8000"
        self._ai_history:    list = []
        self._last_interaction: str = ""
        self._history_loaded:   bool = False
        self._ai_workers = []

        self.setWindowTitle(f"ELDA — Caregiver Command Center  ({master_ip})")
        self.resize(1280, 800)

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {Theme.BG_LIGHT};
                font-family: 'Ubuntu', 'Inter', 'Arial';
            }}
            QLabel {{ color: {Theme.TEXT_DARK}; border: none; background: transparent; }}
            QFrame {{ border: none; background: transparent; }}
            QFrame#Card {{
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid {Theme.BORDER};
            }}
            QTextEdit {{
                background-color: #ffffff;
                border: 1px solid {Theme.BORDER};
                border-radius: 10px;
                color: #1a1a2e;
                font-size: 14px;
                padding: 10px;
            }}
            QListWidget {{
                background-color: #ffffff;
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                color: #2c3e50;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 6px 10px;
                border-bottom: 1px solid #eaecee;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.PRIMARY};
                color: white;
            }}
            QTabWidget::pane {{
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                background: #ffffff;
            }}
            QTabBar::tab {{
                background: #f0f4f8; color: {Theme.TEXT_DARK};
                padding: 7px 18px; border-radius: 6px;
                margin-right: 3px; font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {Theme.PRIMARY}; color: white; font-weight: bold;
            }}
            QTimeEdit {{
                color: #000; background-color: #fff;
                border: 1px solid {Theme.BORDER};
                border-radius: 6px; padding: 4px 8px;
            }}
            QSplitter::handle {{ background-color: {Theme.BORDER}; width: 2px; }}
        """)

        # ── Central / Root ─────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        # ── Title Row ──────────────────────────────────────────
        tr = QHBoxLayout()
        tl = QLabel("🏥  ELDA Caregiver Command Center")
        tl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Theme.PRIMARY};")
        tr.addWidget(tl)
        tr.addStretch()

        self.conn_pill = QLabel(f"⬤  {master_ip}:8000")
        self.conn_pill.setStyleSheet(
            f"font-size: 12px; color: {Theme.SECONDARY}; font-weight: bold;"
            f"padding: 5px 14px; background: #eafaf1; border-radius: 12px;"
            f"border: 1px solid #a9dfbf;"
        )
        tr.addWidget(self.conn_pill)
        root.addLayout(tr)

        # ── Splitter ───────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ════ LEFT PANE ════
        left = QWidget()
        left.setMinimumWidth(400)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 10, 0)
        ll.setSpacing(10)

        # ── Setup Upload Area ───────────────────────────────────────
        self.upload_card = QFrame()
        self.upload_card.setObjectName("Card")
        sc = QVBoxLayout(self.upload_card)
        sc.setContentsMargins(16, 12, 16, 12)
        sc.setSpacing(5)

        self.up_title_lbl = QLabel("📄 Medical Repositories")
        self.up_title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Theme.TEXT_DARK};")
        sc.addWidget(self.up_title_lbl)

        self.up_desc_lbl = QLabel("Upload .txt files to automatically summarize and inform AI.")
        self.up_desc_lbl.setStyleSheet(f"font-size: 12px; color: {Theme.MUTED};")
        sc.addWidget(self.up_desc_lbl)

        self.upload_btn = QPushButton("📂 Upload Report (.txt, .md)")
        self.upload_btn.setMinimumHeight(38)
        self.upload_btn.setStyleSheet(self._btn(Theme.SECONDARY, "#27ae60"))
        self.upload_btn.clicked.connect(self.upload_report)
        sc.addWidget(self.upload_btn)

        ll.addWidget(self.upload_card)

        # ── Broadcast ─────────────────────────────────────────
        bc = QFrame()
        bc.setObjectName("Card")
        bl = QVBoxLayout(bc)
        bl.setContentsMargins(14, 10, 14, 10)
        bl.setSpacing(8)

        bc_title = QLabel("📢  Send Message to Patient")
        bc_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Theme.TEXT_DARK};")
        bl.addWidget(bc_title)

        self.broadcast_inp = QLineEdit()
        self.broadcast_inp.setPlaceholderText("Type a message to the patient terminal…")
        self.broadcast_inp.setMinimumHeight(40)
        self.broadcast_inp.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 14px; border-radius: 20px;
                border: 1.5px solid {Theme.BORDER};
                background-color: #fff; color: #000; font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {Theme.PRIMARY}; }}
        """)
        self.broadcast_inp.returnPressed.connect(self.send_broadcast_now)
        bl.addWidget(self.broadcast_inp)

        brow = QHBoxLayout()
        brow.setSpacing(8)

        self.send_now_btn = QPushButton("📢  Send Now")
        self.send_now_btn.setMinimumHeight(36)
        self.send_now_btn.setStyleSheet(self._btn(Theme.PRIMARY, "#2980b9"))
        self.send_now_btn.clicked.connect(self.send_broadcast_now)
        brow.addWidget(self.send_now_btn)

        self.schedule_time = QTimeEdit()
        self.schedule_time.setDisplayFormat("HH:mm")
        self.schedule_time.setTime(QTime.currentTime().addSecs(120))
        self.schedule_time.setFixedHeight(36)
        brow.addWidget(self.schedule_time)

        self.schedule_btn = QPushButton("⏱  Schedule")
        self.schedule_btn.setMinimumHeight(36)
        self.schedule_btn.setStyleSheet(self._btn(Theme.SECONDARY, "#27ae60"))
        self.schedule_btn.clicked.connect(self.schedule_broadcast)
        brow.addWidget(self.schedule_btn)

        bl.addLayout(brow)
        ll.addWidget(bc)

        # ── Emergency ─────────────────────────────────────────
        sos = QPushButton("🚨  TRIGGER EMERGENCY ALERT")
        sos.setMinimumHeight(44)
        sos.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                font-weight: bold; font-size: 14px;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        sos.clicked.connect(self.trigger_emergency)
        ll.addWidget(sos)

        # ── Tabs: History | Emotions ───────────────────────────
        self.tab = QTabWidget()

        chat_w = QWidget()
        cw_lay = QVBoxLayout(chat_w)
        cw_lay.setContentsMargins(4, 4, 4, 4)
        self.interaction_list = QListWidget()
        self.interaction_list.setAlternatingRowColors(True)
        cw_lay.addWidget(self.interaction_list)
        self.tab.addTab(chat_w, "💬  Interaction History")

        rep_w = QWidget()
        rw_lay = QVBoxLayout(rep_w)
        rw_lay.setContentsMargins(4, 4, 4, 4)
        
        self.report_summary_view = QTextEdit()
        self.report_summary_view.setReadOnly(True)
        self.report_summary_view.setStyleSheet("background: #fdfdfd; border-radius: 8px; border: 1px solid #ddd; font-size: 13px;")
        rw_lay.addWidget(self.report_summary_view)
        
        self.tab.addTab(rep_w, "📑  Active Medical Dossier")

        ll.addWidget(self.tab, stretch=1)
        splitter.addWidget(left)

        # ════ RIGHT PANE — AI Chat ════
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(10, 0, 0, 0)
        rl.setSpacing(10)

        ai_hdr = QLabel("✨  Caregiver AI Assistant")
        ai_hdr.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.PRIMARY};")
        rl.addWidget(ai_hdr)

        ai_sub = QLabel("Ask anything — emergencies, care tips, patient analysis, medication advice.")
        ai_sub.setStyleSheet(f"font-size: 11px; color: {Theme.MUTED};")
        rl.addWidget(ai_sub)

        self.ai_display = QTextEdit()
        self.ai_display.setReadOnly(True)
        rl.addWidget(self.ai_display, stretch=1)

        ai_row = QHBoxLayout()
        ai_row.setSpacing(8)

        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask: e.g. 'My elder fainted, what do I do?'")
        self.ai_input.setMinimumHeight(48)
        self.ai_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 20px; border-radius: 24px;
                border: 1.5px solid {Theme.BORDER};
                background-color: #fff; color: #000; font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1.5px solid #10a37f; }}
        """)
        self.ai_input.returnPressed.connect(self.ask_ai)
        ai_row.addWidget(self.ai_input)

        self.ai_btn = QPushButton("↑")
        self.ai_btn.setFixedSize(48, 48)
        self.ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f; color: white;
                border-radius: 24px; font-weight: bold;
                font-size: 22px; border: none;
            }
            QPushButton:hover { background-color: #0d8f6f; }
            QPushButton:disabled { background-color: #d5d5d5; color: #9e9e9e; border: none; }
        """)
        self.ai_btn.clicked.connect(self.ask_ai)
        ai_row.addWidget(self.ai_btn)
        rl.addLayout(ai_row)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 42)
        splitter.setStretchFactor(1, 58)
        root.addWidget(splitter)

        # ── Signals ────────────────────────────────────────────
        self._ai_signal.connect(self._on_ai_response)
        self._poll_signal.connect(self._on_poll)
        self._report_signal.connect(self._on_report_summary)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._start_poll)
        self._poll_timer.start(2500)

        self._add_ai_bubble("AI", (
            "Hello! I'm your Caregiver AI, powered by Qwen.\n\n"
            "I can help with:\n"
            "• Emergency first aid (fainting, falls, choking)\n"
            "• Alzheimer's care strategies\n"
            "• Medication and routine advice\n"
            "• Patient emotion pattern analysis\n\n"
            "Just type your question below."
        ))

    # ── Helpers ────────────────────────────────────────────────────────────

    def _btn(self, color: str, hover: str) -> str:
        return f"""
            QPushButton {{
                background-color: {color}; color: white;
                border-radius: 8px; font-size: 13px;
                font-weight: bold; border: none; padding: 0 14px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """

    # ── Broadcast ──────────────────────────────────────────────────────────

    def send_broadcast_now(self):
        msg = self.broadcast_inp.text().strip()
        if not msg:
            return
        self.broadcast_inp.clear()
        def _send():
            try:
                requests.post(f"{self.base_url}/caregiver/broadcast",
                              json={"message": msg}, timeout=5)
                QTimer.singleShot(0, lambda: self._feed_add(f"📢 You sent: {msg}"))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._feed_add(f"⚠️ Send failed: {e}"))
        threading.Thread(target=_send, daemon=True).start()

    def schedule_broadcast(self):
        msg = self.broadcast_inp.text().strip()
        if not msg:
            return
        time_str = self.schedule_time.time().toString("HH:mm")
        self.broadcast_inp.clear()
        def _sched():
            try:
                requests.post(f"{self.base_url}/caregiver/schedule_broadcast",
                              json={"message": msg, "time": time_str}, timeout=5)
                QTimer.singleShot(0, lambda: self._feed_add(f"⏱ Scheduled [{time_str}]: {msg}"))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._feed_add(f"⚠️ Schedule failed: {e}"))
        threading.Thread(target=_sched, daemon=True).start()

    def trigger_emergency(self):
        def _send():
            try:
                requests.post(f"{self.base_url}/caregiver/broadcast",
                              json={"message": "EMERGENCY: Your caregiver is on the way. Please stay calm."},
                              timeout=5)
            except Exception:
                pass
        threading.Thread(target=_send, daemon=True).start()
        self._feed_add("🚨 Emergency Alert triggered by caregiver!")

    # ── AI Chat ────────────────────────────────────────────────────────────

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

        w = AIWorker(f"{self.base_url}/caregiver/ask", q, self._ai_history[:-1])
        w.result.connect(self._ai_signal)
        w.start()
        self._ai_workers.append(w)

    def _on_ai_response(self, reply: str):
        self.ai_input.setDisabled(False)
        self.ai_btn.setDisabled(False)
        self.ai_input.setPlaceholderText("Ask: e.g. 'My elder fainted, what do I do?'")
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

    # ── Polling ────────────────────────────────────────────────────────────

    def _start_poll(self):
        def _poll():
            try:
                r = requests.get(f"{self.base_url}/caregiver/dashboard", timeout=2)
                if r.ok:
                    QTimer.singleShot(0, lambda d=r.json(): self._poll_signal.emit(d))
                    return
            except Exception:
                pass
            QTimer.singleShot(0, self._set_disconnected)

        threading.Thread(target=_poll, daemon=True).start()

    def upload_report(self):
        from PySide6.QtWidgets import QFileDialog
        import base64
        import os
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Medical Report",
            "",
            "Reports (*.txt *.md *.png *.jpg *.jpeg)"
        )
        if not file_path:
            return
            
        self.upload_btn.setDisabled(True)
        self.upload_btn.setText("⏳ Uploading & Analyzing...")
        
        def _upload_job():
            try:
                ext = os.path.splitext(file_path)[1].lower()
                payload = {}
                
                if ext in ['.txt', '.md']:
                    with open(file_path, "r", encoding="utf-8") as f:
                        payload["text"] = f.read()
                elif ext in ['.png', '.jpg', '.jpeg']:
                    with open(file_path, "rb") as f:
                        payload["image_base64"] = base64.b64encode(f.read()).decode("utf-8")
                
                # Send raw text or base64 image to backend analyzer
                r = requests.post(f"{self.base_url}/caregiver/upload_report", json=payload, timeout=60)
                if r.ok:
                    data = r.json()
                    summary = data.get("summary", "Done.")
                    self._report_signal.emit(summary)
                else:
                    self._report_signal.emit(f"Error: {r.status_code} - {r.text}")
            except Exception as e:
                self._report_signal.emit(f"Failed to upload: {str(e)}")

        threading.Thread(target=_upload_job, daemon=True).start()

    def _on_report_summary(self, summary: str):
        self.upload_btn.setDisabled(False)
        self.upload_btn.setText("📂 Upload Report (.txt, .md)")
        self.report_summary_view.setText(summary)



    def _on_poll(self, data: dict):
        # Connection pill
        self.conn_pill.setText(f"✅  {self.master_ip}:8000")
        self.conn_pill.setStyleSheet(
            f"font-size:12px;color:#1e8449;font-weight:bold;"
            f"padding:5px 14px;background:#eafaf1;border-radius:12px;border:1px solid #a9dfbf;"
        )

        srv = data.get("username", "")
        if srv and srv != self.username:
            return

        # New interaction from patient
        interaction = data.get("last_interaction", "")
        if interaction and interaction != self._last_interaction:
            self._last_interaction = interaction
            if "[Caregiver]" in interaction:
                pass   # skip echoing our own broadcast
            else:
                self._feed_add(f"💬 {interaction}")

    def _set_disconnected(self):
        self.conn_pill.setText(f"🔴  {self.master_ip}:8000  —  connecting…")
        self.conn_pill.setStyleSheet(
            "font-size:12px;color:#922b21;font-weight:bold;"
            "padding:5px 14px;background:#fdecea;border-radius:12px;border:1px solid #f5b7b1;"
        )

    def _feed_add(self, text: str):
        self.interaction_list.addItem(text)
        self.interaction_list.scrollToBottom()
