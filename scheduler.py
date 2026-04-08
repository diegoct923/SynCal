import schedule
import time
from datetime import datetime
from db import get_tasks
from notifier import send_whatsapp_message

def check_reminders():
    print("Chequeando tareas...")

    today = datetime.now().strftime("%d-%m")

    tasks = get_tasks()

    for task in tasks:
        if task["date"] == today:
            user = task["user"]
            title = task["title"]

            print(f"Enviando recordatorio a {user}...")

            send_whatsapp_message(user, f"📅 Hoy tenés: {title}")

def run_scheduler():
    # cada 60 segundos (para pruebas)
    schedule.every(60).seconds.do(check_reminders)

    while True:
        schedule.run_pending()
        time.sleep(1)