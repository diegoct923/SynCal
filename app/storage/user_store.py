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
        }
        save_users(users)
