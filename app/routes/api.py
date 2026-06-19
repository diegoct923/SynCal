from app.events import emit_task_created, emit_task_updated, emit_task_deleted, emit_blocked_slot_created, emit_blocked_slot_deleted, emit_blocked_slot_toggled
from app.storage.database import connect_db
from app.services.service import (create_user_task, complete_task, reagendar_user_task, delete_task)
from app.storage.task_store import  actualizar_nombre_tarea, actualizar_tipo_tarea, crear_horario_bloqueado, toggle_horario_bloqueado
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
    if result["status"] == "inserted":
        emit_task_created(tel, result["task"])

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

    if result["status"] == "completed":
        emit_task_updated(tel, {"id": data["task_id"], "status": "COMPLETADA"})

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

    if result["status"] == "deleted":
        emit_task_deleted(tel, data["task_id"])

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

    if result["status"] == "reagendada":
        emit_task_updated(tel, {"id": data["task_id"], "deadline": data["deadline"]})

    return jsonify(result)



def api_update_nombre():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    result = actualizar_nombre_tarea(data["task_id"], data["title"], tel)
    
    if result:
        emit_task_updated(tel, {"id": data["task_id"], "title": data["title"]})
    
    return jsonify({"status": "updated" if result else "not_found"})


def api_update_prioridad():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    tipo = PRIORITY_TO_TIPO.get(data["priority"], "TAREA")
    result = actualizar_tipo_tarea(data["task_id"], tipo, tel)

    if result:
        emit_task_updated(tel, {"id": data["task_id"], "priority": data["priority"]})

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
                WHERE usuario_tel = %s
                ORDER BY hora_inicio
                """,
                (tel,)
            )
            propios = cur.fetchall()

            dias_con_propios = set(row[2] for row in propios)

            cur.execute(
                """
                SELECT horario_id FROM squema1.horarios_bloqueados_excluidos
                WHERE usuario_tel = %s
                """,
                (tel,)
            )
            excluidos = set(row[0] for row in cur.fetchall())

            cur.execute(
                """
                SELECT id, usuario_tel, dia_semana, hora_inicio, hora_fin, title
                FROM squema1.horarios_bloqueados
                WHERE usuario_tel IS NULL
                ORDER BY hora_inicio
                """
            )
            defaults_raw = cur.fetchall()

            defaults_activos = []
            defaults_ocultos = []

            for row in defaults_raw:
                if row[0] in excluidos:
                    defaults_ocultos.append(row)
                    continue

                if row[2] is not None:
                    if row[2] not in dias_con_propios:
                        defaults_activos.append(row)
                else:
                    for dia in range(7):
                        if dia not in dias_con_propios:
                            defaults_activos.append((row[0], row[1], dia, row[3], row[4], row[5]))

    finally:
        conn.close()

    def serialize(rows, oculto=False):
        return [
            {
                "id": row[0],
                "usuario_tel": row[1],
                "dia_semana": row[2],
                "hora_inicio": float(row[3]),
                "hora_fin": float(row[4]),
                "title": row[5],
                "oculto": oculto
            }
            for row in rows
        ]

    blocks = serialize(list(propios)) + serialize(defaults_activos) + serialize(defaults_ocultos, oculto=True)

    return jsonify(blocks)



def api_create_blocked_slot():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    hora_inicio = data["startHour"]
    hora_fin = hora_inicio + data["duration"]

    slot_id = crear_horario_bloqueado(
        tel,
        data["day"],
        hora_inicio,
        hora_fin,
        data.get("title", "Bloqueado")
    )

    slot = {
        "id": slot_id,
        "usuario_tel": tel,
        "dia_semana": data["day"],
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "title": data.get("title", "Bloqueado"),
        "oculto": False
    }
    emit_blocked_slot_created(tel, slot)

    return jsonify({"status": "created", "id": slot_id})


def api_delete_blocked_slot():
    data = request.get_json()
    tel, error = get_user_tel_from_state(data["state"])
    if error:
        return jsonify({"error": "unauthorized"}), 403

    result = toggle_horario_bloqueado(data["slot_id"], tel)

    if result["status"] == "deleted":
        emit_blocked_slot_deleted(tel, data["slot_id"])
    elif result["status"] == "toggled":
        emit_blocked_slot_toggled(tel, data["slot_id"], result["oculto"])

    return jsonify(result)