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

            # Verificar si el usuario tiene bloqueos propios para este día
            cur.execute(
                """
                SELECT COUNT(*) FROM squema1.horarios_bloqueados
                WHERE usuario_tel = %s
                  AND (dia_semana = %s OR dia_semana IS NULL)
                """,
                (telefono, dia_semana)
            )
            tiene_propios_hoy = cur.fetchone()[0] > 0   #type: ignore

            if tiene_propios_hoy:
                cur.execute(
                    """
                    SELECT hora_inicio, hora_fin
                    FROM squema1.horarios_bloqueados
                    WHERE usuario_tel = %s
                      AND (dia_semana = %s OR dia_semana IS NULL)
                    ORDER BY hora_inicio
                    """,
                    (telefono, dia_semana)
                )
            else:
                cur.execute(
                    """
                    SELECT hora_inicio, hora_fin
                    FROM squema1.horarios_bloqueados
                    WHERE usuario_tel IS NULL
                      AND (dia_semana = %s OR dia_semana IS NULL)
                    ORDER BY hora_inicio
                    """,
                    (dia_semana,)
                )

            bloques_blandos = [(float(ini), float(fin)) for ini, fin in cur.fetchall()]

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

    return bloques_blandos, bloques_duros
 
 
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