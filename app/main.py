# app/app.py
from fastapi import FastAPI
from app.services import telnyx_cc, memory
import app.dialer as dialer

app = FastAPI(title="AI Dialer")

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Dialer API is running"}

@app.post("/call/start")
def start_call(number: str):
    return dialer.start_call(number)

@app.post("/call/status")
def call_status():
    return dialer.get_status()
