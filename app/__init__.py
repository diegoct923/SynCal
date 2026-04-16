from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.webhook import webhook
    from app.routes.calendar import calendar

    
    app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])
    app.add_url_rule("/calendar", view_func=calendar, methods=["GET"])
    
    return app