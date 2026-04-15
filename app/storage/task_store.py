from app.storage.database import connect_db

tasks = []

def save_task(task): 
    tasks.append(task)
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            print(f"title={task['title']}, deadline={task['deadline']}, tipo={task['tipo']}, phone={task['phone']}")
            cur.execute(
                """
                INSERT INTO squema1.tarea (nombre, deadline, tipo, usuario_tel)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (task["title"], task["deadline"], task["tipo"], task["phone"])
            )
            id_generado = cur.fetchone()[0] #type: ignore
            conn.commit()
            return id_generado
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



def get_tasks(tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nombre, deadline, tipo, usuario_tel FROM squema1.tarea WHERE usuario_tel = %s",
                (tel,)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3], "phone": r[4]}
                for r in rows
            ]
    except Exception as e:
        raise e
    finally:
        conn.close()
    
   