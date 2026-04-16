from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from app.utils.parser import parse_task_data, parse_intent
from app.services.service import create_user_task
from app.storage.task_store import get_tasks
from app.storage.user_store import (
    create_user_if_not_exists
)
from config.config import BASE_URL
import os
from app.utils.state import generar_state
from app.storage.sesiones import guardar_state
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")


def webhook():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")
    phone = sender.split(':+') #type: ignore
    tel = phone[1]
    
    state = generar_state()
    guardar_state(state, tel)

    print(f"Mensaje de {tel}: {incoming_msg}")

    create_user_if_not_exists(phone[1])

    intent = parse_intent(incoming_msg) #ADD, LIST, UNKNOWN

    response = MessagingResponse()

    
    # ADD
    
    if intent["type"] == "ADD":
        task = parse_task_data(incoming_msg)

        if not task["ok"]:
            response.message("No pude crear la tarea: " + task["error"]," " + task["message"])
            return str(response)

        result = create_user_task(tel, task["data"]["tipo"], task["data"]["title"], task["data"]["deadline"])

        if result["status"]=="inserted":
            response.message("Tarea creada")
        elif result["status"]=="duplicate":
            response.message("Tarea duplicada, no se añadió")
        else:
            response.message("Error creando tarea")

    
    # LIST
    
    elif intent["type"] == "LIST":
        tasks = get_tasks(tel)
        tasks = [t for t in tasks if t["phone"] == tel]

        if not tasks:
            response.message("No tenés tareas aún")
        else:
            msg = "Tus tareas:\n"
            for t in tasks:
                msg += f"- {t['tipo']} {t['title']} ({t['deadline']})\n"

            response.message(msg)

    elif intent["type"] == "CALENDAR":
        link= f"{BASE_URL}/calendar?state={state}"        
        response.message(f" Acá tenés tu calendario:\n{link}")    

    elif intent["type"] == "UNKNOWN":
        response.message(
            "No entendí el comando.\n"
            "Usá:\n"
            "- Añadir Tarea, Nombre, Fecha"
            "- Ver tareas\n"
        )

    return str(response)