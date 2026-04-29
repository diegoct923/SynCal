from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.webhook import webhook
    from app.routes.calendar import calendar
    from app.routes.reagendar_tarea import reagendar_tarea_route

    app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])
    app.add_url_rule("/calendar", view_func=calendar, methods=["GET"])
    app.add_url_rule("/reagendar_tarea", view_func=reagendar_tarea_route,methods=['POST'])
    return app