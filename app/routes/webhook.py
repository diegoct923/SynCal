from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from app.utils.parser import parse_task_data, parse_intent
from app.services.service import create_user_task, complete_task
from app.storage.task_store import get_tasks, get_tasks_day, get_tasks_to_complete
from app.storage.user_store import (
    create_user_if_not_exists
)
from config.config import BASE_URL
import os
from app.utils.state import generar_state
from app.storage.sesiones import guardar_state
from app.storage.conversacion import obtener_contexto, limpiar_contexto, guardar_contexto
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

    response = MessagingResponse()
 
    contexto = obtener_contexto(tel) #chequear contexto pendiente antes de parse intent

    if contexto == "id_tarea_completar":
        task_id = incoming_msg.strip() #type: ignore
        
        if not task_id.isdigit():
            response.message("Por favor respondé con el número de la tarea.")
            return str(response)

        result = complete_task(tel, int(task_id))  

        if result["status"] == "completed":
            response.message("Tarea marcada como completada.")
        elif result["status"] == "not_found":
            response.message("No encontré esa tarea.")
        else:
            response.message("Error al completar la tarea.")

        limpiar_contexto(tel)  #limpiar contexto al terminar conversación
        return str(response)


    intent = parse_intent(incoming_msg) #ADD, LIST, UNKNOWN

    
    # ADD
    
    if intent["type"] == "ADD":
        task = parse_task_data(incoming_msg)

        if not task["ok"]:
            response.message(f"No pude crear la tarea: {task['error']}. {task['message']}")
            return str(response)

        result = create_user_task(tel, task["data"]["tipo"], task["data"]["title"], task["data"]["deadline"]) #devuelve json: {"status": "inserted", "id": "id_tarea"}

        if result["status"]=="inserted":
            response.message("Tarea creada")
        elif result["status"]=="duplicate":
            response.message("Tarea duplicada, no se añadió")
        else:
            response.message("Error creando tarea")

    
    # LIST
    
    elif intent["type"] == "LIST":
        tasks = get_tasks(tel)

        if not tasks:
            response.message("No tenés tareas aún")
        else:
            msg = "Tus tareas:\n"
            for t in tasks:
                msg += f"- {t['tipo']} {t['title']} ({t['deadline']}) - {t['status']}\n"

            response.message(msg)

    # LIST_DAY
    elif intent["type"] == "LIST_DAY":
        tasks = get_tasks_day(tel)

        if not tasks:
            response.message("No tenés tareas hoy.")
        else:
            msg = "Tus tareas de hoy:\n"
            for t in tasks:
                deadline = t['deadline']
                time_str = deadline.strftime("%H:%M") if deadline.hour or deadline.minute else "Sin hora registrada"
                msg += f"- {t['tipo']} {t['title']} ({time_str}) - {t['status']}\n"

            response.message(msg)

    # CALENDAR

    elif intent["type"] == "CALENDAR":
        link= f"{BASE_URL}/calendar?state={state}"        
        response.message(f" Acá tenés tu calendario:\n{link}")    
    
    # COMPLETE

    elif intent["type"] == "COMPLETE":
        tasks = get_tasks_to_complete(tel)
        if not tasks:
            response.message("No tenés tareas aún.")
        else:
            msg = "¿Cuál tarea querés completar? Respondé con el número:\n"
            for t in tasks:
                msg += f"{t['id']} - {t['tipo']} {t['title']} ({t['deadline']})\n"
            
            guardar_contexto(tel, "id_tarea_completar")  # ← guardar que esperamos ID
            response.message(msg)

    # UNKNOWN

    elif intent["type"] == "UNKNOWN":
        response.message(
            "No entendí el comando.\n"
            "Usá:\n"
            "- Añadir Tarea, Nombre, Fecha"
            "- Ver tareas\n"
        )

    return str(response)