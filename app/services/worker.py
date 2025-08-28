# app/services/worker.py
import os
import threading
import requests
import logging
from app.services.nlp import transcribe_recording
from app.services.memory import update_call, set_quality
from app.extensions import socketio

log = logging.getLogger("worker")

MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

def _download_and_transcribe(call_id: str, url: str):
    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        filename = f"{call_id}_{int(time.time())}.mp3"
        path = os.path.join(MEDIA_DIR, filename)
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        # Transcribe
        transcript = transcribe_recording(path)
        # Here we can run a simple rule-based scoring
        score = "COLD"
        if transcript and any(w in transcript.lower() for w in ("sell", "interested", "cash", "price")):
            score = "WARM"
        # Save results
        update_call(call_id, last_recording=f"/media/{filename}", transcript=transcript)
        set_quality(call_id, score)
        socketio.emit("call_update", {call_id: update_call(call_id)})
    except Exception as e:
        log.exception("download/transcribe failed: %s", e)

def handle_recording_download(call_id: str, url: str):
    t = threading.Thread(target=_download_and_transcribe, args=(call_id, url), daemon=True)
    t.start()
