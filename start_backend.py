import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.main import app, register_routes

if __name__ == "__main__":
    print("[ELDA] Initializing Backend...")
    
    # Register routes
    register_routes()
    
    print("[ELDA] Server starting on http://0.0.0.0:5000")
    # Using 0.0.0.0 to allow access from Flutter emulator/devices on LAN
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
