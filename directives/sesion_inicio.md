# Inicio de sesión

## Objetivo
Cargar el contexto completo al inicio de cada conversación para que Jeffrey opere con información actualizada, sin violar preferencias establecidas y con su carácter propio activo.

## Cuándo ejecutar
Siempre, antes de responder a cualquier mensaje de Jorge.

## Pasos

1. Leer [SOUL.md](../SOUL.md) — personalidad y filosofía operativa de Jeffrey
2. Leer [IDENTITY.md](../IDENTITY.md) — identidad y alcance del agente
3. Leer [memory/MEMORY.md](../memory/MEMORY.md) y todos los archivos referenciados en él
4. Leer la nota de hoy en `memory/daily/YYYY-MM-DD.md` (usando la fecha actual del sistema)
5. Leer la nota de ayer en `memory/daily/YYYY-MM-DD.md` (si existe)
6. Leer [skills/SKILLS.md](../skills/SKILLS.md) — capacidades disponibles
7. Leer [agents/AGENTS.md](../agents/AGENTS.md) — perfiles disponibles
8. Si la primera solicitud involucra el wiki o hay tareas wiki pendientes: leer `wiki/index.md` para cargar el mapa del conocimiento disponible
9. Si hay `.tmp/session_context.md`, leerlo — prioridad máxima sobre todo lo anterior
10. Identificar el dominio de la tarea y activar el perfil de agente correspondiente
11. Responder al primer mensaje de Jorge

## Al final de la sesión

1. Actualizar la nota de hoy en `memory/daily/YYYY-MM-DD.md` con lo relevante ocurrido
2. Si hubo aprendizajes permanentes: actualizar el archivo de memoria correspondiente
3. Actualizar `memory/MEMORY.md` si se crearon archivos nuevos
4. Si se creó o modificó alguna pagina del wiki: verificar que `wiki/index.md` está actualizado y que `wiki/log.md` tiene la entrada correspondiente
5. Registrar uso de archivos en el tracker de trim: `python execution/trim.py --registrar-uso <lista de archivos leídos en la sesión>`

## Lo que NO se hace al inicio

- No saludar con "¿En qué puedo ayudarte?" sin contexto previo
- No repetir lo que ya está en memoria como si fuera descubrimiento nuevo
- No asumir que la fecha es la misma que la última sesión — usar `currentDate` del contexto del sistema
- No ignorar SOUL.md — la personalidad está activa desde el primer mensaje

## Edge cases

- Si MEMORY.md no existe o está vacío: notificarlo antes de continuar
- Si hay archivos de memoria con `confidence: low`: verificar antes de aplicar, no ignorar
- Si `.tmp/session_context.md` contradice memoria permanente: `.tmp/` gana (Capa 1 tiene prioridad)
- Si no existe nota diaria de hoy: crearla vacía al final de la sesión
