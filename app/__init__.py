from flask import Flask
from app.routes.webhook import webhook
from app.routes.calendar import calendar
from app.routes.reagendar_tarea import reagendar_tarea_route
from app.routes.completar_tarea import completar_tarea_route
from app.routes.borrar_tarea import borrar_tarea_route

def create_app():
    app = Flask(__name__)

    app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])
    app.add_url_rule("/calendar", view_func=calendar, methods=["GET"])
    app.add_url_rule("/reagendar_tarea", view_func=reagendar_tarea_route,methods=['POST'])
    app.add_url_rule("/completar_tarea", view_func=completar_tarea_route, methods=['POST'])
    app.add_url_rule("/borrar_tarea", view_func=borrar_tarea_route, methods=['POST'])
    
    return app