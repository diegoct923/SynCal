from datetime import date, timedelta
from app.storage.database import connect_db
from scheduler.manejo_de_bloques import cargar_bloques, merge_bloques



def verificar_disponibilidad_grupo(grupo_id: int, fecha: date, hora_inicio: float, hora_fin: float) -> dict:
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT usuario_tel FROM squema1.grupo_usuario
                WHERE grupo_id = %s
            """, (grupo_id,))
            tels = [r[0] for r in cur.fetchall()]
    finally:
        conn.close()

    duracion = hora_fin - hora_inicio

    if _todos_disponibles(tels, fecha, hora_inicio, hora_fin):
        return {"disponible": True}

    fecha_busqueda = fecha
    for _ in range(14):
        hueco = _buscar_hueco_comun(tels, fecha_busqueda, duracion)
        if hueco is not None:
            return {"disponible": False, "sugerencia": (fecha_busqueda, hueco)}
        fecha_busqueda += timedelta(days=1)

    return {"disponible": False, "sugerencia": None}


def _todos_disponibles(tels, fecha, hora_inicio, hora_fin):
    
    for tel in tels:
        blandos, duros = cargar_bloques(tel, fecha)
        todos = merge_bloques(blandos + duros)
        for ini, fin in todos:
            if ini < hora_fin and fin > hora_inicio:
                return False
    return True


def _buscar_hueco_comun(tels, fecha, duracion):
    todos_los_bloques = []
    for tel in tels:
        blandos, duros = cargar_bloques(tel, fecha)
        todos_los_bloques.extend(blandos + duros)

    bloques_merged = merge_bloques(todos_los_bloques)
    cursor = 0.0
    for ini, fin in bloques_merged:
        if ini > cursor and ini - cursor >= duracion:
            return cursor
        cursor = max(cursor, fin)

    if 24.0 - cursor >= duracion:
        return cursor
    return None