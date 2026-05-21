import uuid

def generate_state():
    return str(uuid.uuid4())

def fmt(hora: float) -> str:
    """Convierte 8.5 → '08:30', 13.0 → '13:00'"""
    h = int(hora)
    m = int(round((hora - h) * 60))
    return f"{h:02d}:{m:02d}"

