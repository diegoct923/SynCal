import json
import os

FILE = "data/users.json"

def load_users():
    if not os.path.exists(FILE):
        return {}

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    with open(FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user(phone):
    users = load_users()
    return users.get(phone)

def create_user_if_not_exists(phone):
    users = load_users()

    if phone not in users:
        users[phone] = {
            "notion_token": None,
            "database_id": None
        }
        save_users(users)

def update_user_token(phone, token):
    users = load_users()
    if phone not in users:
        users[phone] = {}

    users[phone]["notion_token"] = token
    save_users(users)

def has_notion_connected(phone):
    user = get_user(phone)

    return (
        user and
        user.get("notion_token") and
        user.get("database_id")
    )

def update_user_database(phone, db_id):
    users = load_users()

    if phone not in users:
        users[phone] = {}

    users[phone]["database_id"] = db_id
    save_users(users)

def get_user_token(phone):
    user = get_user(phone)
    return user.get("notion_token") if user else None


def get_user_database(phone):
    user = get_user(phone)
    return user.get("database_id") if user else None