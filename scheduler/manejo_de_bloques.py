from datetime import date, timedelta
from app.storage.database import connect_db



DURACION_BASE = {
    "EXAMEN": 3.0,
    "TAREA":  1.5,
}



def cargar_bloques(telefono: str, fecha: date) -> tuple[list[tuple], list[tuple]]:
    
    dia_semana = fecha.weekday()
    conn = connect_db()
    try:
        with conn.cursor() as cur:
 
            # Bloques blandos: defaults globales (telefono IS NULL, dia_semana IS NULL)
            # más los específicos del usuario para ese día de la semana.
            cur.execute(
                """
                SELECT hora_inicio, hora_fin
                FROM squema1.horarios_bloqueados
                WHERE (usuario_tel IS NULL OR usuario_tel = %s)
                  AND (dia_semana IS NULL OR dia_semana = %s)
                ORDER BY hora_inicio
                """,
                (telefono, dia_semana)
            )
            bloques_blandos = [(float(ini), float(fin)) for ini, fin in cur.fetchall()]
 
            # Bloques duros: subtareas ya agendadas ese día (de cualquier tarea).
            cur.execute(
                """
                SELECT hora_inicio, hora_fin
                FROM squema1.subtareas
                WHERE usuario_tel = %s AND date = %s AND status != 'CANCELADA'
                ORDER BY hora_inicio
                """,
                (telefono, fecha)
            )
            bloques_duros = [(float(ini), float(fin)) for ini, fin in cur.fetchall()]
 
    finally:
        conn.close()
 
    return list(bloques_blandos), list(bloques_duros)
 
 
def merge_bloques(bloques: list[tuple]) -> list[tuple]:
    """Fusiona bloques solapados y los devuelve ordenados."""
    if not bloques:
        return []
    ordenados = sorted(bloques, key=lambda b: b[0])
    merged = [list(ordenados[0])]
    for inicio, fin in ordenados[1:]:
        if inicio <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], fin)
        else:
            merged.append([inicio, fin])
    return [tuple(b) for b in merged]