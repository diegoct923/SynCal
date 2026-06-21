FROM python:3.11-slim

WORKDIR /app

COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY web/ ./web/

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "-m", "web.main"]