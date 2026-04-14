from app.storage.user_store import get_user
from app.storage.task_store import save_task

def create_user_task(user, category, title, date):
    task = {
        "user": user, 
        "title": title,
        "date" : date,
        "category" : category
    }
    save_task(task)

    return task