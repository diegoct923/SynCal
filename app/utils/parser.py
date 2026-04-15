import re
import unicodedata
from datetime import datetime
import dateparser

#tipos de tareas
TYPE_KEYWORDS = { 
    "EXAMEN": ["parcial", "examen"],
    "TAREA": ["tarea", "entrega", "deber"],
    "PRACTICO": ["practico", "repartido", "lectura", "leer", "ejercicios", "ejercicio"],
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

    #patrones en que puede venir fecha  añadir parcial matemáticas jueves 23 de abril
    patterns = [ 
        # combinaciones tipo "jueves 20 de abril"
        r'\b(?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)\s+\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
        
        # "20 de abril"
        r'\b\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
        
        # 15/04 o 15-04
        r'\b\d{1,2}[/-]\d{1,2}\b',

        # expresiones relativas
        r'\b(hoy|manana|pasado manana)\b',

        # "jueves", "viernes", etc.
        r'\b(lunes|martes|miercoles|jueves|viernes|sabado|domingo)\b'        
    ]

    candidatos = []
    #extraer todos los posibles fragmentos de fecha
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            # re.findall puede devolver tuplas si hay grupos
            if isinstance(m, tuple):
                m = " ".join(m)

            candidatos.append(m)
    
     #intentar parsear cada candidato
    for candidato in candidatos:
        date = dateparser.parse(candidato, settings={"RELATIVE_BASE": datetime.now()})
        if date:
            print(date)
            return date

    #si no hubo matches parsea el texto  "PREFER_DATES_FROM": "future", 
    #date = dateparser.parse(text, settings={"RELATIVE_BASE": datetime.now()})
    #if date:
    #    print(date)
    #    return date

    return None


    #limpiar nombre de tarea 

def clean_task_title(text: str) -> str:
   # remover conectores comunes
    noise_words = [
        "para", "el", "la", "los", "las",
        "de", "del", "con", "por", "antes",
        "hacer", "tengo", "que", "agregar", 
        "añadir", "crear", "parcial", "entrega"
    ]
    # remover fechas explícitas
    text = re.sub(r'\d{1,2}/\d{1,2}', '', text) #ej : 12/04
    text = re.sub(r'\d{1,2}-\d{1,2}', '', text) #ej : 12-04

    # remover días y relativos
    text = re.sub(r'(lunes|martes|miercoles|jueves|viernes|sabado|domingo|hoy|manana|pasado manana)','',text)

    # remover keywords de tipo
    for words in TYPE_KEYWORDS.values():
        for w in words:
            text = text.replace(w, "")

    # remover ruido
    for word in noise_words:
        text = text.replace(f" {word} ", " ")

    # limpiar espacios extra
    text = re.sub(r'\s+', ' ', text).strip()

    return text


#parsear intención
def parse_intent(text) -> dict:
    text = text.lower()

    if any(x in text for x in ["agregar", "añadir", "crear", "parcial", "entrega"]):
        return {"type": "ADD"}

    if any(x in text for x in ["ver tareas", "mis tareas", "listar", "tareas", "listar tareas"]):
        return {"type": "LIST"}

    return {"type": "UNKNOWN"}


def parse_task_data(msg) -> dict:
    original = msg
    text = normalize(msg)

    deadline = extract_date(text)
    tipo_tarea = detect_tipo(text)
    title_tarea = clean_task_title(text)

    if not title_tarea:
        title_tarea = original

    if not deadline: #sin deadline no se guarda tarea
        return {
            "ok": False,
            "error": "NO_DEADLINE",
            "message": "No se pudo encontrar fecha"
        }
        

    return {
        "ok": True, #hay deadline
        "data": {
            "tipo": tipo_tarea,
            "title": title_tarea,
            "deadline": deadline.isoformat()
        }
    }
    