import sys
import os

sys.path.append(os.getcwd())

print("Testing Backend Imports...")

try:
    print("1. Importing Flask App...", end="")
    from app.main import app
    print(" OK")
    
    print("2. Importing AI Agent...", end="")
    from app.ai.llm import elda_llm
    print(" OK")
    
    print("3. Importing Risk Engine...", end="")
    from app.ai.risk import risk_engine
    print(" OK")
    
    print("4. Importing Routes...", end="")
    from app.routes import index # Checking init
    print(" OK")

    print("\n✅ BACKEND INTEGRITY CHECK PASSED.")
    
except Exception as e:
    print(f"\n❌ BACKEND ERROR: {e}")
    sys.exit(1)
