from app.integrations.twilio_client import send_whatsapp_message
from app.storage.database import connect_db
from app.storage.task_store import get_tasks
from datetime import datetime, date, timedelta
import schedule
import time



# ── Constantes ────────────────────────────────────────────────────────────────
 
DURACION_BASE = {
    "EXAMEN": 3.0,
    "TAREA":  1.5,
}



# ── 1. Régimen de sesiones ────────────────────────────────────────────────────
 
def calcular_regimen(fecha_registro: date, deadline: date, tipo: str) -> tuple[list[date], float]:
    
    duracion_base = DURACION_BASE.get(tipo)
    dias_restantes = (deadline - fecha_registro).days
 
    if dias_restantes > 7:
        duracion = duracion_base
        fechas = _generar_fechas(fecha_registro, deadline, paso=2)
    elif dias_restantes == 7:
        duracion = duracion_base
        fechas = _generar_fechas(fecha_registro, deadline, paso=1)
    elif 1 < dias_restantes < 7:
        duracion = duracion_base * 1.5 #type: ignore
        fechas = _generar_fechas(fecha_registro, deadline, paso=1)
    elif dias_restantes == 1:
        duracion = duracion_base * 2.5  #type: ignore
        fechas = _generar_fechas(fecha_registro, deadline, paso=1)
    else:
        duracion = duracion_base * 2.5  #type: ignore
        fechas = [fecha_registro]
    
    return fechas, duracion #type: ignore
 
 
def _generar_fechas(desde: date, hasta: date, paso: int) -> list[date]:
    fechas = []
    actual = desde
    while actual < hasta:
        fechas.append(actual)
        actual += timedelta(days=paso)
    return fechas
 
 
# ── 2. Carga de bloques desde BD ──────────────────────────────────────────────
 
def _cargar_bloques(telefono: str, fecha: date) -> tuple[list[tuple], list[tuple]]:
    
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
 
 
def _merge_bloques(bloques: list[tuple]) -> list[tuple]:
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
 
 
# ── 3. Algoritmo para partir sesiones
 
def calcular_tramos(telefono: str, fecha: date, duracion: float) -> list[tuple] | None:
    
    bloques_blandos, bloques_duros = _cargar_bloques(telefono, fecha)
 
    blandos_merged = _merge_bloques(bloques_blandos)
    duros_merged   = _merge_bloques(bloques_duros)
 
    # Línea de tiempo unificada con el tipo de cada bloque
    eventos = []
    for inicio, fin in blandos_merged:
        eventos.append((inicio, fin, 'blando'))
    for inicio, fin in duros_merged:
        eventos.append((inicio, fin, 'duro'))
    eventos.sort(key=lambda e: e[0])
 
    # ── Estado del recorrido ─────────────────────────────────────────────────
    cursor       = 0.0   # posición actual en el día
    acumulado    = 0.0   # horas de estudio acumuladas desde el último reset
    tramos       = []    # tramos de la sesión actual [(inicio, fin)]
    inicio_tramo = None  # dónde empezó el tramo libre actual
 
    def _iniciar_tramo(hora):
        nonlocal inicio_tramo
        if inicio_tramo is None:
            inicio_tramo = hora
 
    def _cerrar_tramo(hora):
        """Cierra el tramo activo y acumula las horas ganadas."""
        nonlocal inicio_tramo, acumulado
        if inicio_tramo is not None and hora > inicio_tramo:
            tramos.append((inicio_tramo, hora))
            acumulado += hora - inicio_tramo
            inicio_tramo = None
 
    def _reset(nuevo_cursor):
        """Al chocar con un bloque duro, descartamos todo y empezamos de cero."""
        nonlocal cursor, acumulado, tramos, inicio_tramo
        acumulado    = 0.0
        tramos       = []
        inicio_tramo = None
        cursor       = nuevo_cursor
 
    # ── Recorrido ────────────────────────────────────────────────────────────
    for bloque_ini, bloque_fin, tipo in eventos:
 
        if bloque_fin <= cursor:
            # Bloque ya pasado, ignorar
            continue
 
        if bloque_ini <= cursor:
            # Estamos dentro del bloque
            if tipo == 'duro':
                _reset(bloque_fin)
            else:
                # Blando: cerramos el tramo si había uno abierto y avanzamos
                _cerrar_tramo(cursor)
                cursor = bloque_fin
            continue
 
        # Hay tiempo libre entre cursor y bloque_ini
        _iniciar_tramo(cursor)
        necesitamos  = duracion - acumulado
        tiempo_libre = bloque_ini - cursor
 
        if tiempo_libre >= necesitamos:
            # Con este hueco alcanza, no necesitamos llegar al bloqueo
            tramos.append((inicio_tramo, inicio_tramo + necesitamos)) #type: ignore
            acumulado    = duracion
            inicio_tramo = None
            break
 
        # No alcanza: cerramos el hueco y procesamos el bloqueo
        _cerrar_tramo(bloque_ini)
 
        if tipo == 'duro':
            _reset(bloque_fin)
        else:
            # Blando: pausamos y seguimos acumulando desde después del bloqueo
            cursor = bloque_fin
 
    else:
        # Salimos sin break → verificar si queda tiempo al final del día
        if acumulado < duracion:
            _iniciar_tramo(cursor)
            necesitamos = duracion - acumulado
            if 24.0 - cursor >= necesitamos:
                tramos.append((inicio_tramo, inicio_tramo + necesitamos)) #type: ignore
                acumulado = duracion
 
    if acumulado < duracion:
        return None
 
    return tramos
 
 
# ── 4. Insertar tramos de una sesión ─────────────────────────────────────────
 
def _insertar_sesion(conn, tarea_id: int, telefono: str, fecha: date,
                     tramos: list[tuple], sesion_grupo: int):
    
    with conn.cursor() as cur:
        for inicio, fin in tramos:
            duracion_tramo = fin - inicio
            cur.execute(
                """
                INSERT INTO squema1.subtareas
                    (task_id, usuario_tel, date, hora_inicio, hora_fin, duracion, status, sesion_grupo)
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDIENTE', %s)
                """,
                (tarea_id, telefono, fecha, inicio, fin, duracion_tramo, sesion_grupo)
            )
 
 
# ── 5. Orquestador principal ──────────────────────────────────────────────────
 
def planificar_tarea(tarea_id: int) -> list[dict]:
    
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tipo, deadline, usuario_tel FROM squema1.tarea WHERE id = %s",
                (tarea_id,)
            )
            row = cur.fetchone()
    finally:
        conn.close()
 
    if not row:
        raise ValueError(f"No existe tarea con id={tarea_id}")
 
    tipo, deadline, telefono = row
 
    if tipo not in DURACION_BASE:
        return []
 
    if isinstance(deadline, str):
        deadline = datetime.fromisoformat(deadline).date()
    elif hasattr(deadline, "date"):
        deadline = deadline.date()
 
    fecha_registro    = date.today()
    fechas_candidatas, duracion = calcular_regimen(fecha_registro, deadline, tipo)
 
    sesiones_agendadas = []
    sesion_grupo       = 1
 
    conn = connect_db()
    try:
        for fecha in fechas_candidatas:
            tramos = calcular_tramos(telefono, fecha, duracion)
 
            if tramos is None:
                # Sin espacio ese día → buscar el día siguiente hasta el deadline
                fecha_alt = fecha + timedelta(days=1)
                while fecha_alt <= deadline:
                    tramos = calcular_tramos(telefono, fecha_alt, duracion)
                    if tramos is not None:
                        fecha = fecha_alt
                        break
                    fecha_alt += timedelta(days=1)
 
            if tramos is None:
                print(f"[scheduler] Sin hueco para sesión {sesion_grupo} de tarea {tarea_id}")
                sesion_grupo += 1
                continue
 
            _insertar_sesion(conn, tarea_id, telefono, fecha, tramos, sesion_grupo)
 
            sesiones_agendadas.append({
                "fecha":          fecha,
                "tramos":         tramos,
                "duracion_total": duracion,
                "sesion_grupo":   sesion_grupo,
            })
 
            sesion_grupo += 1
 
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
 
    return sesiones_agendadas



# ── 6. Disponibilidad grupal ──────────────────────────────────────────────────

def verificar_disponibilidad_grupo(grupo_id, fecha, hora_inicio, hora_fin):
    
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

    # Buscar siguiente hueco común en los próximos 14 días
    fecha_busqueda = fecha
    for _ in range(14):
        hueco = _buscar_hueco_comun(tels, fecha_busqueda, duracion)
        if hueco is not None:
            return {"disponible": False, "sugerencia": (fecha_busqueda, hueco)}
        fecha_busqueda += timedelta(days=1)

    return {"disponible": False, "sugerencia": None}


def _todos_disponibles(tels, fecha, hora_inicio, hora_fin):
    
    for tel in tels:
        blandos, duros = _cargar_bloques(tel, fecha)
        todos = _merge_bloques(blandos + duros)
        for ini, fin in todos:
            if ini < hora_fin and fin > hora_inicio:
                return False
    return True


def _buscar_hueco_comun(tels: list, fecha: date, duracion: float) -> float | None:
    """
    Busca el primer hueco del día donde TODOS los integrantes
    tienen al menos 'duracion' horas libres simultáneamente.
    """
    # Unir todos los bloques de todos los integrantes
    todos_los_bloques = []
    for tel in tels:
        blandos, duros = _cargar_bloques(tel, fecha)
        todos_los_bloques.extend(blandos + duros)

    bloques_merged = _merge_bloques(todos_los_bloques)

    cursor = 0.0
    for ini, fin in bloques_merged:
        if ini > cursor and ini - cursor >= duracion:
            return cursor
        cursor = max(cursor, fin)

    if 24.0 - cursor >= duracion:
        return cursor

    return None


def check_reminders():
    print("Chequeando tareas...")

    today = datetime.now().strftime("%d-%m")

    tasks = get_tasks() #type: ignore 

    for task in tasks:
        if task["date"] == today:
            user = task["user"]
            title = task["title"]

            print(f"Enviando recordatorio a {user}...")

            send_whatsapp_message(user, f"📅 Hoy tenés: {title}")

def run_scheduler():
    # cada 60 segundos (para pruebas)
    schedule.every(60).seconds.do(check_reminders)

    while True:
        schedule.run_pending()
        time.sleep(1)