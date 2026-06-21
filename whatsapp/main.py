import os
from flask import Flask
from dotenv import load_dotenv

from whatsapp.webhook import webhook

load_dotenv()

app = Flask(__name__)

app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)