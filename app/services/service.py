from app.storage.task_store import completar_tarea, save_task, borrar_sesiones, reagendar_tarea, borrar_tarea
from scheduler.scheduler import *


def create_user_task(phone, tipo, title, date, es_grupal = False):
    task = {
        "phone": phone, 
        "title": title,
        "deadline" : date,
        "tipo" : tipo,
    }
    res = save_task(task)

    if res["status"] == "inserted" and tipo in ("EXAMEN", "TAREA") and not es_grupal:
        sesiones = planificar_tarea(res["task"]["id"])      #type: ignore
        res["sesiones"] = sesiones      #type: ignore # ← las pasamos al webhook para armar el mensaje 

    return res

   

def complete_task(task_id, usuario_tel):
    res = completar_tarea(task_id, usuario_tel) #true si completa, false si no encuentra tarea
    if not res:
        return {"status": "not_found"}

    return {"status": "completed"}



def reagendar_user_task(task_id, deadline, usuario_tel):
    # 1. Actualizar deadline en BD
    print(f"[reagendar] task_id={task_id}, deadline={deadline}")
    ok = reagendar_tarea(task_id, deadline, usuario_tel)
    if not ok:
        return {"status": "not_found"}

    # 2. Borrar sesiones viejas
    print(f"[reagendar] reagendar_tarea result: {ok}")
    borrar_sesiones(task_id)

    # 3. Replanificar con el nuevo deadline
    print(f"[reagendar] sesiones borradas")
    sesiones = planificar_tarea(task_id)

    print(f"[reagendar] sesiones nuevas: {sesiones}")
    return {"status": "reagendada", "sesiones": sesiones}



def delete_task(task_id, usuario_tel):
    res = borrar_tarea(task_id, usuario_tel)
    if not res:
        return {"status": "not_found"}
    return {"status": "deleted"}

