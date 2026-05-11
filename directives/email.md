# Email

## Objetivo
Gestionar la comunicación por email de Jorge: redactar, revisar, responder y organizar correos con eficiencia y el tono correcto.

## Inputs
- Instrucción de Jorge (redactar / responder / revisar bandeja)
- Destinatario y contexto si es correo nuevo
- ID de hilo si es respuesta (o usar búsqueda en Gmail)

## Herramientas
- `mcp__claude_ai_Gmail__create_draft` — crear borrador
- `mcp__claude_ai_Gmail__get_thread` — leer hilo existente
- `mcp__claude_ai_Gmail__search_threads` — buscar correos
- `mcp__claude_ai_Gmail__list_labels` — gestión de etiquetas
- `skills/email.md` — proceso detallado

## Pasos

### Redactar correo nuevo
1. Confirmar: destinatario, asunto, propósito (¿qué debe lograr el email?)
2. Si falta alguno: preguntar antes de escribir
3. Redactar borrador — directo, sin relleno, párrafos de máximo 3 líneas
4. Presentar a Jorge para revisión
5. Aplicar cambios si los hay
6. Crear draft en Gmail con `create_draft`
7. Confirmar: "Draft listo en Gmail"

### Responder email existente
1. Obtener el hilo con `get_thread`
2. Leer todo el hilo antes de proponer respuesta
3. Identificar qué espera el remitente
4. Redactar respuesta manteniendo el hilo
5. Presentar a Jorge y aplicar cambios
6. Crear draft con `create_draft` como respuesta al hilo

### Revisar bandeja
1. Buscar con `search_threads` — filtros: `is:unread`, `is:important`, o los que Jorge indique
2. Agrupar resultados: urgente / requiere acción / informativo / spam
3. Presentar resumen con acciones propuestas para cada grupo
4. Ejecutar las acciones que Jorge apruebe

## Edge cases
- Si Gmail MCP no está disponible: redactar el texto igualmente, avisar a Jorge para que lo copie
- Si el asunto puede tener consecuencias legales, económicas o reputacionales: confirmar antes de crear draft
- Si no hay acceso al hilo pero Jorge tiene el contexto: pedírselo en texto antes de redactar
- Si Jorge pide enviar directamente: recordarle que el proceso es draft primero, envío manual
