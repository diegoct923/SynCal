from flask import request
from flask_socketio import join_room
from web.extensions import socketio
from shared.storage.sesiones import obtener_telefono_por_state
from shared.storage.grupo_store import get_grupos_usuario


@socketio.on("connect")
def on_connect():
    print("[socket] intento de conexión")  # ← esto
    state = request.args.get("state")
    if not state:
        return False

    tel = obtener_telefono_por_state(state)
    if not tel:
        return False

    join_room(tel)

    grupos = get_grupos_usuario(tel)
    for grupo in grupos:
        join_room(f"grupo_{grupo['id']}")

    print(f"[socket] {tel} conectado")


@socketio.on("disconnect")
def on_disconnect():
    print(f"[socket] cliente desconectado")