# app/extensions.py
from flask_socketio import SocketIO

# Initialize SocketIO (CORS allowed for frontend/Render)
socketio = SocketIO(cors_allowed_origins="*")
