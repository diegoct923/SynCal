from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.webhook import webhook
    from app.routes.callback import callback

    app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])
    app.add_url_rule("/callback", view_func=callback)

    return app