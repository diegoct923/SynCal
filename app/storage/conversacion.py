from .database import connect_db
import json 


def guardar_contexto(telefono, esperando, datos): #ej: esperando = "id_tarea_completar"
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO squema1.sesion_conversacion (telefono, esperando, datos)
                VALUES (%s, %s, %s)
                ON CONFLICT (telefono) DO UPDATE 
                SET esperando = %s, datos = %s, creado_en = NOW()
            """, (
                  telefono, esperando, json.dumps(datos) if datos else None,
                  esperando, json.dumps(datos) if datos else None
                 )
            )
        conn.commit()
    finally:
        conn.close()

def obtener_contexto(telefono):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT esperando, datos FROM squema1.sesion_conversacion
                WHERE telefono = %s
            """, (telefono,))
            result = cur.fetchone()
            if not result:
                return None, None
            esperando = result[0]
            datos = result[1] if result[1] else None
            return esperando, datos
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