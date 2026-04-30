from app.storage.database import connect_db

tasks = []

def save_task(task): 
    tasks.append(task)
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            #check overlapping
            if task["tipo"] in ("EXAMEN", "PRACTICO"):
                cur.execute(
                    """
                    SELECT id, nombre, deadline FROM squema1.tarea
                    WHERE tipo IN ('EXAMEN', 'PRACTICO') AND deadline = %s AND usuario_tel = %s
                    """,
                    (task["deadline"], task["phone"])
                )
                tarea_existente = cur.fetchall()
                if tarea_existente:
                    return {
                        "status": "overlap", 
                        "id": tarea_existente[0][0],
                        "nombre": tarea_existente[0][1],
                        "deadline": tarea_existente[0][2]
                        }


            print(f"title={task['title']}, deadline={task['deadline']}, tipo={task['tipo']}, phone={task['phone']}")
            cur.execute(
                """
                INSERT INTO squema1.tarea (nombre, deadline, tipo, usuario_tel)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (nombre, tipo, deadline, usuario_tel)
                DO NOTHING
                RETURNING id
                """,
                (task["title"].lower().strip(), task["deadline"], task["tipo"], task["phone"])
            )
            result = cur.fetchone()
            conn.commit()
            
            if result:
                return {"status": "inserted", "id": result[0]}
            else:
                return {"status": "duplicate"}
            
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
                "SELECT id, nombre, deadline, tipo, usuario_tel, status  FROM squema1.tarea WHERE usuario_tel = %s ORDER BY deadline ASC",
                (tel,)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3], "phone": r[4], "status": r[5]}
                for r in rows
            ]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        

def get_tasks_day(tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nombre, deadline, tipo, usuario_tel, status 
                FROM squema1.tarea 
                WHERE usuario_tel = %s 
                AND deadline::date = CURRENT_DATE
                ORDER BY deadline ASC
                """,
                (tel,)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3], "phone": r[4], "status": r[5]}
                for r in rows
            ]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_tasks_to_complete(tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nombre, deadline, tipo, usuario_tel, status  FROM squema1.tarea WHERE usuario_tel = %s AND status = 'PENDIENTE' ORDER BY deadline ASC",
                (tel,)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3], "phone": r[4], "status": r[5]}
                for r in rows
            ]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
   
def completar_tarea(tel, task_id):
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE squema1.tarea
                SET status = 'COMPLETADA'
                WHERE id = %s AND usuario_tel = %s
                """,
                (task_id, tel)
            )

            # check si se actualizó correctamente
            if cur.rowcount == 0:
                print("No existe esa tarea para ese usuario")
                conn.rollback()  # opcional pero prolijo
                return False

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def reagendar_tarea(task_id, deadline):
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE squema1.tarea
                SET deadline = %s
                WHERE id = %s
                """,
                (deadline, task_id)
            )

            if cur.rowcount == 0:
                print("No existe esa tarea")
                conn.rollback()
                return False

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()