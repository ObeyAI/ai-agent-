# app/services/memory.py
import threading
from typing import Dict, Any

_lock = threading.Lock()
_calls: Dict[str, Dict[str, Any]] = {}

def get_all_calls():
    with _lock:
        return dict(_calls)

def get_call(call_id: str):
    with _lock:
        return dict(_calls.get(call_id, {}))

def update_call(call_id: str, **fields):
    with _lock:
        if call_id not in _calls:
            _calls[call_id] = {
                "status": "new",
                "to": None,
                "from": None,
                "loop": 0,
                "quality": "COLD",
                "last_recording": None
            }
        if "from_" in fields:
            fields["from"] = fields.pop("from_")
        _calls[call_id].update(fields)
        return dict(_calls[call_id])

def bump_turn(call_id: str):
    with _lock:
        _calls.setdefault(call_id, {})["loop"] = _calls.get(call_id, {}).get("loop", 0) + 1
        return _calls[call_id]["loop"]

def set_quality(call_id: str, quality: str):
    with _lock:
        _calls.setdefault(call_id, {})["quality"] = quality
