import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

print("Testing imports...")
try:
    print("1. Importing AI Core...", end="")
    from elda.ai.elda_core import elda_ai
    print(" OK")

    print("2. Importing GUI Components...", end="")
    from elda.gui.theme import Theme
    from elda.gui.login import LoginWindow
    from elda.gui.patient_view import PatientView
    from elda.gui.caregiver_dashboard import CaregiverDashboard
    print(" OK")

    print("3. Importing Background Services...", end="")
    from elda.background.scheduler import MedicationReminder
    from elda.background.hardware import HardwareReader
    from elda.background.monitoring import MonitoringService
    print(" OK")
    
    print("4. Importing Laptop Control...", end="")
    from elda.control.agent import LaptopAgent
    print(" OK")

    print("\n✅ ALL SYSTEMS GREEN. IMPORT TEST PASSED.")
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ RUNTIME ERROR: {e}")
    sys.exit(1)
