# SKILLS.md

Índice de habilidades de Jeffrey. Leer al inicio de cada sesión junto con MEMORY.md.

Cada skill define una capacidad concreta: qué puede hacer Jeffrey en ese dominio, qué herramientas necesita y cómo activarla.

## Habilidades disponibles

Cada skill reside en su propio directorio con un archivo `Skill.md` que contiene el frontmatter YAML de activación y el cuerpo de instrucciones.

| Skill | Ruta | Dominio |
|-------|------|---------|
| Email | [email/Skill.md](email/Skill.md) | Redacción, revisión y gestión de correos con Gmail |
| Calendario | [calendar/Skill.md](calendar/Skill.md) | Lectura, creación y gestión de eventos en Google Calendar |
| Clase | [clase/Skill.md](clase/Skill.md) | Preparación de sesiones, materiales y seguimiento del módulo de agentes |
| Research | [research/Skill.md](research/Skill.md) | Búsqueda, síntesis y estructuración de información |
| Wiki | [wiki/Skill.md](wiki/Skill.md) | Gestión del wiki de conocimiento en Obsidian |
| Consejo | [consejo/Skill.md](consejo/Skill.md) | Debate multi-agente secuencial con consenso y síntesis Opus |
| Trim | [trim/Skill.md](trim/Skill.md) | Salud de archivos base: detección de contenido extraíble y validación referencial |
| Bibliotecaria | [bibliotecaria/Skill.md](bibliotecaria/Skill.md) | Interfaz completa con el vault de Obsidian — delega en `[DELEGATE:bibliotecaria]` |
| Crear Agente | [crear-agente/Skill.md](crear-agente/Skill.md) | Crea un agente nuevo completo a partir de nombre, funciones y jerarquía |
| Project Manager | [pm/Skill.md](pm/Skill.md) | Gestión de proyectos y tareas en ClickUp — delega en Ricky con [DELEGATE:ricky] |
| Video | [video/Skill.md](video/Skill.md) | Producción de vídeos MP4 para redes sociales con Hyperframes (horizontal y vertical) |
| Investigacion | [investigacion/Skill.md](investigacion/Skill.md) | N investigadores paralelos e independientes exploran un tema con perspectivas distintas y síntesis Opus |

## Activación

Jeffrey activa una skill automáticamente cuando detecta el dominio de la tarea.
También se puede activar explícitamente: "usa la skill de email para esto".

## Añadir nuevas skills

Estructura requerida por skill:

```
skills/
  <nombre>/
    Skill.md       ← obligatorio, con frontmatter YAML
    REFERENCE.md   ← opcional, para información extensa
```

El frontmatter YAML de `Skill.md` debe incluir:
```yaml
---
name: Nombre legible (max 64 caracteres)
description: Cuándo activar esta skill — lo usa Claude para decidir (max 200 caracteres)
---
```

Añadir una fila a la tabla de arriba tras crear la skill.
