# app/main.py
import os
import telnyx
from flask import Flask, request, jsonify
from app.extensions import socketio

telnyx.api_key = os.getenv("TELNYX_API_KEY")

app = Flask(__name__)
socketio.init_app(app)

@app.route("/")
def home():
    return "✅ AI-Agent with Telnyx running!"

# 🔹 Telnyx webhook route
@app.route("/webhook/telnyx", methods=["POST"])
def telnyx_webhook():
    event = request.get_json()

    if not event or "data" not in event:
        return jsonify({"error": "Invalid event"}), 400

    event_type = event["data"]["event_type"]
    call_control_id = event["data"]["payload"].get("call_control_id")

    print(f"📞 Telnyx event: {event_type}, CallControlID: {call_control_id}")

    # Emit to dashboard via SocketIO
    socketio.emit("telnyx_event", {
        "event_type": event_type,
        "call_control_id": call_control_id,
        "raw": event
    })

    return jsonify({"status": "ok"}), 200
