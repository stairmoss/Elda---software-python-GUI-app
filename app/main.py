from flask import Flask, jsonify
from flask_cors import CORS
import threading
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

app = Flask(__name__)
# Enable CORS for Flutter development (allow all origins for now)
CORS(app)

# Background Global State
class BackendState:
    def __init__(self):
        self.active_threads = []
        self.is_running = True

backend_state = BackendState()

@app.route('/')
def home():
    # Provide a simple landing page so the user doesn't just see raw JSON
    return """
    <html>
        <head>
            <title>ELDA Backend</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #f0f2f5; }
                .btn { display: inline-block; padding: 15px 30px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
                .btn:hover { background-color: #2980b9; }
                code { background: #333; color: #eee; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🤖 ELDA AI Backend is Online</h1>
            <p>Status: <span style="color: green; font-weight: bold;">Running</span> | Version: 2.0.0</p>
            <br>
            <a href="/api/doctor/dashboard" class="btn">🩺 Open Doctor Dashboard</a>
            <br><br>
            <p>API Endpoint: <code>/api/ingest/video</code></p>
        </body>
    </html>
    """

# Register Blueprints (Routes)
def register_routes():
    from app.routes.ingest import ingest_bp
    from app.routes.ai_control import ai_bp
    from app.routes.doctor import doctor_bp
    
    app.register_blueprint(ingest_bp, url_prefix='/api/ingest')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')

# Startup Hook
def start_background_services():
    print("[System] Starting Background AI Services...")
    # Import and start hardware thread
    from app.utils.hardware import hardware_service
    print("[System] Hardware Monitor Initialized.")

if __name__ == '__main__':
    # Initialize logic
    # register_routes() # Commented out until files exist to prevent import errors
    start_background_services()
    
    print("[System] ELDA Backend listening on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
