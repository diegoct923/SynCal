from app.storage.task_store import completar_tarea, save_task
from scheduler.scheduler import *


def create_user_task(phone, tipo, title, date):
    task = {
        "phone": phone, 
        "title": title,
        "deadline" : date,
        "tipo" : tipo
    }
    res = save_task(task)

    if res["status"] == "inserted" and tipo in ("EXAMEN", "TAREA"):
        sesiones = planificar_tarea(res["id"])
        res["sesiones"] = sesiones  # ← las pasamos al webhook para armar el mensaje

    return res

   

def complete_task(tel, task_id):
    res = completar_tarea(tel, task_id) #true si completa, false si no encuentra tarea
    if not res:
        res = {
            "status" : "not_found"
        }
    res={
        "status": "completed"
    }

    return res