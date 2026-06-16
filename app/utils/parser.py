import re
import unicodedata
import json
from datetime import datetime, date, time 
import dateparser
from app.integrations.llm_haiku import call_haiku



SYSTEM_PROMPT = """
Eres un parser de tareas académicas. Del mensaje del usuario extrae TODAS las tareas mencionadas.
- Si tiene hora: "YYYY-MM-DDTHH:MM"
- Si no tiene hora: "YYYY-MM-DD"
Devuelve SOLO un JSON válido sin texto adicional, con este formato:
{{
  "tareas": [
    {{
      "titulo": "nombre limpio de la tarea",
      "tipo": "EXAMEN|TAREA|PRACTICO|UNKNOWN",
      "deadline": "YYYY-MM-DDHH:MM o null",
    }}
  ]
}}
"""


def parsear_con_llm(msg):
    prompt = SYSTEM_PROMPT.format(today=date.today().isoformat())
    raw = call_haiku(prompt, msg)

    print(f"RAW LLM RESPONSE: {repr(raw)}")  # temporal para debug
    
    # limpiar backticks si los hay
    raw = raw.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'```$', '', raw)
    raw = raw.strip()



    tareas = json.loads(raw)["tareas"]

    if not tareas:
        return {
            "ok": False,
            "error": "NO_TASKS",
            "message": "No se encontraron tareas válidas."
        }

    return {
        "ok": True,
        "data": tareas
    }
    

#tipos de tareas
TYPE_KEYWORDS = { 
    "EXAMEN": ["parcial", "examen"],
    "TAREA": ["tarea", "entrega", "deber", "presentacion"],
    "PRACTICO": ["practico", "repartido", "lectura", "leer", "ejercicios", "ejercicio", "actividad"],
}

# Normalizar texto

def normalize(text: str) -> str:
    text = text.lower().strip()

    # sacar tildes
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    return text



# Sacar tipo de tarea

def detect_tipo(text: str) -> str:
    for t, words in TYPE_KEYWORDS.items():
        for w in words:
            if w in text:
                return t
    return "UNKNOWN"


#Extraer fecha  

def extract_date(text: str):
    patterns = [
        r'\b\d{4}[/-]\d{2}[/-]\d{2}\b',

        r'\b(?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)\s+\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',

        r'\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',

        r'(?<!\d)\b\d{1,2}[/-]\d{1,2}\b(?!\d)',

        r'\b(hoy|manana|pasado manana)\b',

        r'\b(?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)\s+\d{1,2}\b',

        r'\b(lunes|martes|miercoles|jueves|viernes|sabado|domingo)\b'
    ]

    candidatos = []

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if isinstance(m, tuple):
                m = " ".join(m)

            candidatos.append(m)

    for candidato in candidatos:
        iso_match = re.fullmatch(r'(\d{4})[/-](\d{2})[/-](\d{2})', candidato)
        if iso_match:
            try:
                return datetime(
                    int(iso_match.group(1)),
                    int(iso_match.group(2)),
                    int(iso_match.group(3))
                ).date()
            except ValueError:
                continue

        # Caso: "jueves 18"
        weekday_day_match = re.fullmatch(
            r'(lunes|martes|miercoles|jueves|viernes|sabado|domingo)\s+(\d{1,2})',
            candidato
        )

        if weekday_day_match:
            day = int(weekday_day_match.group(2))
            today = date.today()

            for month_offset in range(13):
                month = today.month + month_offset
                year = today.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1

                try:
                    candidate_date = date(year, month, day)
                except ValueError:
                    continue

                if candidate_date >= today:
                    return candidate_date

        parsed_date = dateparser.parse(
            candidato,
            languages=["es"],
            settings={"RELATIVE_BASE": datetime.now()}
        )

        if parsed_date:
            return parsed_date.date()

    return None

#extraer hora

def extract_time(text: str):
    patterns = [
        # "a las 18:30" o "a las 6:30pm"
        r'\ba\s+las\s+\d{1,2}:\d{2}(?:\s*[ap]m)?\b',
        # "18:30pm" o "6:30 am"
        r'\b\d{1,2}:\d{2}(?:\s*[ap]m)?\b',
        # "18h30"
        r'\b\d{1,2}h\d{2}\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw = match.group()

            # normalizar: sacar "a las", espacios
            raw = re.sub(r'^a\s+las\s+', '', raw).strip()
            raw = re.sub(r'(\d)h(\d)', r'\1:\2', raw)# "18h30" -> "18:30"

            parsed = dateparser.parse(raw, languages=["es"], settings={"RELATIVE_BASE": datetime.now()})
            if parsed:
                return parsed.time()

    return None


#limpiar nombre de tarea 

def clean_task_title(text: str) -> str:
   # remover conectores comunes
    
    noise_words = [
        "para", "el", "la", "los", "las",
        "del", "con", "por", "antes","a",
        "hacer", "tengo", "que", "agregar", 
        "anadir", "crear", "parcial", "entrega", "de", "listar"
    ]
       

    # noise words
    for word in noise_words:
        text = re.sub(rf'\b{word}\b', '', text)
    
    text = re.sub(r'\s+', ' ', text).strip() #normalizar
   
    #remover horas
    text = re.sub(r'\ba\s+las\s+\d{1,2}:\d{2}(?:\s*[ap]m)?\b', '', text)
    text = re.sub(r'\b\d{1,2}:\d{2}(?:\s*[ap]m)?\b', '', text)
    text = re.sub(r'\b\d{1,2}h\d{2}\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip() 

    #remover iso 8601, antes que el patrón corto
    text = re.sub(r'\b\d{4}[/-]\d{2}[/-]\d{2}\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    #remover fechas cortas 
    text = re.sub(r'(?<!\d)\b\d{1,2}[/-]\d{1,2}\b(?!\d)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    
    # remover días y relativos
    text = re.sub(r'(lunes|martes|miercoles|jueves|viernes|sabado|domingo|hoy|manana|pasado manana)','',text)
    text = re.sub(r'\s+', ' ', text).strip() #normalizar
    

    # fechas tipo "23 abril"
    text = re.sub(
        r'\b\d{1,2}\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
        '',
        text
    )
    text = re.sub(r'\s+', ' ', text).strip() #normalizar 
    

    # remover keywords de tipo
    for words in TYPE_KEYWORDS.values():
        for w in words:
            text = text.replace(w, "")
    text = re.sub(r'\s+', ' ', text).strip() #normalizar
     
    return text


#parsear intención
def parse_intent(text) -> dict:
    text = text.lower()
    text = normalize(text)

    if any(x in text for x in ["/ayuda"]):
        return {"type": "HELP"}
    if any(x in text for x in ["!multi"]):
        return {"type": "MULTI"}
    
    if any(x in text for x in ["actualizar", "reagendar", "cambiar", "mover"]):
        return {"type": "MOVE_TASK"}
        
    if any(x in text for x in ["tarea grupal", "añadir grupal", "agregar grupal"]):
        return {"type": "ADD_GROUP_TASK"}

    if any(x in text for x in ["agregar", "anadir", "añadir", "parcial", "entrega", "hacer", "tengo", "examen"]):
        return {"type": "ADD"}

    if any(x in text for x in ["ver tareas del día", "ver tareas del dia", "mis tareas de hoy", "listar tareas hoy", "listar tareas del dia", "listar tareas del día", "ver tareas hoy", "ver tareas de hoy"]):
        return {"type": "LIST_DAY"}

    if any(x in text for x in ["ver tareas", "mis tareas", "listar", "listar tareas"]):
        return {"type": "LIST"}

    if any(x in text for x in ["ver calendario", "mi calendario", "calendario", "mostrar calendario"]):
        return {"type": "CALENDAR"}
    
    if any(x in text for x in ["completar tarea", "completar tareas", "completar", "marcar tarea completada", "marcar tareas completadas", "finalizar tarea" ]):
        return {"type": "COMPLETE"}

    if any(x in text for x in ["eliminar tarea", "eliminar tareas", "eliminar", "borrar tarea", "borrar tareas", "sacar tarea" ]):
        return {"type": "DELETE"}

    if any(x in text for x in ["crear grupo", "armar grupo", "nuevo grupo", "formar grupo", "materializar grupo", "haya grupo" ]):
        return {"type": "CREW"}

    if any(x in text for x in ["configurar anticipación", "configurar notificaciones", "anticipacion de recordatorio", "configurar anticipacion de recordatorio", "anticipacion", "configurar recordatorio"]):
        return {"type": "SET_ANTICIPACION_NOTIFICACIONES"}

    return {"type": "UNKNOWN"}


def parse_task_data(msg) -> dict:
    text = normalize(msg)

    fecha = extract_date(text)
    hora = extract_time(text)
    tipo_tarea = detect_tipo(text)
    title_tarea = clean_task_title(text)

    if not title_tarea:
        return {
            "ok": False,
            "error": "NO_TITLE",
            "message": "Por favor ingrese un título."
        }

    if not fecha: #sin deadline no se guarda tarea
        return {
            "ok": False,
            "error": "NO_DEADLINE",
            "message": "Por favor ingrese una fecha para la tarea."
        }
        
    deadline = datetime.combine(fecha, hora) if hora else datetime.combine(fecha, time.min)
    if deadline.date() < date.today(): #si la fecha es anterior al día del registro, no se registra 
        return{
            "ok": False,
            "error": "EXPIRED DATE",
            "message": "La fecha ingresada es anterior al día del registro."

        }

    return {
        "ok": True, #hay deadline
        "data": {
            "tipo": tipo_tarea,
            "title": title_tarea,
            "deadline": deadline.isoformat(),
        }
    }


def parse_grupo_data(msg):
    match = re.search(
        r'(?:crear|nuevo)\s+grupo\s+(.+?)\s*,\s*integrantes?\s*:(.+)',
        msg,
        re.IGNORECASE
    )
    if not match:
        return {
            "ok": False,
            "error": """Formato inválido. Usá: 'Crear grupo "nombre", integrantes: user1, user2'"""
        }

    nombre_grupo = match.group(1).strip()
    usernames_raw = match.group(2)
    usernames = [u.strip().lower() for u in usernames_raw.split(",") if u.strip()]

    if not usernames:
        return {
            "ok": False,
            "error": "Especificá al menos un integrante."
        }

    return {
        "ok": True,
        "data": {
            "nombre": nombre_grupo,
            "usernames": usernames
        }
    }



def parse_anticipacion(msg):
    match = re.search(r'(\d+)\s*(?:minutos?|mins?|m)', normalize(msg))
    if not match:
        return {
            "ok": False,
            "error": "No encontré los minutos. Usá: 'Configurar anticipación 30 minutos'"
        }
    minutos = int(match.group(1))
    if minutos < 5 or minutos > 120:
        return {
            "ok": False,
            "error": "La anticipación debe estar entre 5 y 120 minutos."
        }
    return {"ok": True, "data": {"minutos": minutos}}