from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from app.utils.parser import parse_message
from app.services.service import create_user_task
from app.storage.task_store import get_tasks
from app.storage.user_store import (
    create_user_if_not_exists
)
from config.config import BASE_URL
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")


def webhook():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")
    phone = sender.split(':+') #type: ignore
    tel = phone[1]

    print(f"Mensaje de {tel}: {incoming_msg}")

    create_user_if_not_exists(phone[1])

    command = parse_message(incoming_msg)
    response = MessagingResponse()

    
    # ADD
    
    if command["type"] == "ADD":

        result = create_user_task(tel, command["tipo"], command["title"], command["date"])

        if result:
            response.message("Tarea creada")
        else:
            response.message(" Error creando tarea")

    
    # LIST
    
    elif command["type"] == "LIST":
        tasks = get_tasks(tel)
        tasks = [t for t in tasks if t["phone"] == tel]

        if not tasks:
            response.message("No tenés tareas aún")
        else:
            msg = "Tus tareas:\n"
            for t in tasks:
                msg += f"- {t['tipo']} {t['title']} ({t['date']})\n"

            response.message(msg)

    elif command["type"] == "ERROR":
        response.message(command["message"])


    elif command["type"] == "UNKNOWN":
        response.message(
            "No entendí el comando.\n"
            "Usá:\n"
            "- Añadir Parcial/Entrega Nombre Fecha\n"
            "- Ver tareas\n"
            "- Conectar Notion"
        )

    return str(response)