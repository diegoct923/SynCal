FROM python:3.11-slim

WORKDIR /app

COPY notifications/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY notifications/ ./notifications/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "notifications.main"]