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
    """
    Devuelve (fechas_candidatas, duracion_por_sesion).
    La duración es el total de horas de estudio por sesión,
    que puede estar distribuida en varios tramos si hay bloques de rutina en el medio.
    """
    duracion_base = DURACION_BASE.get(tipo)
    dias_restantes = (deadline - fecha_registro).days
 
    if dias_restantes > 7:
        duracion = duracion_base
        fechas = _generar_fechas(fecha_registro, deadline, paso=2)
    elif dias_restantes == 7:
        duracion = duracion_base
        fechas = _generar_fechas(fecha_registro, deadline, paso=1)
    elif 1 < dias_restantes < 7:
        duracion = duracion_base * 1.5
        fechas = _generar_fechas(fecha_registro, deadline, paso=1)
    elif dias_restantes == 1:
        duracion = duracion_base * 2.5
        fechas = _generar_fechas(fecha_registro, deadline, paso=1)
    else:
        duracion = duracion_base * 2.5
        fechas = [fecha_registro]
 
    return fechas, duracion
 
 
def _generar_fechas(desde: date, hasta: date, paso: int) -> list[date]:
    fechas = []
    actual = desde
    while actual < hasta:
        fechas.append(actual)
        actual += timedelta(days=paso)
    return fechas
 
 
# ── 2. Carga de bloques desde BD ──────────────────────────────────────────────
 
def _cargar_bloques(telefono: str, fecha: date) -> tuple[list[tuple], list[tuple]]:
    """
    Devuelve (bloques_blandos, bloques_duros) para ese usuario y fecha.
 
    bloques_blandos: horarios_bloqueados (rutina del usuario).
                      La sesión PUEDE partirse alrededor de estos.
 
    bloques_duros: subtareas ya agendadas.
                      La sesión NO puede partirse, hay que buscar otro hueco.
    """
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
                WHERE (telefono IS NULL OR telefono = %s)
                  AND (dia_semana IS NULL OR dia_semana = %s)
                ORDER BY hora_inicio
                """,
                (telefono, dia_semana)
            )
            bloques_blandos = cur.fetchall()
 
            # Bloques duros: subtareas ya agendadas ese día (de cualquier tarea).
            cur.execute(
                """
                SELECT hora_inicio, hora_fin
                FROM squema1.subtareas
                WHERE telefono = %s AND fecha = %s AND estado != 'CANCELADA'
                ORDER BY hora_inicio
                """,
                (telefono, fecha)
            )
            bloques_duros = cur.fetchall()
 
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
    """
    Intenta encontrar tramos que sumen 'duracion' horas en el día dado.
 
    Reglas:
      - Los bloques BLANDOS (horarios_bloqueados) se pueden saltar:
        se acumula el tiempo antes y después del bloqueo.
      - Los bloques DUROS (subtareas) no se pueden saltar:
        si chocamos con uno, reseteamos el acumulado y empezamos de cero
        desde después del bloque duro.
 
    Devuelve una lista de tramos [(inicio, fin), ...] que en total suman
    la duración pedida, o None si el día no tiene tiempo suficiente.
 
    Ejemplo con EXAMEN (3h):
      Huecos: 08:30→12:30 (4h) con bloqueo blando 10:00→10:30 en el medio
      → tramos: [(8.5, 10.0), (10.5, 12.0)]  →  1.5h + 1.5h = 3h  
 
    Ejemplo con subtarea bloqueando:
      Huecos: 08:30→10:00 libre, 10:00→11:00 SUBTAREA (duro), 11:00→14:00 libre
      → el acumulado se resetea al tocar la subtarea
      → se busca desde 11:00, encuentra 3h continuas hasta 14:00  
    """
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
            tramos.append((inicio_tramo, inicio_tramo + necesitamos))
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
                tramos.append((inicio_tramo, inicio_tramo + necesitamos))
                acumulado = duracion
 
    if acumulado < duracion:
        return None
 
    return tramos
 
 
# ── 4. Insertar tramos de una sesión ─────────────────────────────────────────
 
def _insertar_sesion(conn, tarea_id: int, telefono: str, fecha: date,
                     tramos: list[tuple], sesion_grupo: int):
    """
    Inserta uno o más registros en subtareas para los tramos de una sesión.
    Todos comparten el mismo sesion_grupo para poder agruparlos en el calendario.
    """
    with conn.cursor() as cur:
        for inicio, fin in tramos:
            duracion_tramo = fin - inicio
            cur.execute(
                """
                INSERT INTO squema1.subtareas
                    (tarea_id, telefono, fecha, hora_inicio, hora_fin, duracion, estado, sesion_grupo)
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDIENTE', %s)
                """,
                (tarea_id, telefono, fecha, inicio, fin, duracion_tramo, sesion_grupo)
            )
 
 
# ── 5. Orquestador principal ──────────────────────────────────────────────────
 
def planificar_tarea(tarea_id: int) -> list[dict]:
    """
    Punto de entrada. Recibe el id de la tarea recién insertada,
    calcula el régimen de sesiones y las agenda en squema1.subtareas.
 
    Devuelve la lista de sesiones agendadas para el mensaje de confirmación.
    Cada sesión tiene: fecha, tramos [(inicio, fin)], duracion_total, sesion_grupo.
    """
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



def check_reminders():
    print("Chequeando tareas...")

    today = datetime.now().strftime("%d-%m")

    tasks = get_tasks()

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