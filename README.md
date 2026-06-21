# WiCal

> Asistente de organizacion academica con gestion por WhatsApp, calendario web, planificacion automatica de sesiones de estudio y recordatorios.

## Integrantes

Martin Bentura, Diego Cabrera, Santiago Martinez, Agustina Pereyra, Mateo Yavitz.

## Descripcion

WiCal permite registrar, consultar y administrar tareas academicas desde WhatsApp y verlas en un calendario web autenticado con Google. Para tareas de tipo `EXAMEN` o `TAREA`, el sistema genera sesiones de estudio automaticamente y las muestra en el calendario junto con las tareas originales.

El proyecto actualmente esta separado en servicios Docker:

- `web`: aplicacion Flask del calendario, login, registro, API REST y Socket.IO.
- `whatsapp`: webhook Flask que recibe mensajes de Twilio/WhatsApp.
- `celery_worker`: worker Celery que planifica sesiones de estudio en segundo plano.
- `notifications`: scheduler de recordatorios y resumen diario por WhatsApp.
- `postgres`: base de datos PostgreSQL.
- `rabbitmq`: broker para Celery y cola de mensajes de Socket.IO.
- `nginx`: proxy inverso; expone la app en `http://localhost:8080` y deriva `/webhook` al servicio de WhatsApp.
- `ngrok`: tunel publico hacia Nginx para integracion con Twilio.

## Stack

| Capa | Tecnologia |
|---|---|
| Backend | Python 3.11 + Flask |
| Calendario web | HTML, CSS, JavaScript |
| Tiempo real | Flask-SocketIO + RabbitMQ |
| Tareas asincronas | Celery |
| Base de datos | PostgreSQL 16 |
| Mensajeria | Twilio WhatsApp |
| LLM | Anthropic Claude Haiku |
| Autenticacion | Google OAuth 2.0 |
| Proxy / despliegue local | Nginx, Docker Compose, ngrok |

## Estructura del proyecto

```text
SynCal/
|-- docker-compose.yml
|-- schema.sql
|-- requirements.txt
|-- run.bat / run.sh
|-- nginx/
|   `-- default.conf
|-- web/
|   |-- main.py
|   |-- __init__.py
|   |-- routes/
|   |   |-- api.py
|   |   |-- calendar.py
|   |   |-- callback.py
|   |   |-- login.py
|   |   |-- logout.py
|   |   `-- registro.py
|   |-- templates/
|   `-- static/
|-- whatsapp/
|   |-- main.py
|   `-- webhook.py
|-- notifications/
|   `-- main.py
|-- celery_worker/
|   `-- Dockerfile
|-- shared/
|   |-- celery_app.py
|   |-- celery_tasks.py
|   |-- config/
|   |-- integrations/
|   |-- scheduler/
|   |-- services/
|   |-- storage/
|   `-- utils/
`-- scripts/
    |-- auto_config.py
    `-- ngrok_utils.py
```

## Flujo principal

1. El usuario escribe al bot de WhatsApp.
2. Twilio envia el mensaje a `/webhook`.
3. El servicio `whatsapp` interpreta el comando y registra/consulta/modifica datos en PostgreSQL.
4. Si se crea una tarea planificable (`EXAMEN` o `TAREA`), se envia una tarea a Celery.
5. `celery_worker` calcula las sesiones de estudio y las guarda como `subtareas`.
6. El calendario web consume la API REST y recibe actualizaciones en tiempo real por Socket.IO.
7. `notifications` envia resumen diario y recordatorios puntuales por WhatsApp.

## Funcionalidades

- Alta de tareas academicas por WhatsApp.
- Parseo de fechas, horas y tipos de tarea en lenguaje natural.
- Carga multiple con `!multi` usando Claude Haiku.
- Listado de tareas y tareas del dia.
- Completar, eliminar y reagendar tareas mediante conversaciones guiadas.
- Creacion de grupos por username y tareas grupales.
- Validacion de disponibilidad comun para tareas grupales.
- Calendario web con vista mensual y semanal.
- Login con Google y registro de username.
- Drag and drop / acciones desde calendario para reagendar, completar, editar o eliminar.
- Gestion de horarios bloqueados personales y defaults.
- Actualizaciones en tiempo real con WebSockets.
- Recordatorios configurables entre 5 y 120 minutos antes.

## Tipos de tarea

| Tipo interno | Se planifica automaticamente | Uso |
|---|---:|---|
| `EXAMEN` | Si | parciales, examenes |
| `TAREA` | Si | tareas, entregas, deberes, presentaciones |
| `PRACTICO` | No | practicos, lecturas, ejercicios, actividades |
| `UNKNOWN` | No | tipo no detectado |

En el calendario, la prioridad del frontend se traduce asi:

| Prioridad UI | Tipo interno |
|---|---|
| `alta` | `EXAMEN` |
| `media` | `TAREA` |
| `baja` | `PRACTICO` |

## Base de datos

El schema vive en `schema.sql` y se carga automaticamente al levantar PostgreSQL con Docker Compose.

Tablas principales:

| Tabla | Descripcion |
|---|---|
| `squema1.usuario` | Usuarios, telefono, Google ID, email, username y configuracion de notificaciones |
| `squema1.tarea` | Tareas principales |
| `squema1.subtareas` | Sesiones de estudio generadas por el scheduler |
| `squema1.grupo` | Grupos de trabajo |
| `squema1.grupo_usuario` | Relacion entre grupos y usuarios |
| `squema1.sesiones` | States UUID para acceder al calendario |
| `squema1.sesion_conversacion` | Contexto pendiente de conversaciones por WhatsApp |
| `squema1.horarios_bloqueados` | Horarios no disponibles del usuario y defaults globales |
| `squema1.horarios_bloqueados_excluidos` | Defaults ocultados por usuario |

Los horarios bloqueados globales se insertan desde `schema.sql` con `usuario_tel = NULL`.

## Comandos de WhatsApp

| Accion | Ejemplo |
|---|---|
| Ayuda | `/ayuda` |
| Agregar tarea | `anadir parcial Calculo 15/06 a las 16:00` |
| Agregar varias tareas | `!multi anadir parcial Fisica 10/06 anadir entrega Redes 12/06` |
| Ver tareas | `ver tareas` |
| Ver tareas de hoy | `ver tareas hoy` |
| Ver calendario | `ver calendario` |
| Completar tarea | `completar tarea` y luego responder con el numero |
| Reagendar tarea | `reagendar tarea` y luego responder `numero, nueva fecha` |
| Eliminar tarea | `eliminar tarea` y luego responder con el numero |
| Crear grupo | `crear grupo Redes 2, integrantes: santi, diego` |
| Crear tarea grupal | `anadir tarea grupal parcial Calculo 15/06 a las 16:00` |
| Configurar recordatorios | `configurar anticipacion 30 minutos` |

## Calendario web

El calendario se accede desde un link generado por WhatsApp:

```text
/calendar?state=<uuid>
```

Flujo de autenticacion:

1. El usuario pide el calendario por WhatsApp.
2. El bot genera un `state` y devuelve el link.
3. Si no hay sesion Flask activa, se redirige a `/login?state=<uuid>`.
4. Google devuelve un token al endpoint `/callback`.
5. Si es el primer acceso y falta username, se redirige a `/registro`.
6. Con sesion valida, se renderiza `calendario.html`.

El calendario incluye tareas, sesiones de estudio, vista mensual, vista semanal, panel de resumen, acciones contextuales y gestion de franjas bloqueadas.

## Endpoints

### WhatsApp

| Metodo | Ruta | Servicio | Descripcion |
|---|---|---|---|
| `POST` | `/webhook` | `whatsapp` | Recibe mensajes entrantes de Twilio |

### Web y autenticacion

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/calendar?state=<uuid>` | Muestra el calendario si el state y la sesion son validos |
| `GET` | `/login?state=<uuid>` | Login con Google |
| `POST` | `/callback` | Valida token de Google y abre sesion Flask |
| `GET/POST` | `/registro?state=<uuid>` | Registro de username |
| `GET` | `/logout?state=<uuid>` | Cierra sesion |

### API REST del calendario

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/api/tasks?state=<uuid>` | Obtiene tareas y sesiones |
| `POST` | `/api/tasks/create` | Crea una tarea |
| `POST` | `/api/tasks/complete` | Marca una tarea como completada |
| `POST` | `/api/tasks/delete` | Elimina una tarea |
| `POST` | `/api/tasks/reagendar` | Cambia deadline y replanifica sesiones |
| `POST` | `/api/tasks/nombre` | Actualiza nombre |
| `POST` | `/api/tasks/prioridad` | Actualiza prioridad/tipo |
| `GET` | `/api/tasks/blocked-slots?state=<uuid>` | Lista horarios bloqueados |
| `POST` | `/api/blocked-slots/create` | Crea una franja bloqueada |
| `POST` | `/api/blocked-slots/delete` | Elimina u oculta una franja bloqueada |

Todos los endpoints operativos validan el `state` antes de acceder a datos del usuario.

## Variables de entorno

Crear un archivo `.env` en la raiz del proyecto.

```env
# App
BASE_URL=http://localhost:8080
FLASK_SECRET_KEY=syncal-dev-secret

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRESDB_NAME=syncal
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
OPTIONS=

# RabbitMQ / Celery / Socket.IO
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
SOCKETIO_MESSAGE_QUEUE=amqp://guest:guest@rabbitmq:5672//

# Twilio
TWILIO_SID=AC...
TWILIO_TOKEN=...
TWILIO_FROM_WHATSAPP=whatsapp:+14155238886

# Google OAuth
GOOGLE_CLIENT_ID=...apps.googleusercontent.com

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# ngrok
NGROK_AUTHTOKEN=...
```

En Docker Compose, varios valores tienen defaults para desarrollo. Las credenciales reales de Twilio, Google, Anthropic y ngrok deben configurarse en `.env`.

## Ejecucion con Docker Compose

Requisito: Docker Desktop o Docker Engine con Compose.

```bash
docker compose up --build
```

Servicios expuestos:

| Servicio | URL |
|---|---|
| App web via Nginx | `http://localhost:8080` |
| RabbitMQ Management | `http://localhost:15672` |
| Web Flask interno | `web:5000` |
| WhatsApp Flask interno | `whatsapp:5001` |

El servicio `ngrok` publica Nginx hacia internet. La URL publica debe coincidir con `BASE_URL` para que los links enviados por WhatsApp y OAuth apunten al dominio correcto.

## Ejecucion local sin Docker

El camino recomendado es Docker Compose. Los scripts `run.bat` y `run.sh` son auxiliares para levantar una version local con entorno virtual, Flask y ngrok, pero no reflejan toda la orquestacion actual de servicios separados.

Para ejecucion manual se necesitan, como minimo:

- Python 3.11.
- PostgreSQL accesible con el schema cargado.
- RabbitMQ si se quiere usar Celery y Socket.IO con cola.
- ngrok para exponer `/webhook`.
- Variables `.env` apuntando a servicios locales.

## Configuracion externa

### Twilio WhatsApp

Configurar el webhook entrante del numero/sandbox hacia:

```text
https://<tu-dominio-ngrok>/webhook
```

El helper `scripts/auto_config.py` puede leer la URL local de ngrok y actualizar el webhook de Twilio usando las credenciales del `.env`.

### Google OAuth

En Google Cloud Console, crear un OAuth Client ID de tipo Web Application y registrar el origen/URL usados por el frontend. El login usa Google Identity Services y el backend valida el token recibido en `/callback` con `GOOGLE_CLIENT_ID`.

### Anthropic

`shared/integrations/llm_haiku.py` usa `ANTHROPIC_API_KEY` para parsear mensajes `!multi` con el modelo configurado en el codigo.

## Notificaciones

El servicio `notifications` ejecuta `shared.scheduler.notificaciones.run_scheduler()`.

Se contemplan:

- Resumen diario por WhatsApp.
- Recordatorios antes de tareas y sesiones.
- Anticipacion configurable por usuario con default de 15 minutos y rango de 5 a 120 minutos.

## Desarrollo

Comandos utiles:

```bash
docker compose up --build
docker compose logs -f web
docker compose logs -f whatsapp
docker compose logs -f celery_worker
docker compose logs -f notifications
docker compose down
```

Si se modifica `schema.sql` y se quiere recrear la base desde cero:

```bash
docker compose down -v
docker compose up --build
```

Esto elimina los volumenes de PostgreSQL y WhatsApp definidos por Compose.
