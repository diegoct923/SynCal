from flask import request, jsonify
from app.storage.task_store import borrar_tarea
from app.storage.sesiones import obtener_telefono_por_state


def borrar_tarea_route():
    data = request.get_json()
    task_id = data['task_id']
    state = data['state']

    tel = obtener_telefono_por_state(state)
    if not tel:
        return jsonify({"status": "unauthorized"}), 403

    result = borrar_tarea(task_id, tel)
    if result:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"status": "not_found"})