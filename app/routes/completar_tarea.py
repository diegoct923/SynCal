from flask import request, jsonify
from app.services.service import complete_task
from app.storage.sesiones import obtener_telefono_por_state


def completar_tarea_route():
    data = request.get_json()
    task_id = data['task_id']
    state = data['state']

    tel = obtener_telefono_por_state(state)
    if not tel:
        return jsonify({"status": "unauthorized"}), 403

    result = complete_task(task_id, tel)
    return jsonify(result)