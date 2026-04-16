from app.storage.task_store import save_task


def create_user_task(phone, tipo, title, date):
    task = {
        "phone": phone, 
        "title": title,
        "deadline" : date,
        "tipo" : tipo
    }
    res = save_task(task)

    return res