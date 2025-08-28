# app/services/eleven.py
import os
import requests
import hashlib
from pathlib import Path

ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE = os.getenv("ELEVEN_VOICE_ID", "alloy")  # default voice id; set in env if needed

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def synthesize_text_to_file(text: str, filename_hint: str="greeting") -> str:
    """
    Synthesize text using ElevenLabs and save mp3 to media.
    Returns a relative URL path like /media/filename.mp3
    """
    if not ELEVEN_KEY:
        raise RuntimeError("ELEVEN_API_KEY missing")
    # create hash to cache voice per text
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    fname = f"{filename_hint}_{h}.mp3"
    out_path = MEDIA_DIR / fname
    if out_path.exists():
        return f"/media/{fname}"
    # ElevenLabs endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE}"
    headers = {
        "xi-api-key": ELEVEN_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.3, "similarity_boost": 0.8}
    }
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
    r.raise_for_status()
    # ElevenLabs returns audio bytes
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return f"/media/{fname}"
