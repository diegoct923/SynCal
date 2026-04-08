import os
from flask import Flask, request, jsonify
from parser import parse_message
from service import create_task
from db import get_tasks
from twilio.twiml.messaging_response import MessagingResponse
import threading
from scheduler import run_scheduler
from storage.auth_store import get_phone_from_state, delete_state
from storage.user_store import update_user_token
from storage.auth_store import save_state
from utils import generate_state
from storage.user_store import has_notion_connected, get_user
from storage.user_store import create_user_if_not_exists
from config import BASE_URL
import requests


app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")

    print(f"Mensaje de {sender}: {incoming_msg}")

    create_user_if_not_exists(sender)

    command = parse_message(incoming_msg)
    response = MessagingResponse()

  
    if command["type"] == "ADD":
         
        if not has_notion_connected(sender):
            response.message("Primero conectá tu Notion con 'Conectar Notion'")
            return str(response)
                
        else:
            create_task(
            sender,
            command["title"],
            command["date"],
            command["category"]
            )

        response.message(
            f"{command['category'].capitalize()} '{command['title']}' agregada para {command['date']}"
        )

 
    elif command["type"] == "LIST":
        tasks = get_tasks()

        
        tasks = [t for t in tasks if t["user"] == sender]

        if not tasks:
            response.message("No tenés tareas aún")
        else:
            msg = "Tus tareas:\n"

            for t in tasks:
                msg += f"- {t['category']} {t['title']} ({t['date']})\n"

            response.message(msg)

   
    elif command["type"] == "CONNECT_NOTION":

        state = generate_state()
        save_state(state, sender)

        auth_url = (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={CLIENT_ID}"
            f"&response_type=code"
            f"&owner=user"
            f"&redirect_uri={BASE_URL}/callback"
            f"&state={state}"
        )

        response.message(f"Conectá tu Notion:\n{auth_url}")

   
    else:
        response.message(
            "No entendí el comando.\n"
            "Usá:\n"
            "- Añadir Parcial/Entrega Nombre Fecha\n"
            "- Ver tareas\n"
            "- Conectar Notion"
        )

    return str(response)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    phone = get_phone_from_state(state)

    if not phone:
        return "State Invalid, KILL"
    
    response = requests.post(
        "https://api.notion.com/v1/oauth/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        json={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{BASE_URL}/callback"
        }
    )

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        return " Error obteniendo token"

    update_user_token(phone, access_token)
    delete_state(state)

    print(f" Usuario {phone} conectó Notion")

    return " Notion conectado! Volvé a WhatsApp"


if __name__ == "__main__":
    threading.Thread(target=run_scheduler).start()
    app.run(port=5000)