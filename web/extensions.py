import os
from flask_socketio import SocketIO

MESSAGE_QUEUE_URL = os.getenv("SOCKETIO_MESSAGE_QUEUE", "amqp://guest:guest@rabbitmq:5672//")

socketio = SocketIO(message_queue=MESSAGE_QUEUE_URL, async_mode="threading")
