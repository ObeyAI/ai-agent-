from app.app import create_app
from app.dialer import start_dialer_thread
import threading
import os

if __name__ == "__main__":
    # start dialer thread (daemon)
    start_dialer_thread()
    # start flask
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
