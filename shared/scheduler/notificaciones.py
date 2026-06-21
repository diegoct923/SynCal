from datetime import datetime, date, timedelta
from shared.storage.task_store import get_tasks_day, get_sessions_day
from shared.storage.user_store import get_all_users, get_minutos_anticipacion_to_notify
from shared.utils.helpers import fmt
import schedule
import time
from shared.integrations.twilio_client import send_whatsapp_message



def check_reminders():
    print("[scheduler] Chequeando recordatorios...")

    users = get_all_users()

    for tel in users:
        tareas = get_tasks_day(tel)
        sesiones = get_sessions_day(tel)

        if not tareas and not sesiones:
            continue

        msg = "📅 *Recordatorio WiCal* — tareas de hoy:\n"

        if tareas:
            msg += "\n*Tareas:*\n"
            for t in tareas:
                hora = t["deadline"].strftime("%H:%M") if t["deadline"].hour or t["deadline"].minute else "Sin hora"
                grupo = " 👥" if t["es_grupal"] else ""
                msg += f"• {t['tipo']} {t['title']} — {hora}{grupo}\n"

        if sesiones:
            msg += "\n*Sesiones de estudio:*\n"
            for s in sesiones:
                msg += f"• 📚 {s['tarea_nombre']} — {fmt(s['hora_inicio'])} a {fmt(s['hora_fin'])}\n"

        try:
            send_whatsapp_message(f"whatsapp:+{tel}", msg)
            print(f"[scheduler] Recordatorio enviado a {tel}")
        except Exception as e:
            print(f"[scheduler] Error enviando a {tel}: {e}")



def check_upcoming_reminders():

    print("[scheduler] Chequeando recordatorios puntuales...")

    now = datetime.now()
    users = get_all_users()

    for tel in users:
        minutos = get_minutos_anticipacion_to_notify(tel)
        tareas  = get_tasks_day(tel)
        sesiones = get_sessions_day(tel)

        for t in tareas:
            if not t["deadline"]:
                continue
            deadline = t["deadline"]
            if not deadline.hour and not deadline.minute:
                continue  # sin hora específica, no notificar

            diff = (deadline.replace(tzinfo=None) - now).total_seconds() / 60
            if abs(diff - minutos) <= 1:
                msg = f"⏰ En {minutos} min: {t['tipo']} *{t['title']}*"
                try:
                    send_whatsapp_message(f"whatsapp:+{tel}", msg)
                    print(f"[scheduler] Recordatorio puntual a {tel}: {t['title']}")
                except Exception as e:
                    print(f"[scheduler] Error: {e}")

        for s in sesiones:
            hora_inicio = s["hora_inicio"]
            sesion_time = now.replace(
                hour=int(hora_inicio),
                minute=int((hora_inicio % 1) * 60),
                second=0,
                microsecond=0
            )
            diff = (sesion_time - now).total_seconds() / 60
            if abs(diff - minutos) <= 1:
                msg = f"⏰ En {minutos} min: sesión 📚 *{s['tarea_nombre']}* — {fmt(s['hora_inicio'])} a {fmt(s['hora_fin'])}"
                try:
                    send_whatsapp_message(f"whatsapp:+{tel}", msg)
                    print(f"[scheduler] Recordatorio puntual a {tel}: {s['tarea_nombre']}")
                except Exception as e:
                    print(f"[scheduler] Error: {e}")



def run_scheduler():
    schedule.every().day.at("08:00").do(check_reminders)
    schedule.every(1).minutes.do(check_upcoming_reminders)

    print("[scheduler] Corriendo, esperando las 8:00...")
    while True:
        schedule.run_pending()
        time.sleep(30)