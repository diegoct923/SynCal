from datetime import datetime


def format_date(date_str):
    try:
        # formato: 25-04-2026
        if len(date_str.split("-")) == 3:
            dt = datetime.strptime(date_str, "%d-%m-%Y")

        # formato: 25-04 → asume año actual
        elif len(date_str.split("-")) == 2:
            dt = datetime.strptime(date_str, "%d-%m")
            dt = dt.replace(year=datetime.now().year)

        else:
            return None

        return dt.strftime("%Y-%m-%d")  # ISO 8601

    except:
        return None


def parse_message(message):
    message = message.strip().lower()
    parts = message.split()

    # 🔗 CONECTAR NOTION
    if message in ["conectar notion", "notion", "login notion"]:
        return {"type": "CONNECT_NOTION"}

    # 📋 VER TAREAS
    if message in ["ver tareas", "listar", "list"]:
        return {"type": "LIST"}

    # ➕ AÑADIR TAREA
    if len(parts) >= 4 and parts[0] == "añadir":
        category = parts[1]

        title = " ".join(parts[2:-1])
        raw_date = parts[-1]

        formatted_date = format_date(raw_date)

        if not formatted_date:
            return {
                "type": "ERROR",
                "message": " Fecha inválida. Usá formato 25-04 o 25-04-2026"
            }

        return {
            "type": "ADD",
            "category": category,
            "title": title,
            "date": formatted_date  #  ya listo para Notion
        }

    return {"type": "UNKNOWN"}