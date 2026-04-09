#!/usr/bin/env python3
"""
ELDA — Empathetic Living Daily Assistant
=========================================
Main launcher. Run this file to start the full ELDA system.

Usage:
    python start.py                   # launch full app (GUI + API)
    python start.py --api-only        # launch only the FastAPI backend
"""

import sys
import os

# Ensure the root directory is always in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if "--api-only" in sys.argv:
        import uvicorn
        print("[ELDA] Starting API server only on http://0.0.0.0:8000")
        uvicorn.run("elda.api.main:app", host="0.0.0.0", port=8000, log_level="info")
    else:
        from elda.run_elda import main as run_main
        print("=" * 50)
        print("  ELDA — Empathetic Living Daily Assistant")
        print("  Version: 1.0  |  Final Prototype")
        print("=" * 50)
        run_main()


if __name__ == "__main__":
    main()
