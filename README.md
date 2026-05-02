# WiCal

> Sistema de organización de tareas académicas con planificación automática vía WhatsApp y calendario web.

## Integrantes

Martín Bentura, Santiago Martínez, Agustina Pereyra, Mateo Yavitz, Diego Cabrera

---

## Descripción

WiCal permite al estudiante registrar y gestionar tareas académicas por WhatsApp y visualizarlas en un calendario web interactivo. Para tareas de tipo **EXAMEN** o **TAREA**, el sistema genera automáticamente sesiones de estudio distribuidas desde el día del registro hasta el deadline, respetando la rutina del usuario, evitando solapamientos con otras sesiones.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.14 + Flask |
| Base de datos | PostgreSQL 16 |
| Mensajería | Twilio (WhatsApp Sandbox) |
| LLM | Anthropic Claude Haiku |
| Túnel local | ngrok |
| Frontend | HTML + CSS + JavaScript |

---

## Estructura del proyecto

```
WiCal/
├── main.py                        # Punto de entrada Flask
├── config/
│   └── config.py                  # URL base de ngrok
├── schema.sql                     # Schema completo de la BD
├── requirements.txt
├── run.bat                        # Script de inicio (Windows)
├── run.sh                         # Script de inicio (Linux)
│
├── app/
│   ├── __init__.py                # Factory de Flask, registro de rutas
│   │
│   ├── routes/
│   │   ├── webhook.py             # Entrada de mensajes WhatsApp (Twilio)
│   │   ├── calendar.py            # Sirve el calendario web
│   │   ├── reagendar_tarea.py     # Endpoint PUT deadline + replanificación
│   │   ├── completar_tarea.py     # Endpoint marcar tarea completada
│   │   └── borrar_tarea.py        # Endpoint eliminar tarea y sesiones
│   │
│   ├── services/
│   │   └── service.py             # Lógica de negocio (orquesta storage + scheduler)
│   │
│   ├── storage/
│   │   ├── database.py            # Conexión psycopg2 a PostgreSQL
│   │   ├── task_store.py          # CRUD de tareas y subtareas
│   │   ├── user_store.py          # CRUD de usuarios
│   │   ├── sesiones.py            # States UUID para autenticación del calendario
│   │   └── conversacion.py        # Contexto de conversación activa por usuario
│   │
│   ├── utils/
│   │   ├── parser.py              # Parseo de intents, fechas y datos de tareas
│   │   ├── helpers.py             # Utilidades: fmt() para horas, generate_state()
│   │   └── state.py               # Generación de UUID de sesión
│   │
│   └── integrations/
│       ├── llm_haiku.py           # Cliente Anthropic Claude Haiku
│       └── twilio_client.py       # Cliente Twilio + auto-config de webhook
│
├── scheduler/
│   └── scheduler.py               # Motor de planificación automática de sesiones
│
└── static/
    ├── js/
    │   ├── utils.js               # Utilidades de fecha y formato
    │   ├── tasks.js               # Array de tareas, helpers, fetch de acciones
    │   ├── monthView.js           # Vista mensual
    │   ├── weekView.js            # Vista semanal con bloques por hora
    │   ├── taskMenu.js            # Menú contextual (completar, mover, borrar)
    │   ├── taskCreator.js         # Modal de creación de tarea
    │   ├── modal.js               # Sistema de modales genérico
    │   └── script.js              # Inicialización y navegación del calendario
    │
    ├── styles/
    │   ├── base.css               # Reset, layout, clases de prioridad
    │   ├── month.css              # Estilos vista mensual
    │   ├── week.css               # Estilos vista semanal
    │   ├── components.css         # Menú, modales, scrollbar
    │   └── responsive.css         # Media queries
    │
    ├── logo_wical.png
    └── background.png
```

---

## Base de datos

```sql
usuario              -- Usuarios registrados (tel como clave natural)
tarea                -- Tareas académicas (nombre, deadline, tipo, status)
subtareas            -- Sesiones de estudio generadas por el scheduler
sesiones             -- States UUID para autenticación del calendario web
sesion_conversacion  -- Contexto de conversación activa por usuario en WhatsApp
horarios_bloqueados  -- Rutina del usuario (bloques de tiempo no disponibles)
grupo                -- Grupos de trabajo (funcionalidad futura)
```

### Tipos de tarea

| Tipo | Planificación automática | Duración base por sesión |
|---|---|---|
| `EXAMEN` | Sí | 3 horas |
| `TAREA` |  Sí | 2 horas |
| `PRACTICO` | No | 1 hora|

### Estados de tarea

| Estado | Descripción |
|---|---|
| `PENDIENTE` | Estado inicial |
| `COMPLETADA` | Marcada como completada |

---

## Planificación automática (scheduler)

Al registrar o reagendar una tarea de tipo `EXAMEN` o `TAREA`, el scheduler genera sesiones de estudio automáticamente según el tiempo disponible hasta el deadline:

| Tiempo hasta deadline | Frecuencia | Duración por sesión |
|---|---|---|
| Más de 7 días | Día de por medio | Base |
| 7 días exactos | Todos los días | Base |
| 2 a 6 días | Todos los días | Base × 1.5 |
| 1 día | Todos los días | Base × 2.5 |

### Tipos de bloqueo

El scheduler distingue dos tipos de bloqueos al calcular los slots disponibles:

**Bloques blandos** (`horarios_bloqueados`): representan la rutina del usuario (dormir, comer, descanso). La sesión **se puede partir** en tramos alrededor de ellos — por ejemplo, estudiar 2h antes del almuerzo y 1h después.

**Bloques duros** (subtareas ya agendadas): representan sesiones de otras tareas ya planificadas. La sesión **no se puede partir** — si hay conflicto, se busca el siguiente hueco disponible en días posteriores.

### Bloques de rutina por defecto

Si el usuario no configura sus propios bloques, se aplican los siguientes (tomando como ejemplo estudiantes de la licenciatura):

| Horario | Motivo |
|---|---|
| 00:00 – 08:00 | Sueño |
| 08:00 – 08:30 | Desayuno |
| 12:30 – 13:00 | Almuerzo |
| 17:00 – 17:30 | Pausa tarde/Merienda |
| 18:00 – 22:00 | Clases |
| 23:00 – 00:00 | Cierre del día |

Los bloques por defecto se almacenan con `telefono = NULL` y `dia_semana = NULL` para que apliquen a todos los usuarios y todos los días.

---

## Comandos WhatsApp

| Intent | Ejemplos de mensaje |
|---|---|
| Agregar tarea | `Añadir parcial de matemáticas el jueves 8 de mayo a las 16:00` |
| Agregar múltiples (LLM) | `!multi tengo parcial de física el 10/06 y entrega de redes el 12/06` |
| Listar tareas | `Ver tareas`, `Mis tareas` |
| Tareas de hoy | `Ver tareas de hoy`, `Mis tareas de hoy` |
| Completar tarea | `Completar tarea` |
| Reagendar tarea | `Reagendar tarea` → responder `(id), (nueva fecha)` |
| Eliminar tarea | `Eliminar tarea`, `Borrar tarea` → responder `(id)`|
| Ver calendario | `Calendario`, `Ver calendario` |

---

## Calendario web

El calendario web es accesible vía link generado por WhatsApp con un `state` UUID de sesión de corta duración. Incluye:

- **Vista mensual**: muestra las tareas con color según tipo (EXAMEN = rojo, TAREA = naranja, PRACTICO = azul, Completada = verde).
- **Vista semanal**: muestra tareas y sesiones de estudio posicionadas por hora, con soporte para sesiones partidas en múltiples tramos.
- **Drag & drop**: reagendar tareas arrastrándolas a otro día/hora, con replanificación automática de sesiones.
- **Menú contextual** (click derecho): cambiar nombre, cambiar fecha/hora, completar o eliminar tarea.
- **Resumen semanal**: cantidad de tareas, carga por día y tip de estudio.

### Autenticación del calendario

El calendario no requiere login. El acceso se controla mediante un `state` UUID generado en cada mensaje de WhatsApp y almacenado en la tabla `sesiones`. Cada operación desde el frontend (reagendar, completar, borrar) valida el `state` contra la BD para identificar al usuario sin exponer el número de teléfono.

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/webhook` | Recibe mensajes de WhatsApp via Twilio |
| `GET` | `/calendar?state=<uuid>` | Sirve el calendario web del usuario |
| `POST` | `/reagendar_tarea` | Actualiza deadline, borra sesiones viejas y replanifica |
| `POST` | `/completar_tarea` | Marca tarea como `COMPLETADA` |
| `POST` | `/borrar_tarea` | Elimina tarea y sus sesiones |

Todos los endpoints POST del calendario reciben `{ task_id, state }` y validan el `state` antes de operar.

---

## Instalación y ejecución

### Requisitos

- Python 3.14+
- PostgreSQL 16+
- Cuenta Twilio con número de WhatsApp (sandbox disponible)
- ngrok
- Clave API de Anthropic

### Setup

```bash
# 1. Clonar el repositorio
git clone <repo>
cd WiCal

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear la base de datos
psql -U postgres -c "CREATE DATABASE syncal;"
psql -U postgres -d syncal -f schema.sql

# 6. Configurar variables de entorno
cp .env.example .env
# Completar con tus credenciales
```

### Variables de entorno (.env)

```env
ANTHROPIC_API_KEY=sk-ant-...
TWILIO_SID=AC...
TWILIO_TOKEN=...
```

### Iniciar el sistema

**Windows:**
```bat
run.bat
```

**Linux:**
```bash
chmod +x run.sh
./run.sh
```

Ambos scripts levantan Flask en el puerto 5000, inician ngrok y configuran el webhook de Twilio automáticamente.

---

## Variables de configuración

`config/config.py` contiene la `BASE_URL` que se usa para generar el link del calendario en los mensajes de WhatsApp. Esta URL se actualiza automáticamente al ejecutar el script de inicio via `scripts/auto_config.py`.
