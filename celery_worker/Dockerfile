FROM python:3.11-slim

WORKDIR /app

COPY celery_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/

ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "shared.celery_app", "worker", "--loglevel=info"]