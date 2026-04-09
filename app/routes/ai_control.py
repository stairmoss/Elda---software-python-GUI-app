from flask import Blueprint, request, jsonify
from app.ai.llm import elda_llm

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main conversational endpoint.
    Input: {"text": "User speech text", "context": {...}}
    Output: {"text": "AI Reply", "function_call": { ... } or None}
    """
    data = request.json
    user_text = data.get('text', '')
    
    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    response = elda_llm.process_input(user_text)
    return jsonify(response)
