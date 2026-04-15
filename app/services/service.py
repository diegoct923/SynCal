from app.storage.task_store import save_task


def create_user_task(phone, tipo, title, date):
    task = {
        "phone": phone, 
        "title": title,
        "date" : date,
        "tipo" : tipo
    }
    save_task(task)

    return task