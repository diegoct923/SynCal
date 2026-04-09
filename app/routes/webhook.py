from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from app.utils.parser import parse_message
from app.services.service import create_user_task
from app.storage.task_store import get_tasks
from app.storage.user_store import (
    has_notion_connected,
    create_user_if_not_exists
)
from app.storage.auth_store import save_state
from app.utils.helpers import generate_state
from config.config import BASE_URL
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")


def webhook():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")

    print(f"Mensaje de {sender}: {incoming_msg}")

    create_user_if_not_exists(sender)

    command = parse_message(incoming_msg)
    response = MessagingResponse()

    # =========================
    # ADD
    # =========================
    if command["type"] == "ADD":

        if not has_notion_connected(sender):
            response.message("Primero conectá tu Notion con 'Conectar Notion'")
            return str(response)

        result = create_user_task(sender, command["task"], command["date"], command["priority"])

        if result:
            response.message(" Tarea creada en Notion")
        else:
            response.message(" Error creando tarea")

    # =========================
    # LIST
    # =========================
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

    # =========================
    # CONNECT NOTION
    # =========================
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

    elif command["type"] == "ERROR":
        response.message(command["message"])


    else:
        response.message(
            "No entendí el comando.\n"
            "Usá:\n"
            "- Añadir Parcial/Entrega Nombre Fecha\n"
            "- Ver tareas\n"
            "- Conectar Notion"
        )

    return str(response)