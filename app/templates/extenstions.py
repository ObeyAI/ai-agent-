# app/extensions.py
from flask_socketio import SocketIO

# Use eventlet async mode (make sure eventlet is installed)
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
