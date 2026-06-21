from web.extensions import socketio



def emit_task_created(tel, task):
    socketio.emit("task_created", task, to=tel)



def emit_task_updated(tel, task):
    socketio.emit("task_updated", task, to=tel)



def emit_task_deleted(tel, task_id):
    socketio.emit("task_deleted", {"id": task_id}, to=tel)



def emit_group_task_created(grupo_id, task):
    socketio.emit("task_created", task, to=f"grupo_{grupo_id}")



def emit_group_task_deleted(grupo_id, task_id):
    socketio.emit("task_deleted", {"id": task_id}, to=f"grupo_{grupo_id}")



def emit_blocked_slot_created(tel, slot):
    socketio.emit("blocked_slot_created", slot, to=tel)



def emit_blocked_slot_toggled(tel, slot_id, oculto):
    socketio.emit("blocked_slot_toggled", {"id": slot_id, "oculto": oculto}, to=tel)



def emit_blocked_slot_deleted(tel, slot_id):
    socketio.emit("blocked_slot_deleted", {"id": slot_id}, to=tel)