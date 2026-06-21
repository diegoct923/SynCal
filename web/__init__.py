from logging import log

from flask import Flask
from web.extensions import socketio
from web.routes import registro
from web.routes.calendar import calendar
from web.routes.callback import google_callback
from web.routes.login import login
from web.routes.logout import logout
from web.routes.registro import registro
from web.routes.api import (api_get_tasks, api_create_task, api_complete_task, api_delete_task, api_reagendar_task, api_update_nombre, 
                            api_update_prioridad, api_get_blocked_slots, api_create_blocked_slot, api_delete_blocked_slot)

import os
def create_app():   
    app = Flask(__name__)

    socketio.init_app(app, cors_allowed_origins="*")

    from web import sockets

    
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
