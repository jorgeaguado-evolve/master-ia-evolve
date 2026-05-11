# Gestión de memoria persistente

## Objetivo

Mantener un único sistema de memoria coherente que persista entre sesiones, sin duplicados ni archivos dispersos.

## Regla fundamental

La carpeta `memory/` dentro del proyecto es la UNICA fuente de verdad.
No usar ni escribir en ningún otro sistema de memoria (incluyendo `~/.claude/projects/*/memory/`).

## Inputs

- `memory/MEMORY.md` — índice de todos los archivos de memoria long-term
- Archivos individuales en `memory/` referenciados desde ese índice
- `memory/daily/YYYY-MM-DD.md` — notas efímeras del día actual y del anterior

## Dos capas de memoria

### Memoria long-term (`memory/*.md`)
Preferencias, aprendizajes y contexto permanente de Jorge. Persiste indefinidamente.
Se gestiona a través de `memory/MEMORY.md` como índice.

### Memoria diaria (`memory/daily/`)
Notas efímeras del día: contexto activo, decisiones en curso, pendientes.
Se carga automáticamente al inicio (hoy y ayer).
Se consolida semanalmente a través del proceso [DREAMS](../DREAMS.md).
Los archivos de más de 7 días se eliminan después de ser consolidados.

## Lectura — cuándo y qué leer

### Al inicio de cada sesión (obligatorio)
1. Leer `memory/MEMORY.md` completo y todos los archivos referenciados
2. Leer `memory/daily/[hoy].md` si existe
3. Leer `memory/daily/[ayer].md` si existe

Sin este paso, Jeffrey puede violar preferencias ya establecidas por Jorge o perder el hilo del día.

### Durante la sesión
Releer un archivo concreto si la tarea lo requiere (por ejemplo, al redactar un email, releer feedback de estilo).

## Escritura — cuándo y qué escribir

### Escribir inmediatamente cuando Jorge:
- Corrija un comportamiento ("no hagas X", "deja de hacer Y")
- Confirme que algo funcionó bien y quiere que se repita
- Comparta información sobre su rol, objetivos o contexto
- Mencione algo sobre el proyecto que no esté en el código ni en git

### Escribir al final de sesión si:
- Se aprendió algo relevante que no se guardó durante la sesión

### NO escribir:
- Patrones de código, arquitectura o rutas de archivos (están en el código)
- Historial de cambios o git (está en git)
- Estado temporal de tareas en curso (pertenece a la conversación, no a memoria)
- Nada que ya esté en CLAUDE.md

## Tipos de memoria y archivos

| Tipo | Archivo | Contenido |
|------|---------|-----------|
| `user` | `user.md` | Quién es Jorge, su rol, objetivos, preferencias |
| `feedback` | `feedback_*.md` | Correcciones y validaciones de comportamiento |
| `project` | `project_*.md` | Contexto de iniciativas, decisiones, fechas |
| `reference` | `reference_*.md` | Dónde encontrar información en sistemas externos |
| `errors` | `errors.md` | Tabla de errores cometidos y cómo evitarlos |

## Formato de archivos de memoria

```markdown
---
name: Nombre del recuerdo
description: Una línea — se usa para decidir relevancia en sesiones futuras
type: user | feedback | project | reference
created: YYYY-MM-DD
confidence: high | medium | low
---

Contenido del recuerdo.

**Why:** Por qué importa o por qué Jorge lo pidió.
**How to apply:** Cuándo y cómo aplicarlo.
```

### Campos de proveniencia

- `created`: fecha en que se escribió o actualizó el recuerdo por última vez
- `confidence`: nivel de certeza sobre el recuerdo
  - `high`: confirmado explícitamente por Jorge o repetido varias veces
  - `medium`: inferido del contexto o confirmado una vez
  - `low`: hipótesis sin confirmar — revisar antes de aplicar

Al escribir un recuerdo nuevo, siempre incluir ambos campos.
Al actualizar un recuerdo, actualizar `created` a la fecha actual y revisar si `confidence` debe cambiar.

## Formato del índice MEMORY.md

Una línea por entrada, máximo 150 caracteres:
```
- [Título](archivo.md) — descripción corta
```

Sin frontmatter. Sin contenido directo. Solo punteros.

## Actualización

- Antes de crear un archivo nuevo, revisar si ya existe uno que se puede actualizar.
- Si un recuerdo queda obsoleto, actualizarlo o eliminarlo. No acumular entradas contradictorias.
- Si se elimina un archivo, eliminar también su línea en MEMORY.md.

## Edge cases

- Si Jorge pide recordar algo que ya está en CLAUDE.md: no duplicar, responder que ya está cubierto allí.
- Si hay conflicto entre un recuerdo y el estado actual del código: confiar en el código, actualizar el recuerdo.
- Si un recuerdo menciona un archivo o función que ya no existe: verificar antes de actuar, luego actualizar el recuerdo.
