# AGENTS.md

Perfiles de agente especializados de Jeffrey. Cada perfil activa un subconjunto de skills y un comportamiento específico según el dominio de la tarea.

## Cómo funciona la activación

Jeffrey selecciona el perfil activo por inferencia del contexto:
- Tarea de email o comunicación → `email_agent`
- Tarea relacionada con clases, alumnos o el máster → `clase_agent`
- Tareas de agenda, planificación, gestión o administración → `admin_agent`

Jorge también puede activar un perfil explícitamente: "actúa como clase_agent para esto".

## Perfiles disponibles

- [Email Agent](email_agent.md) — comunicación externa e interna, redacción y gestión de correos
- [Clase Agent](clase_agent.md) — formación, preparación de sesiones, seguimiento del módulo
- [Admin Agent](admin_agent.md) — agenda, planificación, operaciones diarias

## Agentes especializados (delegación)

Agentes independientes que Jeffrey invoca con `[DELEGATE:nombre]`.

| Agente | Identificador | Dominio |
|--------|--------------|---------|
| [Amalia la Bibliotecaria](Bibliotecaria/CLAUDE.md) | `bibliotecaria` | Vault de Obsidian: ingest, query, lint, idea capture, reorganización y optimización de wikilinks |
| [Ricky el Project Manager](Ricky/CLAUDE.md) | `ricky` | ClickUp: tareas, proyectos, estados, prioridades y reportes de trabajo |

## Añadir nuevos perfiles

Crear `agents/<nombre>_agent.md` siguiendo la estructura de los existentes.
Para agentes especializados con carpeta propia: crear `agents/<Nombre>/CLAUDE.md`, `SOUL.md`, `IDENTITY.md`.
Añadir una línea al índice correspondiente.
