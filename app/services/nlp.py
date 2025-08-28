# app/services/nlp.py
import os
import requests

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def transcribe_recording(file_path: str) -> str:
    """
    Uses OpenAI's Whisper model (v1/audio/transcriptions).
    Returns transcribed text or empty string.
    """
    if not OPENAI_KEY:
        return ""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    # whisper model 'whisper-1' is commonly used
    files = {
        "file": open(file_path, "rb")
    }
    data = {"model": "whisper-1"}
    r = requests.post(url, headers=headers, data=data, files=files, timeout=120)
    r.raise_for_status()
    resp = r.json()
    return resp.get("text", "")
