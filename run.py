# run.py
from app.main import app
from app.extensions import socketio

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
