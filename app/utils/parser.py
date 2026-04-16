import re
import unicodedata
from datetime import datetime
import dateparser

#tipos de tareas
TYPE_KEYWORDS = { 
    "EXAMEN": ["parcial", "examen"],
    "TAREA": ["tarea", "entrega", "deber"],
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

    #patrones en que puede venir fecha  ej : añadir parcial matemáticas jueves 23 de abril
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

    

    return None


    #limpiar nombre de tarea 

def clean_task_title(text: str) -> str:
   # remover conectores comunes
    
    noise_words = [
        "para", "el", "la", "los", "las",
        "del", "con", "por", "antes",
        "hacer", "tengo", "que", "agregar", 
        "anadir", "crear", "parcial", "entrega", "de", "listar"
    ]

     # noise words
    for word in noise_words:
        text = re.sub(rf'\b{word}\b', '', text)

    text = re.sub(r'\s+', ' ', text).strip() #normalizar
   

    
    # remover fechas explícitas
    text = re.sub(r'\d{1,2}/\d{1,2}', '', text) #ej : 12/04
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\d{1,2}-\d{1,2}', '', text) #ej : 12-04
    text = re.sub(r'\s+', ' ', text).strip() #normalizar
    
    
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

    if any(x in text for x in ["agregar", "anadir", "crear", "parcial", "entrega", "hacer", "tengo"]):
        return {"type": "ADD"}

    if any(x in text for x in ["ver tareas", "mis tareas", "listar", "listar tareas"]):
        return {"type": "LIST"}

    if any(x in text for x in ["ver calendario", "mi calendario", "calendario", "mostrar calendario"]):
        return {"type": "CALENDAR"}

    return {"type": "UNKNOWN"}


def parse_task_data(msg) -> dict:
    original = msg
    text = normalize(msg)

    deadline = extract_date(text)
    tipo_tarea = detect_tipo(text)
    title_tarea = clean_task_title(text)

    if not title_tarea:
        return {
            "ok": False,
            "error": "NO_TITLE",
            "message": "Por favor ingrese un título"
        }

    if not deadline: #sin deadline no se guarda tarea
        return {
            "ok": False,
            "error": "NO_DEADLINE",
            "message": "Por favor ingrese una fecha para la tarea"
        }
        

    return {
        "ok": True, #hay deadline
        "data": {
            "tipo": tipo_tarea,
            "title": title_tarea,
            "deadline": deadline.isoformat()
        }
    }
    