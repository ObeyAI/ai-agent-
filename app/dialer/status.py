from flask import Blueprint, jsonify

status_bp = Blueprint("status", __name__)

@status_bp.route("/calls")
def calls():
    # Simulated call status API
    return jsonify([
        {"id": "c1", "status": "in-progress"},
        {"id": "c2", "status": "completed"},
    ])
