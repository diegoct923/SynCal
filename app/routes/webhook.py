import os
from flask import request
from datetime import datetime, date
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from app.services.service import create_user_task, complete_task, delete_task, reagendar_user_task
from app.storage.task_store import get_tasks, get_tasks_day, get_tasks_to_complete, reagendar_tarea
from app.storage.user_store import create_user_if_not_exists
from config.config import BASE_URL
from app.utils.state import generar_state
from app.utils.parser import parse_task_data, parse_intent, parsear_con_llm, extract_date, extract_time
from app.storage.sesiones import guardar_state
from app.storage.conversacion import obtener_contexto, limpiar_contexto, guardar_contexto
from app.utils.helpers import fmt

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
    


    #Contexto Completar Tarea
    if contexto == "id_tarea_completar":
        task_id = incoming_msg.strip() #type: ignore
        
        if not task_id.isdigit():
            response.message("Por favor respondé con el número de la tarea.")
            return str(response)

        result = complete_task(int(task_id), tel)  

        if result["status"] == "completed":
            #eliminar tarea
            response.message("Tarea marcada como completada.")
        elif result["status"] == "not_found":
            response.message("No encontré esa tarea.")
        else:
            response.message("Error al completar la tarea.")

        limpiar_contexto(tel)  #limpiar contexto al terminar conversación
        return str(response)
    


    #Contexto Reagendar Tarea
    if contexto == "id_tarea_mover":
        message= incoming_msg.strip() #type: ignore 
        parts = message.split(sep=",") #type: ignore
        task_id = parts[0]
        date=extract_date(parts[1])
        time=extract_time(parts[1])

        if not task_id.isdigit():
            response.message("Por favor responda con el número de la tarea.")
            return str(response)
        
        if  date is None:
            response.message("Por favor incluya una fecha válida.")
            return str(response)
        deadline = datetime.combine(date, time) if time else date
        if deadline < date.today(): #si la fecha es anterior al día del registro, no se registra 
            jason={
            "ok": False,
            "error": "EXPIRED DATE",
            "message": "La fecha ingresada es anterior al día del registro."
            }
            response.message(f"Ocurrió un error con la fecha: {jason['error']}, {jason['message']}")
            return str(response)

        result = reagendar_user_task(task_id, deadline, tel)
        if result["status"] == "not_found":
            response.message("No encontré esa tarea.")
        else:
            msg = "Tarea reagendada"
            sesiones = result.get("sesiones", [])
            if sesiones:
                msg += "\n\nNuevas sesiones de estudio:"
                for s in sesiones:
                    if len(s["tramos"]) == 1:
                        ini, fin = s["tramos"][0]
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} - {fmt(ini)} a {fmt(fin)}"
                    else:
                        tramos_str = " + ".join(f"{fmt(i)} a {fmt(f)}" for i, f in s["tramos"])
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} - {tramos_str}"
            response.message(msg)
        limpiar_contexto(tel)
        return str(response)



    #Contexto eliminar tarea
    if contexto == "id_tarea_eliminar":
        task_id = incoming_msg.strip() #type: ignore

        if not task_id.isdigit():
            response.message("Por favor respondé con el número de la tarea.")
            return str(response)

        res = delete_task(task_id, tel)
        if res["status"] == "deleted":
            response.message("Tarea eliminada con exito.")
        elif res["status"] == "not_found":
            response.message("No se encontró la tarea.")
        else:
            response.message("Error al eliminar la tarea.")

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

        if result["status"] == "inserted":
            msg = "Tarea creada"

            sesiones = result.get("sesiones", [])
            if sesiones:
                msg += "\n\nSesiones de estudio agendadas:"
                for s in sesiones:
                    if len(s["tramos"]) == 1:
                        # Sesión continua
                        ini, fin = s["tramos"][0]
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {fmt(ini)} a {fmt(fin)}"
                    else:
                        # Sesión partida en varios tramos
                        tramos_str = " + ".join(f"{fmt(i)} a {fmt(f)}" for i, f in s["tramos"])
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {tramos_str}"
            response.message(msg)   

        elif result["status"]=="duplicate":
            response.message("Tarea duplicada, no se añadió")

        elif result["status"]=="overlap":
            response.message(f"Error al añadir tarea, ya hay una tarea existente en el horario ingresado:\nID:{result['id']}, TAREA:{result['nombre']}, FECHA:{result['deadline']} ")
        
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
    
    
    #MULTI
    
    elif intent["type"] == "MULTI":
        result = parsear_con_llm(incoming_msg)
    
        if not result["ok"]:
            response.message(result["message"])
        else:
            confirmaciones = []
            errores = []
            for tarea in result["data"]:
                if not tarea["deadline"]:
                    errores.append(f" '{tarea['titulo']}' no tiene fecha, no se guardó.")
                    continue
            
                db_result = create_user_task(tel, tarea["tipo"], tarea["titulo"], tarea["deadline"])
                print(f"DB RESULT: {db_result}")

                if result["status"] == "inserted":
                    msg = "Tarea creada"

                    sesiones = result.get("sesiones", [])
                    if sesiones:
                        msg += "\n\nSesiones de estudio agendadas:"
                        for s in sesiones:
                            if len(s["tramos"]) == 1:
                                # Sesión continua
                                ini, fin = s["tramos"][0]
                                msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {fmt(ini)} a {fmt(fin)}"
                            else:
                                # Sesión partida en varios tramos
                                tramos_str = " + ".join(f"{fmt(i)} a {fmt(f)}" for i, f in s["tramos"])
                                msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {tramos_str}"
                    response.message(msg)       
                
                elif db_result["status"] == "duplicate":
                    errores.append(f" '{tarea['titulo']}' ya existe, no se añadió.")
                    
                else:
                    errores.append(f" '{tarea['titulo']}' error al guardar.")
        
            if confirmaciones:
                response.message("Tareas agregadas correctamente:\n" + "\n".join(confirmaciones))
            if errores:
                response.message("Hubo algunos problemas:\n" + "\n".join(errores))
            

    
    # COMPLETE

    elif intent["type"] == "COMPLETE":
        tasks = get_tasks_to_complete(tel)
        if not tasks:
            response.message("No tenés tareas aún.")
        else:
            msg = "¿Cuál tarea querés completar? Respondé con el número de la tarea:\n"
            for t in tasks:
                msg += f"{t['id']} - {t['tipo']} {t['title']} ({t['deadline']})\n"
            
            guardar_contexto(tel, "id_tarea_completar")  # ← guardar que esperamos ID
            response.message(msg)

    #MOVE_TASK

    elif intent["type"] == "MOVE_TASK":
        tasks = get_tasks_to_complete(tel)
        if not tasks:
            response.message("No tenés tareas aún.")
        else:
            msg = "¿Cuál tarea querés reagendar? Respondé de la siguiente manera  '(numero de tarea) , (nueva fecha)':\n"
            for t in tasks:
                msg += f"{t['id']} - {t['tipo']} {t['title']} ({t['deadline']})\n"
            
            guardar_contexto(tel, "id_tarea_mover")  # ← guardar que esperamos ID
            response.message(msg)

    #DELETE
    elif intent["type"] == "DELETE":
        tasks = get_tasks_to_complete(tel)
        if not tasks:
            response.message("No tenés tareas aún.")
        else:
            msg = "¿Cuál tarea querés eliminar? Respondé con el número de la tarea:\n"
            for t in tasks: 
                msg += f"{t['id']} - {t['tipo']} {t['title']} ({t['deadline']})\n"
            
            guardar_contexto(tel, "id_tarea_eliminar")
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