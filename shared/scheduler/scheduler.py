from shared.storage.database import connect_db
from datetime import datetime, date, timedelta
from shared.scheduler.manejo_de_bloques import cargar_bloques, merge_bloques





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
 
 


 
 
# ── 2. Algoritmo para partir sesiones
 
def calcular_tramos(telefono: str, fecha: date, duracion: float) -> list[tuple] | None:
    
    bloques_blandos, bloques_duros = cargar_bloques(telefono, fecha)
 
    blandos_merged = merge_bloques(bloques_blandos)
    duros_merged   = merge_bloques(bloques_duros)
 
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
 
 
# ── 3. Insertar tramos de una sesión ─────────────────────────────────────────
 
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
 
 
# ── 4. Orquestador principal ──────────────────────────────────────────────────
 
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
            conn.commit()  # ← commit después de cada sesión para que _cargar_bloques la vea

            sesiones_agendadas.append({
                "fecha":          fecha,
                "tramos":         tramos,
                "duracion_total": duracion,
                "sesion_grupo":   sesion_grupo,
            })

            sesion_grupo += 1

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
 
    return sesiones_agendadas



