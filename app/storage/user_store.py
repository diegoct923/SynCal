import json
import os
import uuid
from app.storage.database import connect_db

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
    es_nuevo = False
    
    if phone not in users:
        users[phone] = {
        }
        save_users(users)
        es_nuevo = True
        
        
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO usuario (tel) VALUES (%s) 
                ON CONFLICT (tel) DO NOTHING 
                RETURNING id
                """,
                (phone,)
            )
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT id FROM squema1.usuario WHERE tel = %s", (phone,))
                row = cur.fetchone()
            conn.commit()
            return {"tel" : row[0], "es_nuevo" : es_nuevo} #type: ignore
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    

