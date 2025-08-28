# app/services/telnyx_cc.py
import os
import telnyx

telnyx.api_key = os.getenv("TELNYX_API_KEY")

def place_call(number: str, caller_id: str = None):
    return telnyx.Call.create(
        connection_id=os.getenv("TELNYX_CONNECTION_ID"),
        to=number,
        from_=caller_id or os.getenv("CALLER_ID")
    )
