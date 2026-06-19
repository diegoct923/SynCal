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


            print(f"title={task['title']}, deadline={task['deadline']}, tipo={task['tipo']}, phone={task['phone']}") #log tarea a guardar
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
                return {"status": "inserted",
                        "task": {
                            "id": result[0],
                            "title": task["title"],
                            "deadline": task["deadline"],
                            "priority": task["tipo"],
                            "isGroup": False
                        }
                    }               
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
                """
                SELECT id, nombre, deadline, tipo, usuario_tel, status, es_grupal, grupo_id
                FROM squema1.tarea
                WHERE usuario_tel = %s
                
                UNION
                
                SELECT t.id, t.nombre, t.deadline, t.tipo, t.usuario_tel, t.status, t.es_grupal, t.grupo_id
                FROM squema1.tarea t
                JOIN squema1.grupo_usuario gu ON gu.grupo_id = t.grupo_id
                WHERE gu.usuario_tel = %s AND t.es_grupal = TRUE

                ORDER BY deadline ASC
                """,
                (tel, tel)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3], 
                "phone": r[4], "status": r[5], "es_grupal": r[6], "grupo_id": r[7]}
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
                SELECT id, nombre, deadline, tipo, usuario_tel, status, es_grupal, grupo_id
                FROM squema1.tarea
                WHERE usuario_tel = %s
                AND deadline::date = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Montevideo')::date

                UNION

                SELECT t.id, t.nombre, t.deadline, t.tipo, t.usuario_tel, t.status, t.es_grupal, t.grupo_id
                FROM squema1.tarea t
                JOIN squema1.grupo_usuario gu ON gu.grupo_id = t.grupo_id
                WHERE gu.usuario_tel = %s AND t.es_grupal = TRUE
                AND t.deadline::date = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Montevideo')::date

                ORDER BY deadline ASC
                """,
                (tel, tel)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3],
                 "phone": r[4], "status": r[5], "es_grupal": r[6], "grupo_id": r[7]}
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
                """
                SELECT id, nombre, deadline, tipo, usuario_tel, status, es_grupal, grupo_id
                FROM squema1.tarea
                WHERE usuario_tel = %s AND status = 'PENDIENTE'

                UNION

                SELECT t.id, t.nombre, t.deadline, t.tipo, t.usuario_tel, t.status, t.es_grupal, t.grupo_id
                FROM squema1.tarea t
                JOIN squema1.grupo_usuario gu ON gu.grupo_id = t.grupo_id
                WHERE gu.usuario_tel = %s AND t.es_grupal = TRUE AND t.status = 'PENDIENTE'

                ORDER BY deadline ASC
                """,
                (tel, tel)
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "deadline": r[2], "tipo": r[3], 
                 "phone": r[4], "status": r[5], "es_grupal": r[6], "grupo_id": r[7]}
                for r in rows
            ]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



def get_tasks_numbered(tel):
    tasks = get_tasks_to_complete(tel)

    return [
        {
            **task,
            "numero_usuario": i
        }
        for i, task in enumerate(tasks, start=1)
    ]


def get_real_task_id_from_user_number(tel, numero_usuario):
    tasks = get_tasks_numbered(tel)

    index = int(numero_usuario) - 1

    if index < 0 or index >= len(tasks):
        return None

    return tasks[index]["id"]



def completar_tarea(task_id, usuario_tel):
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE squema1.tarea
                SET status = 'COMPLETADA'
                WHERE id = %s AND usuario_tel = %s
                """,
                (task_id, usuario_tel,)
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


def reagendar_tarea(task_id, deadline, usuario_tel):
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE squema1.tarea
                SET deadline = %s
                WHERE id = %s AND usuario_tel = %s
                """,
                (deadline, task_id, usuario_tel,)
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



def actualizar_nombre_tarea(task_id, nombre, tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE squema1.tarea
                SET nombre = %s
                WHERE id = %s AND usuario_tel = %s
                """,
                (nombre.lower().strip(), task_id, tel)
            )
            if cur.rowcount == 0:
                return False
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



def actualizar_tipo_tarea(task_id, tipo, tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE squema1.tarea
                SET tipo = %s
                WHERE id = %s AND usuario_tel = %s
                """,
                (tipo, task_id, tel)
            )
            if cur.rowcount == 0:
                return False
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



def borrar_tarea(task_id, usuario_tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM squema1.tarea 
                WHERE id = %s AND usuario_tel = %s
                """,
                (task_id, usuario_tel,)
            )

            # check si se actualizó correctamente
            if cur.rowcount == 0:
                print("No se encontró la tarea")
                conn.rollback()  
                return False

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def borrar_sesiones(task_id):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM squema1.subtareas WHERE task_id = %s",
                (task_id,)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



def get_sessions_day(tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.hora_inicio, s.hora_fin, t.nombre
                FROM squema1.subtareas s
                JOIN squema1.tarea t ON t.id = s.task_id
                WHERE s.usuario_tel = %s
                AND s.date = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Montevideo')::date
                AND s.status = 'PENDIENTE'
                ORDER BY s.hora_inicio ASC
                """,
                (tel,)
            )
            rows = cur.fetchall()
            return [
                {
                    "hora_inicio": float(r[0]),
                    "hora_fin": float(r[1]),
                    "tarea_nombre": r[2]
                }
                for r in rows
            ]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    


#horarios bloqueados
def crear_horario_bloqueado(tel, dia_semana, hora_inicio, hora_fin, title):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO squema1.horarios_bloqueados
                    (usuario_tel, dia_semana, hora_inicio, hora_fin, title)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (tel, dia_semana, hora_inicio, hora_fin, title)
            )
            result = cur.fetchone()
        conn.commit()
        return result[0]  #type: ignore
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def toggle_horario_bloqueado(slot_id, tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT usuario_tel FROM squema1.horarios_bloqueados WHERE id = %s",
                (slot_id,)
            )
            row = cur.fetchone()
            if not row:
                return {"status": "not_found"}

            es_propio = row[0] == tel

            if es_propio:
                cur.execute(
                    """
                    DELETE FROM squema1.horarios_bloqueados
                    WHERE id = %s AND usuario_tel = %s
                    """,
                    (slot_id, tel)
                )
                if cur.rowcount == 0:
                    return {"status": "not_found"}

                conn.commit()
                return {"status": "deleted"}

            else:
                cur.execute(
                    """
                    SELECT 1 FROM squema1.horarios_bloqueados_excluidos
                    WHERE usuario_tel = %s AND horario_id = %s
                    """,
                    (tel, slot_id)
                )
                ya_excluido = cur.fetchone() is not None

                if ya_excluido:
                    cur.execute(
                        """
                        DELETE FROM squema1.horarios_bloqueados_excluidos
                        WHERE usuario_tel = %s AND horario_id = %s
                        """,
                        (tel, slot_id)
                    )
                    nuevo_estado_oculto = False
                else:
                    cur.execute(
                        """
                        INSERT INTO squema1.horarios_bloqueados_excluidos (usuario_tel, horario_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (tel, slot_id)
                    )
                    nuevo_estado_oculto = True

                conn.commit()
                return {"status": "toggled", "oculto": nuevo_estado_oculto}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()