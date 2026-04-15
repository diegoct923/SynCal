from datetime import datetime

def validate_date(date_str):
    if date_str is None:
        return None

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except:
        return None


def parse_message(message):
    message = message.strip().lower()
    parts = message.split(" ")

    #VER TAREAS
    if message in ["ver tareas", "listar", "list"]:
        return {"type": "LIST"}

    #AÑADIR
    if len(parts) >= 4 and parts[0] == "añadir":
        
        #validar fecha por aca 
        
        return {
            "type": "ADD",     #parts[0]
            "tipo": parts[1],  #ej: parcial, entrega, practico
            "title": parts[2], #ej: redes, matematicas...
            "date": parts[3]   #en formato aaaa/mm/dd 
        }


    return {"type": "UNKNOWN"}