# app/dialer/manager.py
import os
import threading
import time
import logging
from app.services.telnyx_cc import initiate_call
from app.services.memory import update_call

log = logging.getLogger("dialer.manager")
_dialer_thread = None
_lock = threading.Lock()

def dialer_loop():
    to_list = os.getenv("DIALER_TO", "")
    from_number = os.getenv("TELNYX_NUMBER", "")
    spacing = int(os.getenv("DIALER_SPACING_SEC", "3"))
    if not to_list:
        log.warning("No DIALER_TO configured - exiting")
        return
    targets = [t.strip() for t in to_list.split(",") if t.strip()]
    for t in targets:
        try:
            call_id = initiate_call(to=t, from_=from_number)
            update_call(call_id, status="dialing", to=t, from_=from_number)
        except Exception as e:
            log.exception("Failed to initiate call to %s: %s", t, e)
        time.sleep(spacing)
    log.info("Dialer loop finished")

def start_dialer_thread():
    global _dialer_thread
    with _lock:
        if _dialer_thread is None or not _dialer_thread.is_alive():
            _dialer_thread = threading.Thread(target=dialer_loop, name="dialer-thread", daemon=True)
            _dialer_thread.start()
            return True
        return False

def get_dialer_state():
    return {"running": _dialer_thread is not None and _dialer_thread.is_alive()}
