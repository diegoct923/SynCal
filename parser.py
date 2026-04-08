
def parse_message(message):
    message = message.strip().lower()
    parts = message.split()

    #  CONECTAR NOTION
   
    if message in ["conectar notion", "notion", "login notion"]:
        return {"type": "CONNECT_NOTION"}

    #  VER TAREAS
    
    if message in ["ver tareas", "listar", "list"]:
        return {"type": "LIST"}

    #  AÑADIR TAREA
   
    if len(parts) >= 4 and parts[0] == "añadir":
        category = parts[1]

        #  soporta títulos con espacios
        title = " ".join(parts[2:-1])
        date = parts[-1]

        return {
            "type": "ADD",
            "category": category,
            "title": title,
            "date": date
        }

  
    #  DESCONOCIDO

    return {"type": "UNKNOWN"}