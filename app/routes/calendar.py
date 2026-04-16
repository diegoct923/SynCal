from flask import request
from flask import render_template
from app.storage.database import connect_db
from app.storage.sesiones import obtener_telefono_por_state, limpiar_states_vencidos


def obtener_tareas_db(phone):
    
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.nombre, t.deadline, t.tipo
                FROM tarea t
                JOIN usuario u ON u.tel = t.usuario_tel
                WHERE u.tel = %s
            """, (phone,))

            filas = cur.fetchall()

            tareas = []
            for nombre, deadline, tipo in filas:
                tareas.append({
                    "date": deadline.strftime("%Y-%m-%d"),
                    "title": nombre,
                    "priority": tipo
                })
            return tareas
        
    finally:
        conn.close()


def calendar():
    limpiar_states_vencidos()
    state = request.args.get("state")
    tel = obtener_telefono_por_state(state)

    if not tel:
        return "Sesión inválida", 403

    tareas = obtener_tareas_db(tel)
    return render_template("calendario.html", tareas=tareas)