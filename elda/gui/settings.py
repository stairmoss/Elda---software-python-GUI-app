from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                               QCheckBox, QPushButton, QMessageBox, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt
from elda.gui.theme import Theme


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELDA — System Settings")
        self.setFixedSize(380, 320)
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
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        title = QLabel("⚙️  Configuration")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.PRIMARY};")
        root.addWidget(title)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {Theme.BORDER}; border: none;")
        root.addWidget(divider)

        # TTS Speed
        speed_lbl = QLabel("🗣️  Voice Speed")
        speed_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        root.addWidget(speed_lbl)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(100)
        self.speed_slider.setMaximum(250)
        self.speed_slider.setValue(150)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(25)
        self.speed_slider.setStyleSheet(f"accent-color: {Theme.PRIMARY};")
        root.addWidget(self.speed_slider)

        self.speed_val_lbl = QLabel("150 wpm")
        self.speed_val_lbl.setStyleSheet(f"font-size: 11px; color: {Theme.MUTED};")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_val_lbl.setText(f"{v} wpm"))
        root.addWidget(self.speed_val_lbl)

        # TTS Volume
        vol_lbl = QLabel("🔊  Voice Volume")
        vol_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        root.addWidget(vol_lbl)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setMinimum(10)
        self.vol_slider.setMaximum(100)
        self.vol_slider.setValue(90)
        self.vol_slider.setStyleSheet(f"accent-color: {Theme.PRIMARY};")
        root.addWidget(self.vol_slider)

        # Save Button
        self.save_btn = QPushButton("💾  Save Settings")
        self.save_btn.setMinimumHeight(42)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SECONDARY};
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: #27ae60; }}
        """)
        self.save_btn.clicked.connect(self.save_settings)
        root.addWidget(self.save_btn)

    def save_settings(self):
        speed = self.speed_slider.value()
        from elda.ai.state import app_state
        app_state.config["tts_rate"] = speed

        # Apply to ELDA AI TTS rate
        try:
            from elda.ai.elda_core import elda_ai
            elda_ai.tts_rate = speed
        except Exception:
            pass

        QMessageBox.information(self, "Settings Saved", "Configuration updated successfully!")
        self.close()
