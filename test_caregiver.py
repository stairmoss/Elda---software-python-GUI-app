import sys
from PySide6.QtWidgets import QApplication
from elda.gui.caregiver_dashboard import CaregiverDashboard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        dash = CaregiverDashboard()
        print("CaregiverDashboard instantiated successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Crash:", e)
