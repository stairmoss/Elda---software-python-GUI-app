from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt
from elda.gui.theme import Theme


class RoleCard(QFrame):
    def __init__(self, title, icon, desc, color, callback):
        super().__init__()
        self.setFixedSize(160, 190)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.callback = callback
        self.color = color
        self._normal_style = f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 14px;
                border: 1.5px solid {Theme.BORDER};
            }}
        """
        self._hover_style = f"""
            QFrame {{
                background-color: #f0f8ff;
                border-radius: 14px;
                border: 2px solid {color};
            }}
        """
        self.setStyleSheet(self._normal_style)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Colored top accent bar
        accent_bar = QFrame()
        accent_bar.setFixedHeight(4)
        accent_bar.setStyleSheet(f"background-color: {color}; border-radius: 2px; border: none;")
        layout.addWidget(accent_bar)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 36px; border: none; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_icon)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {Theme.TEXT_DARK}; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet(f"font-size: 11px; color: {Theme.MUTED}; border: none; background: transparent;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)

    def leaveEvent(self, event):
        self.setStyleSheet(self._normal_style)

    def mousePressEvent(self, event):
        self.callback()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELDA — Empathetic Living Daily Assistant")
        self.setFixedSize(700, 520)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG_LIGHT};
                font-family: 'Ubuntu', 'Inter', 'Arial';
            }}
            QLabel {{ color: {Theme.TEXT_DARK}; border: none; background: transparent; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(60, 40, 60, 30)
        root.setSpacing(0)

        # ── Hero ─────────────────────────────────────────
        title = QLabel("ELDA")
        title.setStyleSheet(f"font-size: 52px; font-weight: bold; color: {Theme.PRIMARY}; letter-spacing: 3px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Empathetic Living Daily Assistant")
        subtitle.setStyleSheet(f"font-size: 15px; color: {Theme.MUTED}; margin-bottom: 6px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {Theme.BORDER}; border: none; margin: 18px 0px;")
        root.addWidget(divider)

        # ── Username Input ────────────────────────────────
        uname_lbl = QLabel("Username  (must match on both Patient & Caregiver devices)")
        uname_lbl.setStyleSheet(f"font-size: 12px; color: {Theme.MUTED}; margin-bottom: 4px;")
        root.addWidget(uname_lbl)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g.  adarsh")
        self.username_input.setMinimumHeight(44)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 18px;
                border-radius: 22px;
                border: 1.5px solid {Theme.BORDER};
                background-color: #ffffff;
                color: #000000;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {Theme.PRIMARY}; }}
        """)
        root.addWidget(self.username_input)

        root.addSpacing(22)

        # ── Role Cards ────────────────────────────────────
        section_lbl = QLabel("Choose your role")
        section_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Theme.MUTED}; letter-spacing: 1px;")
        root.addWidget(section_lbl)

        root.addSpacing(10)

        card_row = QHBoxLayout()
        card_row.setSpacing(18)

        self.card_patient = RoleCard(
            "Patient", "🤖", "Always-on Voice Assistant", Theme.PRIMARY, self.open_patient
        )
        card_row.addWidget(self.card_patient)

        self.card_caregiver = RoleCard(
            "Caregiver", "🏥", "Live Monitoring & Alerts", Theme.SECONDARY, self.open_caregiver
        )
        card_row.addWidget(self.card_caregiver)

        self.card_doctor = RoleCard(
            "Doctor", "👨‍⚕️", "Clinical History & Analysis", "#8e44ad", self.do_doctor_login
        )
        card_row.addWidget(self.card_doctor)

        root.addLayout(card_row)
        root.addStretch()

        # ── Footer ────────────────────────────────────────
        footer_row = QHBoxLayout()
        footer_row.addStretch()
        self.settings_btn = QPushButton("⚙️  Settings")
        self.settings_btn.setFixedHeight(34)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #ecf0f1;
                border-radius: 8px;
                font-size: 13px;
                color: {Theme.TEXT_DARK};
                padding: 0px 14px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #dfe6e9; }}
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        footer_row.addWidget(self.settings_btn)
        root.addLayout(footer_row)

    def open_settings(self):
        from elda.gui.settings import SettingsWindow
        self.settings_win = SettingsWindow()
        self.settings_win.show()

    def open_patient(self):
        uname = self.username_input.text().strip() or "Guest"
        from elda.ai.state import app_state
        app_state.username = uname
        from elda.gui.patient_view import PatientView
        self.view = PatientView()
        self.view.show()
        self.close()

    def open_caregiver(self):
        uname = self.username_input.text().strip() or "Guest"
        from PySide6.QtWidgets import QInputDialog
        ip, ok = QInputDialog.getText(
            self, "Caregiver — Connect",
            "Master Node IP Address:\n(Leave blank or confirm for local)",
            text="127.0.0.1"
        )
        if not ok:
            return
        master_ip = ip.strip() or "127.0.0.1"
        from elda.gui.caregiver_dashboard import CaregiverDashboard
        self.view = CaregiverDashboard(master_ip=master_ip, username=uname)
        self.view.show()
        self.close()

    def do_doctor_login(self):
        from elda.gui.doctor_dashboard import DoctorDashboard
        self.view = DoctorDashboard()
        self.view.show()
        self.close()

    def do_login(self):
        pass
