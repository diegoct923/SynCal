from app.storage.database import connect_db
from app.services.service import (create_user_task, complete_task, reagendar_user_task, delete_task)
from app.storage.task_store import  actualizar_nombre_tarea, actualizar_tipo_tarea
from app.routes.calendar import obtener_tareas_db
from app.utils.helpers import get_user_tel_from_state
from flask import request, jsonify


PRIORITY_TO_TIPO = {
    "alta": "EXAMEN",
    "media": "TAREA",
    "baja": "PRACTICO"
}


def api_get_tasks():
    state = request.args.get("state")

    tel, error = get_user_tel_from_state(state)

    if error:
        return jsonify({"error": "unauthorized"}), 403

    tareas, sesiones = obtener_tareas_db(tel)

    return jsonify({
        "tasks": tareas,
        "sessions": sesiones
    })



def api_create_task():
    data = request.get_json()

    state = data.get("state")

    tel, error = get_user_tel_from_state(state)

    if error:
        return jsonify({"error": "unauthorized"}), 403

    tipo = PRIORITY_TO_TIPO.get(data["priority"], "TAREA")

    result = create_user_task(
        tel,
        tipo,
        data["title"],
        data["deadline"]
    )

    return jsonify(result)



def api_complete_task():
    data = request.get_json()

    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    result = complete_task(
        data["task_id"],
        tel
    )

    return jsonify(result) 



def api_delete_task():
    data = request.get_json()

    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403
    
    result = delete_task(
        data["task_id"],
        tel
    )

    return jsonify(result)



def api_reagendar_task():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    
    if error:
        return jsonify({"error": "unauthorized"}), 403

    result = reagendar_user_task(
        data["task_id"],
        data["deadline"],
        tel
    )

    return jsonify(result)



def api_update_nombre():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    result = actualizar_nombre_tarea(data["task_id"], data["title"], tel)
    return jsonify({"status": "updated" if result else "not_found"})


def api_update_prioridad():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    tipo = PRIORITY_TO_TIPO.get(data["priority"], "TAREA")
    result = actualizar_tipo_tarea(data["task_id"], tipo, tel)
    return jsonify({"status": "updated" if result else "not_found"})



def api_get_blocked_slots():
    state = request.args.get("state")

    tel, error = get_user_tel_from_state(state)
    if error:
        return jsonify({"error": "unauthorized"}), 403

    

    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, usuario_tel, dia_semana, hora_inicio, hora_fin, title
                FROM squema1.horarios_bloqueados
                WHERE usuario_tel IS NULL OR usuario_tel = %s
                ORDER BY hora_inicio
                """,
                (tel,)
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    blocks = [
        {
            "id": row[0],
            "usuario_tel": row[1],
            "dia_semana": row[2],
            "hora_inicio": float(row[3]),
            "hora_fin": float(row[4]),
            "title": row[5]
        }
        for row in rows
    ]

    return jsonify(blocks)