from flask import Blueprint, request, jsonify
import time
import threading

ingest_bp = Blueprint('ingest', __name__)

# Mock storage for received data chunks
received_data = {
    "last_video_frame": None,
    "last_audio_segment": None,
    "last_heartbeat": 0
}

@ingest_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Keep-alive pulse from the Flutter app."""
    received_data["last_heartbeat"] = time.time()
    return jsonify({"status": "pulse_received", "timestamp": time.time()})

@ingest_bp.route('/video', methods=['POST'])
def upload_video():
    """Receive a video frame or clip (Base64 or binary)."""
    # In a real system, you'd decode and pass to OpenCV
    # frame = request.files['frame'] or request.json['frame']
    
    # For now, acknowledge receipt
    received_data["last_video_frame"] = time.time()
    
    # Fire-and-forget analysis (threaded)
    # threading.Thread(target=analyze_vision, args=(data,)).start()
    
    return jsonify({"status": "processed", "emotion": "neutral"}) # Mock return

@ingest_bp.route('/audio', methods=['POST'])
def upload_audio():
    """Receive audio buffer for STT."""
    # Simulates receiving audio bytes
    received_data["last_audio_segment"] = time.time()
    
    return jsonify({"status": "processed", "text": ""})  # Mock return
