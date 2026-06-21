import json
import os
from shared.storage.database import connect_db

FILE = os.getenv("USERS_FILE", "data/users.json")

def load_users():
    if not os.path.exists(FILE):
        return {}

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    os.makedirs(os.path.dirname(FILE) or ".", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user(phone):
    users = load_users()
    return users.get(phone)



def get_all_users():
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tel FROM squema1.usuario")
            return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()



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
                INSERT INTO squema1.usuario (tel) VALUES (%s) 
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



def get_minutos_anticipacion_to_notify(tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT minutos_anticipacion_notificacion FROM squema1.usuario WHERE tel = %s",
                (tel,)
            )
            row = cur.fetchone()
            return row[0] if row else 15
    finally:
        conn.close()



def set_minutos_anticipacion_to_notify(tel, minutos):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE squema1.usuario SET minutos_anticipacion_notificacion = %s WHERE tel = %s",
                (minutos, tel)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    

