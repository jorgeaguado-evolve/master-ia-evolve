---
name: Email
description: Gestión completa de correo Gmail de Jorge: redactar, revisar, responder emails y revisar bandeja de entrada. Activar para cualquier operación de email o comunicación externa.
---

# Skill: Email

## Herramientas requeridas
- MCP Gmail (mcp__claude_ai_Gmail__*)
- Acceso a `memory/user.md` para tono y contexto del remitente

## Cuándo activar
- Jorge pide redactar, revisar o responder un email
- Jorge pide revisar su bandeja de entrada
- Jorge pide buscar un correo concreto
- Tarea relacionada con comunicación externa o interna

## Proceso

### Redactar email nuevo
1. Identificar destinatario, asunto y propósito clave
2. Leer `memory/user.md` para aplicar el tono correcto
3. Redactar borrador: directo, sin relleno, párrafos cortos
4. Presentar el borrador a Jorge para revisión antes de enviar
5. Aplicar cambios si los hay
6. Crear draft en Gmail con `mcp__claude_ai_Gmail__create_draft`
7. Confirmar a Jorge que el draft está listo

### Responder email existente
1. Leer el hilo completo con `mcp__claude_ai_Gmail__get_thread`
2. Entender el contexto y lo que se espera como respuesta
3. Redactar respuesta manteniendo el hilo
4. Presentar a Jorge antes de enviar

### Revisar bandeja de entrada
1. Buscar con `mcp__claude_ai_Gmail__search_threads` usando filtros relevantes
2. Agrupar por prioridad: urgente / requiere acción / informativo
3. Presentar resumen estructurado a Jorge
4. Proponer acciones concretas para cada grupo

## Tono y estilo
- Español por defecto salvo que el destinatario sea angloparlante
- Directo y profesional — sin fórmulas de cortesía innecesarias
- Sin "Espero que estés bien" ni "No dudes en contactarme"
- Firma: Jorge (sin cargo ni datos extra salvo que se pida)

## Edge cases
- Si falta el destinatario: preguntar antes de redactar
- Si el asunto es sensible o puede tener consecuencias: confirmar antes de crear draft
- Si Gmail MCP no está disponible: redactar el texto igualmente y pedir a Jorge que lo copie
- Si hay ambigüedad sobre el tono (formal/informal): usar el histórico del hilo o preguntar
