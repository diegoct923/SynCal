import os
from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

celery_app = Celery(
    "syncal",
    broker=BROKER_URL,
    include=["shared.celery_tasks"]
)
