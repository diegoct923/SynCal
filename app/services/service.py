from app.storage.task_store import completar_tarea, save_task


def create_user_task(phone, tipo, title, date):
    task = {
        "phone": phone, 
        "title": title,
        "deadline" : date,
        "tipo" : tipo
    }
    res = save_task(task)

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