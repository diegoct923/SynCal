from app import create_app
from app.extensions import socketio
from scheduler.scheduler import start_scheduler_thread

app = create_app()

if __name__ == "__main__":
    start_scheduler_thread()
    socketio.run(app, port=5000, allow_unsafe_werkzeug=True)