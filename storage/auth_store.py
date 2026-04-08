import json
import os

FILE = "data/pending_auth.json"

def load_auth():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save_auth(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_state(state, phone):
    data = load_auth()
    data[state] = phone
    save_auth(data)

def get_phone_from_state(state):
    data = load_auth()
    return data.get(state)

def delete_state(state):
    data = load_auth()
    if state in data:
        del data[state]
        save_auth(data)