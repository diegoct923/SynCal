from tareas import *

#Crear tarea
crear_tarea("Entrega Ing de Software", "2026-03-16")
crear_tarea("Parcial AM2", "2026-03-20")

#Listar tareas
tareas = listar_tareas()
for tarea in tareas:
    print(f"Título: {tarea['titulo']}, Fecha Límite: {tarea['fecha_limite']}")