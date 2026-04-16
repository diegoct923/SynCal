from .database import connect_db


def guardar_state(state, telefono):
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO sesiones (state, telefono)
                        VALUES (%s, %s)
                        """, (state, telefono))
            
        conn.commit()

    finally:
        conn.close()


def obtener_telefono_por_state(state):
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT telefono
                FROM sesiones
                WHERE state = %s
            """, (state,))

            result = cur.fetchone()

            if result:
                return result[0]
            else:
                return None

    finally:
        conn.close()


def limpiar_states_vencidos():
    conn = connect_db()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM sesiones
                WHERE creado_en < NOW() - INTERVAL '1 hour'
            """)
        conn.commit()

    finally:
        conn.close()