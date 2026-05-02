from flask import request, jsonify
from app.services.service import reagendar_user_task
from app.storage.sesiones import obtener_telefono_por_state


def reagendar_tarea_route():
    data = request.get_json()
    task_id = data['task_id']
    deadline = data['deadline']
    state = data['state']

    tel = obtener_telefono_por_state(state)
    if not tel:
        return jsonify({"status": "unauthorized"}), 403

    result = reagendar_user_task(task_id, deadline, tel)
    return jsonify(result)