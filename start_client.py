import sys
import os
from PySide6.QtWidgets import QApplication

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from elda.gui.login import LoginWindow

if __name__ == "__main__":
    print("Starting ELDA Secondary Client (GUI Only)...")
    print("Note: This will not launch Backend AI or Vitals Simulation.")
    
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
