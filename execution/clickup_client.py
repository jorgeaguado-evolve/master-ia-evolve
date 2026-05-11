"""
Cliente base para la API de ClickUp.
IDs fijos del workspace de Jorge (Edu):
  workspace_id: 90121712408
  space_id:     90127431397
  folder_id:    901210976344 (Proyectos)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.clickup.com/api/v2"
HEADERS = {"Authorization": os.getenv("CLICKUP_API_KEY"), "Content-Type": "application/json"}

WORKSPACE_ID = "90121712408"
SPACE_ID = "90127431397"
FOLDER_ID = "901210976344"


def _get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def _post(path, body):
    r = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()


def _put(path, body):
    r = requests.put(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()


def _delete(path):
    r = requests.delete(f"{BASE_URL}{path}", headers=HEADERS)
    r.raise_for_status()
    return r.json() if r.content else r.status_code


# Listas
def get_lists():
    """Devuelve todas las listas de la carpeta Proyectos."""
    return _get(f"/folder/{FOLDER_ID}/list")["lists"]


def create_list(name, content=""):
    """Crea una lista nueva en la carpeta Proyectos."""
    return _post(f"/folder/{FOLDER_ID}/list", {"name": name, "content": content})


# Tareas
def get_tasks(list_id, include_closed=False):
    """Devuelve las tareas de una lista."""
    return _get(f"/list/{list_id}/task", {"include_closed": str(include_closed).lower()})["tasks"]


def get_task(task_id):
    """Devuelve una tarea por ID."""
    return _get(f"/task/{task_id}")


def create_task(list_id, name, description="", status="pendiente", priority=None, due_date=None):
    """
    Crea una tarea en una lista.
    priority: 1=urgent, 2=high, 3=normal, 4=low
    due_date: timestamp en milisegundos (int)
    """
    body = {"name": name, "description": description, "status": status}
    if priority:
        body["priority"] = priority
    if due_date:
        body["due_date"] = due_date
    return _post(f"/list/{list_id}/task", body)


def update_task(task_id, **fields):
    """
    Actualiza campos de una tarea existente.
    Campos válidos: name, description, status, priority, due_date
    """
    return _put(f"/task/{task_id}", fields)


def delete_task(task_id):
    """Elimina una tarea por ID."""
    return _delete(f"/task/{task_id}")


# Utilidades
def find_list_by_name(name):
    """Devuelve la primera lista cuyo nombre coincida (case-insensitive)."""
    for lst in get_lists():
        if lst["name"].lower() == name.lower():
            return lst
    return None


if __name__ == "__main__":
    # Smoke test: listar listas y tareas
    lists = get_lists()
    for lst in lists:
        print(f"\nLista: {lst['name']} (id: {lst['id']})")
        tasks = get_tasks(lst["id"])
        for t in tasks:
            print(f"  [{t['status']['status']}] {t['name']}")
