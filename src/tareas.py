tareas = []

def crear_tarea(titulo, fecha_limite):
    tarea = {
        "titulo": titulo,
        "fecha_limite": fecha_limite,
    }

    tareas.append(tarea)
    return tarea

def listar_tareas():
    return tareas