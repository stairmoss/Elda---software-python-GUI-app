from flask import Blueprint, jsonify, render_template

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard', methods=['GET'])
def view_dashboard():
    """
    Serves the Visual Web Dashboard (Blue/White UI).
    """
    return render_template('doctor_dashboard.html')

@doctor_bp.route('/patient/<patient_id>/overview', methods=['GET'])
def get_patient_overview(patient_id):
    """
    Returns high-level status for the doctor dashboard.
    """
    from app.utils.hardware import hardware_service
    real_data = hardware_service.get_latest()
    
    return jsonify({
        "patient_id": patient_id,
        "status": "Stable" if real_data['active'] else "Sensor Disconnected",
        "risk_score": 1, # Logic to be connected to Risk Engine too
        "last_emotion": "Calm",
        "vitals": {
            "heart_rate": real_data.get('heart_rate', '--'),
            "oxygen": real_data.get('oxygen', '--')
        },
        "alerts": []
    })

@doctor_bp.route('/patient/<patient_id>/logs/vitals', methods=['GET'])
def get_vitals_history(patient_id):
    """
    Returns filtered historical heart rate data.
    """
    import json
    import os
    
    log_file = "vitals_log.json"
    if not os.path.exists(log_file):
        return jsonify([])
        
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify([])

@doctor_bp.route('/patient/<patient_id>/logs/chat', methods=['GET'])
def get_chat_history(patient_id):
    """
    Returns conversation history from Memory.
    """
    from app.ai.llm import elda_llm
    # Use internal memory store if available
    if elda_llm.memory:
        return jsonify({"logs": elda_llm.memory.documents})
    
    # Fallback/Mock if memory not init
@doctor_bp.route('/send_report', methods=['POST'])
def trigger_report():
    """
    Manually triggers the daily email report.
    """
    from app.utils.emailer import generate_and_send_summary
    from app.utils.hardware import hardware_service
    from app.ai.risk import risk_engine
    
    # Gather Data
    hw_data = hardware_service.get_latest()
    # Mock Risk assessment for now
    risk_data = risk_engine.assess({"confusion_count": 0})
    
    # Send
    generate_and_send_summary(risk_data, hw_data)
    
    return jsonify({"status": "sent", "message": "Emails dispatched to Doctor and Caregiver."})
