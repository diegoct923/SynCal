from .database import connect_db


def guardar_contexto(telefono, esperando): #ej: esperando = "id_tarea_completar"
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO squema1.sesion_conversacion (telefono, esperando)
                VALUES (%s, %s)
                ON CONFLICT (telefono) DO UPDATE SET esperando = %s, creado_en = NOW()
            """, (telefono, esperando, esperando))
        conn.commit()
    finally:
        conn.close()

def obtener_contexto(telefono):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT esperando FROM squema1.sesion_conversacion
                WHERE telefono = %s
            """, (telefono,))
            result = cur.fetchone()
            return result[0] if result else None
    finally:
        conn.close()

def limpiar_contexto(telefono):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM squema1.sesion_conversacion WHERE telefono = %s
            """, (telefono,))
        conn.commit()
    finally:
        conn.close()