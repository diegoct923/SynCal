from datetime import datetime
from app.integrations.openai import parse_message_ia


def validate_date(date_str):
    if date_str is None:
        return None

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except:
        return None


def parse_message(message: str) -> dict:
    result = parse_message_ia(message)

    if not isinstance(result, dict):
        return {
            "type": "ERROR",
            "message": "Invalid response type"
        }

    if result.get("type") == "ERROR":
        return {
            "type": "ERROR",
            "message": "No se pudo interpretar el mensaje"
        }

    date = validate_date(result.get("date"))

    if result.get("date") is not None and date is None:
        return {
            "type": "ERROR",
            "message": "Invalid date format",
            "data": result
        }

    result["date"] = date

    return result