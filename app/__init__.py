from logging import log

from flask import Flask
from app.extensions import socketio
from app.routes import registro
from app.routes.webhook import webhook
from app.routes.calendar import calendar
from app.routes.reagendar_tarea import reagendar_tarea_route
from app.routes.completar_tarea import completar_tarea_route
from app.routes.borrar_tarea import borrar_tarea_route
from app.routes.callback import google_callback
from app.routes.login import login
from app.routes.logout import logout
from app.routes.registro import registro
from app.routes.api import (api_get_tasks, api_create_task, api_complete_task, api_delete_task, api_reagendar_task, api_update_nombre, 
                            api_update_prioridad, api_get_blocked_slots, api_create_blocked_slot, api_delete_blocked_slot)

import os
def create_app():   
    app = Flask(__name__)

    socketio.init_app(app, cors_allowed_origins="*")

    from app import sockets

    app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])
    app.add_url_rule("/calendar", view_func=calendar, methods=["GET"])

    app.add_url_rule("/callback",view_func=google_callback,methods=["POST"])
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    app.add_url_rule("/login",view_func=login,methods=["GET"])
    app.add_url_rule("/logout", view_func=logout,methods=["GET"])
    app.add_url_rule("/registro",view_func=registro,methods=["GET", "POST"])
    
    app.add_url_rule("/api/tasks", view_func=api_get_tasks, methods=["GET"])
    app.add_url_rule("/api/tasks/create", view_func=api_create_task, methods=["POST"])
    app.add_url_rule("/api/tasks/complete", view_func=api_complete_task, methods=["POST"])
    app.add_url_rule("/api/tasks/delete", view_func=api_delete_task, methods=["POST"])
    app.add_url_rule("/api/tasks/reagendar", view_func=api_reagendar_task, methods=["POST"])
    app.add_url_rule("/api/tasks/nombre", view_func=api_update_nombre, methods=["POST"])
    app.add_url_rule("/api/tasks/prioridad", view_func=api_update_prioridad, methods=["POST"])
    app.add_url_rule("/api/tasks/blocked-slots", view_func=api_get_blocked_slots, methods=["GET"])
    app.add_url_rule("/api/blocked-slots/create", view_func=api_create_blocked_slot, methods=["POST"])
    app.add_url_rule("/api/blocked-slots/delete", view_func=api_delete_blocked_slot, methods=["POST"])

    return app
