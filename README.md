# WiCal

> Sistema de organización de tareas académicas con planificación automática vía WhatsApp y calendario web.

## Integrantes

Martín Bentura, Diego Cabrera, Santiago Martínez, Agustina Pereyra, Mateo Yavitz.

---

## Descripción

WiCal permite al estudiante registrar y gestionar tareas académicas por WhatsApp y visualizarlas en un calendario web interactivo. Para tareas de tipo **EXAMEN** o **TAREA**, el sistema genera automáticamente sesiones de estudio distribuidas desde el día del registro hasta el deadline, respetando la rutina del usuario y evitando solapamientos con otras sesiones. El sistema también soporta **grupos de trabajo** con tareas compartidas entre integrantes, verificando disponibilidad horaria de todos los miembros antes de agendar.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.14 + Flask |
| Base de datos | PostgreSQL 16 |
| Mensajería | Twilio (WhatsApp Sandbox) |
| LLM | Anthropic Claude Haiku |
| Autenticación | Google OAuth 2.0 |
| Tiempo real | Flask-SocketIO |
| Túnel local | ngrok |
| Frontend | HTML + CSS + JavaScript |

---

## Estructura del proyecto

```
WiCal/
├── main.py                        # Punto de entrada Flask + arranque del scheduler
├── config/
│   └── config.py                  # URL base de ngrok, credenciales Google OAuth
├── schema.sql                     # Schema completo de la BD
├── requirements.txt
├── run.bat                        # Script de inicio (Windows)
├── run.sh                         # Script de inicio (Linux)
│
├── app/
│   ├── __init__.py                # Factory de Flask, registro de rutas
│   ├── extensions.py              # Instancia de SocketIO
│   ├── sockets.py                 # Handlers de conexión WebSocket
│   ├── events.py                  # Funciones para emitir eventos a clientes
│   │
│   ├── routes/
│   │   ├── webhook.py             # Entrada de mensajes WhatsApp (Twilio)
│   │   ├── calendar.py            # Sirve el calendario web
│   │   ├── api.py                 # API REST para el calendario web
│   │   ├── login.py               # Sirve la página de login con Google
│   │   ├── callback.py            # Callback de Google OAuth, maneja sesión Flask
│   │   └── registro.py            # Registro de username tras primer login
│   │
│   ├── services/
│   │   └── service.py             # Lógica de negocio (orquesta storage + scheduler)
│   │
│   ├── storage/
│   │   ├── database.py            # Conexión psycopg2 a PostgreSQL
│   │   ├── task_store.py          # CRUD de tareas y subtareas
│   │   ├── grupo_store.py         # CRUD de grupos y tareas grupales
│   │   ├── user_store.py          # CRUD de usuarios
│   │   ├── sesiones.py            # States UUID para autenticación del calendario
│   │   └── conversacion.py        # Contexto de conversación activa por usuario
│   │
│   ├── utils/
│   │   ├── parser.py              # Parseo de intents, fechas y datos de tareas
│   │   ├── helpers.py             # Utilidades: fmt(), get_user_tel_from_state()
│   │   └── state.py               # Generación de UUID de sesión
│   │
│   └── integrations/
│       ├── llm_haiku.py           # Cliente Anthropic Claude Haiku
│       └── twilio_client.py       # Cliente Twilio + auto-config de webhook
│
├── scheduler/
│   ├── scheduler.py               # Motor de planificación + recordatorios
│   ├── manejo_de_bloques.py       # Carga y merge de bloques horarios
│   └── disponibilidad.py          # Verificación de disponibilidad grupal
│
└── static/
    ├── js/
    │   ├── config.js              # BASE_URL del backend
    │   ├── api.js                 # Funciones fetch hacia la API REST
    │   ├── socket.js              # Cliente WebSocket (Socket.IO)
    │   ├── utils.js               # Utilidades de fecha, formato y touch
    │   ├── tasks.js               # Array de tareas, helpers, carga desde backend
    │   ├── monthView.js           # Vista mensual
    │   ├── weekView.js            # Vista semanal con bloques por hora
    │   ├── taskMenu.js            # Menú contextual (completar, mover, borrar)
    │   ├── taskCreator.js         # Modal de creación de tarea
    │   ├── blockSlots.js          # Modal de gestión de franjas bloqueadas
    │   ├── modal.js               # Sistema de modales genérico
    │   └── script.js              # Inicialización y navegación del calendario
    │
    ├── styles/
    │   ├── base.css               # Reset, layout, clases de prioridad
    │   ├── month.css              # Estilos vista mensual
    │   ├── week.css               # Estilos vista semanal
    │   ├── components.css         # Menú, modales, scrollbar
    │   └── responsive.css         # Media queries (incluye vista mobile)
    │
    ├── logo_wical.png
    └── background.png
```

---

## Base de datos

### Tablas

| Tabla | Descripción |
|---|---|
| `usuario` | Usuarios registrados |
| `tarea` | Tareas académicas |
| `subtareas` | Sesiones de estudio generadas por el scheduler |
| `grupo` | Grupos de trabajo |
| `grupo_usuario` | Relación muchos a muchos entre grupos y usuarios |
| `sesiones` | States UUID para autenticación del calendario web |
| `sesion_conversacion` | Contexto de conversación activa por usuario en WhatsApp |
| `horarios_bloqueados` | Rutina del usuario (bloques de tiempo no disponibles) |

---

### Tipos de tarea

| Tipo | Planificación automática | Duración base por sesión |
|---|---|---|
| `EXAMEN` | Sí | 3 horas |
| `TAREA` | Sí | 1.5 horas |
| `PRACTICO` | No | — |

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

**Bloques blandos** (`horarios_bloqueados`): representan la rutina del usuario. La sesión **se puede partir** en tramos alrededor de ellos.

**Bloques duros** (subtareas ya agendadas): la sesión **no se puede partir** — si hay conflicto, se busca el siguiente hueco disponible.

### Bloques de rutina por defecto

Los bloques con `usuario_tel = NULL` y `dia_semana = NULL` aplican a todos los usuarios y todos los días:

| Horario | Motivo |
|---|---|
| 00:00 – 08:00 | Sueño |
| 08:00 – 08:30 | Desayuno |
| 12:30 – 13:00 | Almuerzo |
| 17:00 – 17:30 | Pausa tarde / Merienda |
| 18:00 – 22:00 | Clases |
| 23:00 – 00:00 | Cierre del día |

---

## Grupos de trabajo

Los grupos permiten compartir tareas entre integrantes. Solo el creador puede agregar tareas grupales. Al agendar una tarea grupal, el sistema verifica que todos los integrantes tengan ese horario libre. Si hay conflicto, sugiere el próximo hueco disponible en común dentro de los siguientes 14 días.

---

## Sistema de notificaciones

El scheduler corre en un thread separado y envía dos tipos de notificaciones por WhatsApp:

**Resumen diario** — todos los días a las 8:00 AM con todas las tareas y sesiones de estudio del día.

**Recordatorio puntual** — X minutos antes de cada tarea o sesión, configurable por usuario (`minutos_anticipacion_notificacion`, default 15 min, rango 5–120 min).

---

## Comandos WhatsApp

| Intent | Ejemplos de mensaje |
|---|---|
| Agregar tarea | `Añadir parcial de matemáticas el jueves 8 de mayo a las 16:00` |
| Agregar múltiples (LLM) | `!multi tengo parcial de física el 10/06 y entrega de redes el 12/06` |
| Listar tareas | `Ver tareas`, `Mis tareas` |
| Tareas de hoy | `Ver tareas de hoy`, `Mis tareas de hoy` |
| Completar tarea | `Completar tarea` → responder con número de tarea |
| Reagendar tarea | `Reagendar tarea` → responder `(id), (nueva fecha)` |
| Eliminar tarea | `Eliminar tarea`, `Borrar tarea` → responder con número de tarea |
| Ver calendario | `Calendario`, `Ver calendario` |
| Crear grupo | `Crear grupo Redes 2, integrantes: user1, user2` |
| Tarea grupal | `Añadir tarea grupal parcial el 10 de junio a las 16:00` → elegir grupo |
| Configurar anticipación | `Configurar anticipación 30 minutos` |

---

## Calendario web

El calendario web es accesible vía link generado por WhatsApp con un `state` UUID de sesión. Incluye:

- **Vista mensual y semanal**: tareas posicionadas por hora con color según tipo. Las tareas grupales se identifican con 👥.
- **Vista mobile**: interfaz adaptada para dispositivos móviles.
- **Sesiones de estudio**: bloques generados por el scheduler visibles en la vista semanal, con soporte para sesiones partidas en múltiples tramos.
- **Drag & drop**: reagendar tareas arrastrándolas, con replanificación automática de sesiones.
- **Menú contextual**: editar nombre, cambiar fecha/hora, cambiar prioridad, completar, cambiar tipo grupal/individual o eliminar tarea.
- **Gestor de franjas bloqueadas**: agregar y eliminar bloques de horario personal.
- **Tiempo real**: actualizaciones instantáneas via WebSockets — crear, completar, reagendar o eliminar tareas se refleja sin recargar la página.
- **Resumen semanal**: cantidad de tareas, carga por día y tip de estudio.

### Autenticación del calendario

```
Usuario pide calendario por WhatsApp
→ Recibe link /calendar?state=uuid
→ Abre link → si no tiene sesión activa → redirige a /login
→ Se autentica con Google
→ Primera vez: redirige a /registro para elegir username
→ Sesión Flask activa → accede al calendario
```

---

## Endpoints

### WhatsApp
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/webhook` | Recibe y procesa mensajes de WhatsApp via Twilio |

### Autenticación
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/login?state=<uuid>` | Sirve la página de login con Google |
| `POST` | `/callback` | Valida token Google, crea sesión Flask |
| `GET/POST` | `/registro?state=<uuid>` | Registro de username |
| `GET` | `/calendar?state=<uuid>` | Sirve el calendario web |

### API REST (calendario web)
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/tasks?state=<uuid>` | Obtiene tareas y sesiones del usuario |
| `POST` | `/api/tasks/create` | Crea nueva tarea |
| `POST` | `/api/tasks/reagendar` | Reagenda tarea y replanifica sesiones |
| `POST` | `/api/tasks/complete` | Marca tarea como completada |
| `POST` | `/api/tasks/delete` | Elimina tarea y sus sesiones |
| `POST` | `/api/tasks/nombre` | Actualiza nombre de tarea |
| `POST` | `/api/tasks/prioridad` | Actualiza tipo/prioridad de tarea |
| `POST` | `/api/tasks/grupal` | Actualiza flag grupal de tarea |
| `GET` | `/api/tasks/blocked-slots` | Obtiene franjas bloqueadas del usuario |

Todos los endpoints de la API reciben `state` en el body o query param y lo validan antes de operar.

---

## Instalación y ejecución

### Requisitos

- Python 3.12 (eventlet no es compatible con 3.14+, usar threading)
- PostgreSQL 16+
- Cuenta Twilio con número de WhatsApp (sandbox disponible)
- ngrok
- Clave API de Anthropic
- Proyecto en Google Cloud Console con OAuth 2.0 configurado

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
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=...
FLASK_SECRET_KEY=...
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

Ambos scripts levantan Flask en el puerto 5000, inician ngrok y configuran el webhook de Twilio automáticamente. El scheduler de notificaciones arranca automáticamente en un thread separado.

### Configuración de Google OAuth

1. Ir a [console.cloud.google.com](https://console.cloud.google.com)
2. APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
3. Application type: **Web application**
4. Authorized redirect URIs: `https://<tu-url-ngrok>/callback`
5. Copiar `Client ID` y `Client Secret` al `.env`
