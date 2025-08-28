# app/services/telnyx_cc.py
import os
import time
import logging
import requests
from flask import Blueprint, request, jsonify
from app.services.memory import update_call, bump_turn, set_quality
from app.extensions import socketio

log = logging.getLogger("telnyx_cc")
telnyx_bp = Blueprint("telnyx", __name__)

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY")  # if available for verification
TELNYX_CONNECTION_ID = os.getenv("TELNYX_CONNECTION_ID")
TELNYX_API_BASE = "https://api.telnyx.com/v2"

def _telnyx_post(path: str, payload: dict):
    url = f"{TELNYX_API_BASE}{path}"
    r = requests.post(url, json=payload, auth=(TELNYX_API_KEY, ""))
    r.raise_for_status()
    return r.json()

def initiate_call(to: str, from_: str):
    payload = {
        "connection_id": TELNYX_CONNECTION_ID,
        "to": to,
        "from": from_,
        "timeout": 60
    }
    res = _telnyx_post("/calls", payload)
    call_id = res.get("data", {}).get("call_control_id") or res.get("data", {}).get("id")
    log.info("Initiated call %s -> %s (call_id=%s)", from_, to, call_id)
    update_call(call_id, status="initiated", to=to, from_=from_)
    # notify UI
    socketio.emit("call_update", {call_id: update_call(call_id)})
    return call_id

def call_action(call_id: str, action: str, payload: dict=None):
    payload = payload or {}
    path = f"/calls/{call_id}/actions/{action}"
    return _telnyx_post(path, payload)

def play_audio(call_id: str, media_url: str):
    payload = {
        "stream": False,
        "media": [
            {"type": "audio", "url": media_url}
        ]
    }
    return call_action(call_id, "play", payload)

def start_recording(call_id: str):
    return call_action(call_id, "start_recording", {"direction":"both"})

def stop_audio(call_id: str):
    return call_action(call_id, "stop", {})

def hangup(call_id: str):
    return call_action(call_id, "hangup", {})

# — webhook verification: simple optional bypass for dev
def verify_webhook(raw_body: bytes, sig_header: str) -> bool:
    if os.getenv("VERIFY_WEBHOOK", "false").lower() in ("false","0","no"):
        return True
    # more advanced Ed25519 verification can be added here
    return True

def _handle_event(event: dict):
    data = event.get("data", {})
    etype = data.get("event_type")
    payload = data.get("payload") or {}
    call_id = payload.get("call_control_id")
    to = payload.get("to") or payload.get("to_number")
    frm = payload.get("from") or payload.get("from_number")

    if etype == "call.initiated":
        update_call(call_id, status="initiated", to=to, from_=frm)
    elif etype == "call.answered":
        answered_by = payload.get("answered_by")
        if answered_by == "machine":
            update_call(call_id, status="voicemail")
            hangup(call_id)
        else:
            update_call(call_id, status="in_call")
            # play greeting if you have a greeting URL set on env
            greeting = os.getenv("GREETING_URL")
            if greeting:
                try:
                    play_audio(call_id, greeting)
                except Exception as e:
                    log.exception("Failed to play greeting: %s", e)
            # start recording
            try:
                start_recording(call_id)
            except Exception:
                log.exception("Failed to start recording")
    elif etype == "call.recording.saved":
        rec_url = payload.get("recording_urls", [None])[0]
        if rec_url:
            bump_turn(call_id)
            update_call(call_id, last_recording=rec_url)
            # emit to ui
            socketio.emit("call_update", {call_id: update_call(call_id)})
            # download asynchronously (offload ideally)
            try:
                from app.services.worker import handle_recording_download
                handle_recording_download(call_id, rec_url)
            except Exception:
                log.exception("Failed to start recording download worker")
    elif etype in ("call.hangup", "call.ended"):
        update_call(call_id, status="ended")
    # emit update
    socketio.emit("call_update", {call_id: update_call(call_id)})

@telnyx_bp.route("/webhook", methods=["POST"])
def telnyx_webhook():
    raw = request.get_data()
    sig = request.headers.get("Telnyx-Signature-Ed25519", "")
    if not verify_webhook(raw, sig):
        return jsonify({"ok": False}), 403
    event = request.json or {}
    try:
        _handle_event(event)
    except Exception:
        log.exception("Error handling webhook")
    return jsonify({"ok": True})
