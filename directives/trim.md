# Trim — Limpieza de archivos always-loaded

## Objetivo
Mantener los archivos del hot path (cargados en cada inicio de sesión) dentro de sus umbrales de tamaño. Mover contenido de detalle a archivos on-demand. Evitar que el contexto base crezca indefinidamente.

## Cuándo ejecutar
- Jorge invoca `/trim` o la skill de trim
- HEARTBEAT mensual

## Hot path y umbrales

| Archivo | Umbral |
|---------|--------|
| CLAUDE.md | 5 KB |
| SOUL.md | 2.5 KB |
| IDENTITY.md | 1.5 KB |
| memory/user.md | 2 KB |
| memory/feedback_*.md | 1 KB cada uno |
| memory/session_log.md | 1 KB |
| directives/sesion_inicio.md | 2 KB |
| skills/SKILLS.md | 1 KB |
| agents/AGENTS.md | 1 KB |

## Pasos

### 1. Medir
Para cada archivo del hot path: obtener tamaño (`wc -c`) y comparar con umbral.
Listar los que están por encima.

### 2. Analizar (solo archivos sobre umbral)
Identificar secciones candidatas a mover:
- Guías paso a paso → ya existe una directiva específica, reemplazar con enlace
- Listas de ejemplos o edge cases → mover a `<archivo>_detail.md`
- Contenido idéntico o redundante con otro archivo → eliminar y dejar solo el enlace
- Tablas de referencia que ya existen en otro archivo → reemplazar con enlace

No mover nunca:
- Reglas de comportamiento obligatorias
- Restricciones explícitas del usuario
- Índices (listas de enlaces a otros archivos)

### 3. Archivar session_log.md
- Si hay más de 10 entradas en la tabla: mover las más antiguas a `memory/archive/session_log_YYYY.md`
- Dejar solo las 10 más recientes en el archivo activo

### 4. Proponer a Jorge
Mostrar un resumen de cambios antes de ejecutar:
- Archivos sobre umbral y su tamaño actual
- Secciones propuestas para mover o eliminar
- Destino de cada sección

### 5. Ejecutar (con aprobación explícita)
Solo modificar archivos tras confirmación de Jorge.

### 6. Actualizar índices
- Si se crearon archivos nuevos: añadir entrada en `memory/MEMORY.md`
- Verificar que todos los enlaces nuevos son válidos

## Criterio de decisión
Pregunta clave para cada bloque de texto: "¿Necesito esto en el 100% de las sesiones?"
Si no → candidato a mover a on-demand.

## Edge cases
- Si un archivo está sobre umbral pero todo su contenido es comportamiento obligatorio: dejarlo, no forzar el recorte
- Si `memory/archive/` no existe: crearlo antes de archivar
- Si hay entradas en session_log con `confidence: low`: marcarlas en el informe para que Jorge las revise
