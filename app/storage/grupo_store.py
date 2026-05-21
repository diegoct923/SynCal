from app.storage.database import connect_db
from app.utils.helpers import fmt
from datetime import datetime
from scheduler.scheduler import verificar_disponibilidad_grupo, DURACION_BASE


def crear_grupo(nombre, creador_tel, usernames):
    conn = connect_db()
    try:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT username FROM squema1.usuario WHERE tel = %s",
                (creador_tel,)
            )
            row = cur.fetchone()
            if not row or not row[0]:
                return {
                    "status": "error",
                    "message": "Necesitás tener un username para crear grupos. Abrí tu calendario y registrate."
                }              

            # verificar que todos los usernames existen
            cur.execute(
                "SELECT username, tel FROM squema1.usuario WHERE username = ANY(%s)",
                (usernames,)
            )
            encontrados = cur.fetchall()
            usernames_encontrados = [r[0] for r in encontrados]

            no_encontrados = [u for u in usernames if u not in usernames_encontrados]
            if no_encontrados:
                return {
                    "status": "error",
                    "message": f"No se encontraron los siguientes usuarios: {', '.join(no_encontrados)}"
                }

            # verificar que el nombre de grupo no esté tomado
            cur.execute(
                "SELECT id FROM squema1.grupo WHERE nombre = %s",
                (nombre,)
            )
            if cur.fetchone():
                return {
                    "status": "error",
                    "message": f"Ya existe un grupo con el nombre '{nombre}'."
                }

            # crear el grupo
            cur.execute(
                """
                INSERT INTO squema1.grupo (nombre, creador_tel)
                VALUES (%s, %s)
                RETURNING id
                """,
                (nombre, creador_tel)
            )
            grupo_id = cur.fetchone()[0] #type: ignore

            # agregar creador como integrante
            tels = [r[1] for r in encontrados]
            tels_integrantes = set(tels)
            tels_integrantes.add(creador_tel)

            for tel in tels_integrantes:
                cur.execute(
                    """
                    INSERT INTO squema1.grupo_usuario (grupo_id, usuario_tel)
                    VALUES (%s, %s)
                    """,
                    (grupo_id, tel)
                )

        conn.commit()
        return {
            "status": "created",
            "grupo_id": grupo_id,
            "nombre": nombre,
            "integrantes": list(tels_integrantes)
        }

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_grupos_usuario(tel):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT g.id, 
                       g.nombre, 
                       g.creador_tel,
                       ROW_NUMBER() OVER (PARTITION BY g.creador_tel ORDER BY g.id ASC) AS numero_grupo
                FROM squema1.grupo g
                JOIN squema1.grupo_usuario gu ON gu.grupo_id = g.id
                WHERE gu.usuario_tel = %s
                ORDER BY g.nombre
            """, (tel,))
            rows = cur.fetchall()
            return [{"id": r[0], "nombre": r[1]} for r in rows]
    finally:
        conn.close()
        


def save_group_task(grupo_id, tipo, title, deadline, creador_tel):

    # parsear deadline
    if isinstance(deadline, str):
        deadline_dt = datetime.fromisoformat(deadline)
    else:
        deadline_dt = deadline

    fecha       = deadline_dt.date()
    hora_inicio = deadline_dt.hour + deadline_dt.minute / 60
    duracion    = DURACION_BASE.get(tipo, 2.0)
    hora_fin    = hora_inicio + duracion

    # verificar disponibilidad de todos los integrantes
    disponibilidad = verificar_disponibilidad_grupo(grupo_id, fecha, hora_inicio, hora_fin)

    if not disponibilidad["disponible"]:
        if disponibilidad["sugerencia"]:
            fecha_sug, hora_sug = disponibilidad["sugerencia"]      #type: ignore
            return {
                "status": "no_disponible",
                "sugerencia_fecha": fecha_sug.strftime("%d/%m"),
                "sugerencia_hora": fmt(hora_sug)
            }
        else:
            return {
                "status": "no_disponible",
                "sugerencia_fecha": None,
                "sugerencia_hora": None
            }

    # insertar tarea
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO squema1.tarea (nombre, deadline, tipo, usuario_tel, grupo_id, es_grupal)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (nombre, tipo, deadline, usuario_tel)
                DO NOTHING
                RETURNING id
            """, (title.lower().strip(), deadline_dt, tipo, creador_tel, grupo_id))
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