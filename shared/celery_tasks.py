import os
import socketio as socketio_client
from shared.celery_app import celery_app
from shared.scheduler.scheduler import planificar_tarea
from shared.integrations.twilio_client import send_whatsapp_message
from shared.utils.helpers import fmt

MESSAGE_QUEUE_URL = os.getenv("SOCKETIO_MESSAGE_QUEUE", "amqp://guest:guest@rabbitmq:5672//")

sio = socketio_client.KombuManager(MESSAGE_QUEUE_URL, write_only=True)


@celery_app.task
def planificar_tarea_task(task_id, phone):
    sesiones = planificar_tarea(task_id)

    if not sesiones:
        return

    msg = "Sesiones de estudio agendadas:"
    sesiones_serializadas = []

    for s in sesiones:
        sesiones_serializadas.append({
            "fecha": s["fecha"].strftime("%Y-%m-%d"),
            "tramos": s["tramos"],
            "sesion_grupo": s["sesion_grupo"]
        })

        if len(s["tramos"]) == 1:
            ini, fin = s["tramos"][0]
            msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {fmt(ini)} a {fmt(fin)}"
        else:
            tramos_str = " + ".join(f"{fmt(i)} a {fmt(f)}" for i, f in s["tramos"])
            msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {tramos_str}"

    send_whatsapp_message(phone, msg)
    sio.emit("task_updated", {"id": task_id, "sesiones": sesiones_serializadas}, room=phone)
