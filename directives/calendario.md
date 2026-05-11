# Calendario

## Objetivo
Leer, crear y gestionar eventos en Google Calendar de Jorge para mantener su agenda organizada y sin conflictos.

## Inputs
- Instrucción de Jorge (ver agenda / crear evento / verificar disponibilidad)
- Fecha o período relevante
- Detalles del evento si se va a crear

## Herramientas
- `mcp__claude_ai_Google_Calendar__authenticate` — autenticación
- `mcp__claude_ai_Google_Calendar__complete_authentication` — completar auth
- `skills/calendar.md` — proceso detallado
- Zona horaria siempre: Europe/Madrid

## Pasos

### Ver agenda del día / período
1. Autenticar si es necesario
2. Obtener eventos del período solicitado
3. Presentar en formato limpio:
   ```
   [hora] - [título] ([duración])
   ```
4. Señalar si hay huecos grandes o conflictos

### Crear evento
1. Confirmar: título, fecha, hora inicio, duración
2. Opcionales: descripción, participantes, ubicación
3. Si hay solapamiento: avisar antes de crear
4. Crear evento y confirmar a Jorge los detalles

### Verificar disponibilidad
1. Obtener agenda del período relevante
2. Identificar huecos libres del tamaño solicitado
3. Proponer opciones (preferencia: mañanas, salvo indicación contraria)

### Briefing de agenda (HEARTBEAT diario)
1. Obtener eventos de hoy
2. Presentar en formato briefing del `admin_agent`
3. Señalar cualquier evento sin preparación conocida que requiera atención

## Edge cases
- Si Calendar MCP no está disponible: pedir a Jorge que comparta su agenda en texto
- Si hay solapamiento: nunca crear sin confirmación explícita de Jorge
- Si Jorge usa términos relativos ("mañana", "el jueves"): resolver siempre contra la fecha actual del sistema
- Si un evento tiene participantes externos: verificar disponibilidad antes de proponer hora
