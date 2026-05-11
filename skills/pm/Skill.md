---
name: Project Manager (Ricky)
description: Activar cuando la tarea involucre ClickUp, gestion de tareas, proyectos, estado de trabajo pendiente o priorizacion. Delega en Ricky con [DELEGATE:ricky].
---

# Skill: Project Manager

## Que hace

Ricky gestiona el workspace de ClickUp de Jorge: crea, lee, actualiza y reporta sobre tareas y proyectos.
Opera como interfaz entre Jorge (o Jeffrey) y ClickUp, manteniendo el workspace ordenado y actualizado.

## Cuando activar

- Jorge pregunta por el estado de sus proyectos o tareas
- Jorge quiere crear una tarea nueva
- Jeffrey recibe una peticion relacionada con gestion de trabajo o seguimiento de proyectos
- Hay que priorizar, reorganizar o reportar el estado del trabajo

## Como delegar

Jeffrey invoca a Ricky con:

```
[DELEGATE:ricky] <descripcion de la operacion>
```

Jorge invoca directamente con `/pm`.

## Operaciones disponibles

| Operacion | Descripcion |
|-----------|-------------|
| LIST | Ver tareas de un proyecto o todas las pendientes |
| CREATE | Crear tarea o lista nueva en ClickUp |
| UPDATE | Cambiar estado, prioridad o descripcion de una tarea |
| REPORT | Resumen de estado de todos los proyectos |
| REORG | Proponer o ejecutar reorganizacion del workspace |

## Herramienta base

`execution/clickup_client.py` — cliente Python con las operaciones principales de la API de ClickUp.
