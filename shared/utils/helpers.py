from shared.storage.sesiones import obtener_telefono_por_state
import uuid


def generate_state():
    return str(uuid.uuid4())

def fmt(hora: float) -> str:
    """Convierte 8.5 → '08:30', 13.0 → '13:00'"""
    h = int(hora)
    m = int(round((hora - h) * 60))
    return f"{h:02d}:{m:02d}"

def get_user_tel_from_state(state):
    if not state:
        return None, "missing state"
    tel = obtener_telefono_por_state(state)
    if not tel:
        return None, "unauthorized"
    return tel, None
