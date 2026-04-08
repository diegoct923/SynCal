from db import save_task

def create_task(user, title, date, category):
    task = {
        "user": user,
        "title": title,
        "date": date,
        "category": category
    }

    # guardar en storage
    save_task(task)