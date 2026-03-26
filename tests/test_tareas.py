from src.tareas import *

def test_crear_tarea():
    tarea = crear_tarea("Test Tarea", "2026-01-01")
    assert tarea["titulo"] == "Test Tarea"
    assert tarea["fecha_limite"] == "2026-01-01"

def test_listar_tareas():
    crear_tarea("Tarea 1", "2026-02-01")

    tareas = listar_tareas()
    assert len(tareas) >= 1