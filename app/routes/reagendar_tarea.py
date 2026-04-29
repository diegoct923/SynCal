from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from app.storage.task_store import reagendar_tarea



response = MessagingResponse()



def reagendar_tarea_route():
    data = request.get_json()
    task_id = data['task_id']
    deadline = data['deadline']
    
    success = reagendar_tarea(task_id, deadline)
    response.message("Tarea Reagendada con éxito.")
    
    return str(response)