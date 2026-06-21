FROM python:3.11-slim

WORKDIR /app

COPY whatsapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY whatsapp/ ./whatsapp/

ENV PYTHONUNBUFFERED=1

EXPOSE 5001

CMD ["python", "-m", "whatsapp.main"]