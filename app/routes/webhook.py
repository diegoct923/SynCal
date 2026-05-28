import os
from flask import request
from datetime import datetime, date, time
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from app.services.service import create_user_task, complete_task, delete_task, reagendar_user_task
from app.storage.grupo_store import crear_grupo, get_grupos_usuario, save_group_task
from app.storage.task_store import get_tasks, get_tasks_day, get_tasks_to_complete
from app.storage.user_store import create_user_if_not_exists, set_minutos_anticipacion_to_notify        
from config.config import BASE_URL
from app.utils.state import generar_state
from app.utils.parser import parse_task_data, parse_intent, parsear_con_llm, parse_grupo_data, parse_anticipacion, extract_date, extract_time
from app.storage.sesiones import guardar_state
from app.storage.conversacion import obtener_contexto, limpiar_contexto, guardar_contexto
from app.utils.helpers import fmt
from textwrap import dedent


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")

HELP = dedent("""
    👋 ¡Hola! Soy WiCal, tu asistente de tareas universitarias.

    Para agregar una tarea escribí:
    añadir [tipo] [nombre] [fecha]
    ✏️ Ej: añadir parcial Cálculo 15/06
    📚 Tipos: parcial · examen · tarea · entrega · actividad · práctico · deber · lectura
    ─────────────────
    📋 Ver tareas → ver tareas
    📅 Ver tareas de hoy → ver tareas hoy
    🗓️ Calendario → ver calendario
    ✅ Completar → completar tarea
    🗑️ Eliminar → eliminar tarea
    📆 Reagendar → reagendar tarea
    ─────────────────
    ➕ Varias a la vez:
    !multi
    añadir parcial Cálculo 15/06
    añadir entrega Informe 20/06
    ─────────────────
    👥 Grupos:
    Crear grupo → crear grupo [nombre], integrantes: user1, user2
    ✏️ Ej: crear grupo Redes 2, integrantes: santi, diego

    📌 Tarea grupal → añadir tarea grupal [tipo] [nombre] [fecha]
    ✏️ Ej: añadir tarea grupal parcial Cálculo 15/06 a las 16:00
    (el sistema verifica que todos tengan ese horario libre) 
    ─────────────────
    🔔 Recordatorios:
    Recibís un resumen diario a las 8:00 AM con tus tareas y sesiones del día.
    También te avisamos antes de cada tarea o sesión.
    Para configurar con cuánta anticipación:
    → configurar anticipación [minutos] minutos
    ✏️ Ej: configurar anticipación 30 minutos
    (mínimo 5 min · máximo 120 min · default 15 min)
""").strip()



def webhook():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")
    phone = sender.split(':+') #type: ignore
    tel = phone[1]
    
    state = generar_state() 
    guardar_state(state, tel)

    print(f"Mensaje de {tel}: {incoming_msg}")

    user_data = create_user_if_not_exists(phone[1])

    response = MessagingResponse()

    # envío de manual de uso
    if user_data["es_nuevo"]:
        response.message(HELP)
        return str(response)
    

    contexto, datos_contexto = obtener_contexto(tel) #chequear contexto pendiente antes de parse intent
    


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
        fecha=extract_date(parts[1])
        hora=extract_time(parts[1])

        if not task_id.isdigit():
            response.message("Por favor responda con el número de la tarea.")
            return str(response)
        
        if  fecha is None:
            response.message("Por favor incluya una fecha válida.")
            return str(response)
        deadline = datetime.combine(fecha, hora) if hora else datetime.combine(fecha, time.min)
        if deadline.date() < date.today(): #si la fecha es anterior al día del registro, no se registra 
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
                    if len(s["tramos"]) == 1: #type: ignore
                        ini, fin = s["tramos"][0] #type: ignore
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} - {fmt(ini)} a {fmt(fin)}" #type: ignore
                    else:
                        tramos_str = " + ".join(f"{fmt(i)} a {fmt(f)}" for i, f in s["tramos"]) #type: ignore
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} - {tramos_str}" #type: ignore
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
    

    #contexto tarea grupal
    
    if contexto == "elegir_grupo_tarea":
        opcion = incoming_msg.strip()       #type:ignore

        if not opcion.isdigit():
            response.message("Por favor respondé con el número del grupo.")
            return str(response)

        
        grupos = get_grupos_usuario(tel)

        indice = int(opcion) - 1
        if indice < 0 or indice >= len(grupos):
            response.message("Número inválido. Respondé con uno de los números de la lista.")
            return str(response)

        grupo = grupos[indice]

        # Solo el creador puede agregar tareas
        if grupo["creador_tel"] != tel:
            limpiar_contexto(tel)
            response.message(f"Solo el creador del grupo '{grupo['nombre']}' puede agregar tareas.")
            return str(response)

        result = save_group_task(
            grupo_id=grupo["id"],
            tipo=datos_contexto["tipo"],            #type:ignore
            title=datos_contexto["title"],          #type:ignore
            deadline=datos_contexto["deadline"],    #type:ignore
            creador_tel=tel
        )

        limpiar_contexto(tel)

        if result["status"] == "inserted":
            response.message(f"Tarea '{datos_contexto['title']}' agregada al grupo {grupo['nombre']} ")     #type:ignore    
        elif result["status"] == "no_disponible":
            if result["sugerencia_fecha"]:
                response.message(
                    f"No todos los integrantes tienen ese horario libre. "
                    f"El próximo hueco disponible para todos es el {result['sugerencia_fecha']} a las {result['sugerencia_hora']}."
                )
            else:
                response.message("No todos los integrantes tienen ese horario libre y no se encontró un hueco común en los próximos 14 días.")
        elif result["status"] == "duplicate":
            response.message("Esa tarea ya existe en el grupo.")
        else:
            response.message("Error al crear la tarea grupal.")

        return str(response)           



        

       
    intent = parse_intent(incoming_msg) #ADD, LIST, UNKNOWN

    # HELP
    if intent["type"] == "HELP":
        response.message(HELP)
        return str(response)


    
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
                    if len(s["tramos"]) == 1: #type: ignore
                        # Sesión continua
                        ini, fin = s["tramos"][0] #type: ignore
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {fmt(ini)} a {fmt(fin)}" #type: ignore
                    else:
                        # Sesión partida en varios tramos
                        tramos_str = " + ".join(f"{fmt(i)} a {fmt(f)}" for i, f in s["tramos"]) #type: ignore
                        msg += f"\n• {s['fecha'].strftime('%a %d/%m')} — {tramos_str}" #type: ignore
            response.message(msg)   

        elif result["status"]=="duplicate":
            response.message("Tarea duplicada, no se añadió")

        elif result["status"]=="overlap":
            response.message(f"Error al añadir tarea, ya hay una tarea existente en el horario ingresado:\nID:{result['id']}, TAREA:{result['nombre']}, FECHA:{result['deadline']} ")
        
        else:
            response.message("Error creando tarea")

    
    # LIST
    
    elif intent["type"] == "LIST":
        print("Entra a list")
        tasks = get_tasks(tel)
        print("sale get_task", tasks)
    
        if not tasks:
            response.message("No tenés tareas aún")
            print("no tasks")
        else:
            msg = "Tus tareas:\n"
            for t in tasks:
                msg += f"- {t['tipo']} {t['title']} ({t['deadline']}) - {t['status']}\n"

            response.message(msg)
            print("Formula respuesta: ", msg)

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
            
            guardar_contexto(tel, "id_tarea_completar", None)  # ← guardar que esperamos ID
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
            
            guardar_contexto(tel, "id_tarea_mover", None)  # ← guardar que esperamos ID
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
            
            guardar_contexto(tel, "id_tarea_eliminar", None)
            response.message(msg)
    
    #CREW
    elif intent["type"] == "CREW":  
        parsed = parse_grupo_data(incoming_msg)

        if not parsed["ok"]:
            response.message(f"No pude crear el grupo: {parsed['error']}")
            return str(response)

        result = crear_grupo(
            nombre=parsed["data"]["nombre"],
            creador_tel=tel,
            usernames=parsed["data"]["usernames"]
        )

        if result["status"] == "error":
            response.message(f"No se pudo crear el grupo. {result['message']}")
        else:
            integrantes_str = ", ".join(parsed["data"]["usernames"])
            response.message(
                f"Grupo '{result['nombre']}' creado \n"
                f"Integrantes: {integrantes_str}"
            )
    


    #ADD GROUP TASK
    elif intent["type"] == "ADD_GROUP_TASK":
        task = parse_task_data(incoming_msg)
        if not task["ok"]:
            response.message(f"No pude entender la tarea: {task['error']}. {task['message']}")
            return str(response)

        #obtener grupos del usuario
        grupos = get_grupos_usuario(tel)        
        if not grupos:
            response.message("No pertenecés a ningún grupo todavía.")
            return str(response)

        #guardar contexto con los datos de la tarea
        guardar_contexto(tel, "elegir_grupo_tarea", datos=task["data"])

        msg = "¿A qué grupo querés agregar la tarea? Respondé con el número:\n"
        for i, g in enumerate(grupos, 1):
            msg += f"{i} - {g['nombre']}\n"

        response.message(msg)   



    elif intent["type"] == "SET_ANTICIPACION_NOTIFICACIONES":
        
        parsed = parse_anticipacion(incoming_msg)
        if not parsed["ok"]:
            response.message(f"No pude configurar la anticipación: {parsed['error']}")
        else:
            minutos = parsed["data"]["minutos"]
            set_minutos_anticipacion_to_notify(tel, minutos)
            response.message(f"Está bien, te voy a avisar {minutos} minutos antes de cada tarea y sesión.") 



    # UNKNOWN
    elif intent["type"] == "UNKNOWN":
        msg = dedent("""
            No entendí el comando.
            
            Para agregar una tarea escribí:
            añadir [tipo] [nombre] [fecha]

            ✏️ Ej: añadir parcial Cálculo 15/06

            📚 Tipos:
            parcial · examen · tarea · entrega · actividad · práctico · deber · lectura
            ─────────────────
            📋 Ver tareas → ver tareas
            📅 Ver tareas de hoy → ver tareas hoy
            🗓️ Calendario → ver calendario
            ✅ Completar → completar tarea
            🗑️ Eliminar → eliminar tarea
            📆 Reagendar → reagendar tarea
            ─────────────────
            ➕ Varias a la vez:
            !multi
            añadir parcial Cálculo 15/06
            añadir entrega Informe 20/06
            ─────────────────
            🔔 Recordatorios:
            Recibís un resumen diario a las 8:00 AM con tus tareas y sesiones del día.
            También te avisamos antes de cada tarea o sesión.
            Para configurar con cuánta anticipación:
            → configurar anticipación [minutos] minutos
            ✏️ Ej: configurar anticipación 30 minutos
            (mínimo 5 min · máximo 120 min · default 15 min)        
        """).strip()

        response.message(msg)
    return str(response)    