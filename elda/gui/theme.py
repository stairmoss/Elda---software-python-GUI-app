from PySide6.QtGui import QColor, QFont

class Theme:
    # COLOR PALETTE
    PRIMARY     = "#3498db"   # Medical Blue
    SECONDARY   = "#2ecc71"   # Calming Green
    ACCENT      = "#e67e22"   # Warm Orange
    BG_LIGHT    = "#f7f9fc"   # Off-white background
    BG_WHITE    = "#ffffff"
    TEXT_DARK   = "#2c3e50"
    TEXT_LIGHT  = "#ecf0f1"
    DANGER      = "#e74c3c"   # Alert Red
    BORDER      = "#dfe6e9"   # Neutral border
    MUTED       = "#7f8c8d"   # Muted/secondary text

    # Gradient for Login
    GRADIENT_CSS = "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fdfbfb, stop:1 #ebedee);"

    # Font — cross-platform (works on Linux, Mac, Windows)
    FONT_FAMILY = "Ubuntu, Inter, Segoe UI, Arial"

    @staticmethod
    def title_font():
        f = QFont("Ubuntu")
        f.setPointSize(18)
        f.setBold(True)
        return f

    @staticmethod
    def body_font():
        f = QFont("Ubuntu")
        f.setPointSize(10)
        return f

    # STYLESHEETS
    CARD_STYLE = f"""
        QFrame {{
            background-color: {BG_WHITE};
            border-radius: 12px;
            border: 1px solid {BORDER};
            padding: 15px;
        }}
    """

    CARD_HOVER_STYLE = f"""
        QFrame {{
            background-color: {BG_WHITE};
            border-radius: 12px;
            border: 2px solid {PRIMARY};
            padding: 15px;
        }}
    """

    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
            border: none;
        }}
        QPushButton:hover {{ background-color: #2980b9; }}
        QPushButton:pressed {{ background-color: #1a5276; }}
    """

    BUTTON_SECONDARY = f"""
        QPushButton {{
            background-color: {SECONDARY};
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
            border: none;
        }}
        QPushButton:hover {{ background-color: #27ae60; }}
    """

    BUTTON_ACCENT = f"""
        QPushButton {{
            background-color: {ACCENT};
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
            border: none;
        }}
        QPushButton:hover {{ background-color: #d35400; }}
    """

    DASHBOARD_BG = f"background-color: {BG_LIGHT};"

    # Pill input style — reusable across all screens
    PILL_INPUT = f"""
        QLineEdit {{
            padding: 10px 18px;
            border-radius: 22px;
            border: 1.5px solid {BORDER};
            background-color: {BG_WHITE};
            color: #000000;
            font-size: 14px;
        }}
        QLineEdit:focus {{ border: 1.5px solid {PRIMARY}; }}
    """
