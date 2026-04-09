from app.storage.user_store import get_user
from app.integrations.notion_client_integration import create_task


def create_user_task(user, title, date, category):
    user_data = get_user(user)

    if not user_data:
        return None

    token = user_data.get("notion_token")
    db_id = user_data.get("database_id")

    if not token or not db_id:
        return None

    return create_task(token, db_id, title, date, category)