from flask import request
from flask import render_template
from app.storage.database import connect_db
from app.storage.sesiones import obtener_telefono_por_state, limpiar_states_vencidos


def obtener_tareas_db(phone):
    conn = connect_db()
    try:
        with conn.cursor() as cur:

            #tareas principales
            cur.execute("""
                SELECT t.id, t.nombre, t.deadline, t.tipo
                FROM tarea t
                JOIN usuario u ON u.tel = t.usuario_tel
                WHERE u.tel = %s
            """, (phone,))

            tareas = []
            for id, nombre, deadline, tipo in cur.fetchall():
                tareas.append({
                    "id": id,
                    "date": deadline.strftime("%Y-%m-%d"),
                    "title": nombre,
                    "priority": tipo       # EXAMEN | TAREA | PRACTICO
                })

            #subtareas / sesiones de estudio
            #traemos todos los tramos agrupados por sesion_grupo + fecha.
            #cada fila es un tramo; los que comparten sesion_grupo y tarea_id
            #son partes de la misma sesión partida.
            cur.execute("""
                SELECT
                    s.id,
                    s.tarea_id,
                    s.fecha,
                    s.hora_inicio,
                    s.hora_fin,
                    s.duracion,
                    s.sesion_grupo,
                    s.estado,
                    t.nombre AS tarea_nombre,
                    t.tipo   AS tarea_tipo
                FROM squema1.subtareas s
                JOIN squema1.tarea t ON t.id = s.tarea_id
                WHERE s.telefono = %s AND s.estado != 'CANCELADA'
                ORDER BY s.fecha, s.sesion_grupo, s.hora_inicio
            """, (phone,))

            #agrupar tramos por (tarea_id, sesion_grupo) para reconstruir
            #sesiones partidas como un solo objeto con múltiples tramos.
            sesiones_map = {}
            for row in cur.fetchall():
                id_, tarea_id, fecha, hora_ini, hora_fin, duracion, grupo, estado, nombre, tipo = row
                key = (tarea_id, grupo)

                hora_ini = float(hora_ini)
                hora_fin = float(hora_fin)

                if key not in sesiones_map:
                    sesiones_map[key] = {
                        "tarea_id":    tarea_id,
                        "tarea_nombre": nombre,
                        "tarea_tipo":  tipo,
                        "fecha":       fecha.strftime("%Y-%m-%d"),
                        "sesion_grupo": grupo,
                        "estado":      estado,
                        #el startHour y duration que usa el JS para posicionar
                        #se calculan a partir del primer y último tramo
                        "hora_inicio": hora_ini,
                        "hora_fin":    hora_fin,
                        "tramos":      []
                    }

                sesiones_map[key]["tramos"].append({
                    "id":         id_,
                    "hora_inicio": hora_ini,
                    "hora_fin":    hora_fin,
                    "duracion":    float(duracion)
                })

                #actualizar rango total de la sesión
                sesiones_map[key]["hora_inicio"] = min(sesiones_map[key]["hora_inicio"], hora_ini)
                sesiones_map[key]["hora_fin"]    = max(sesiones_map[key]["hora_fin"],    hora_fin)

            sesiones = list(sesiones_map.values())

        return tareas, sesiones

    finally:
        conn.close()


def calendar():
    limpiar_states_vencidos()
    state = request.args.get("state")
    tel = obtener_telefono_por_state(state)

    if not tel:
        return "Sesión inválida", 403

    tareas, sesiones = obtener_tareas_db(tel)
    return render_template("calendario.html", tareas=tareas, sesiones=sesiones)