---
name: Calendario
description: Lectura, creación y gestión de eventos en Google Calendar. Activar cuando Jorge pregunte por agenda, pida crear o mover un evento, o Jeffrey necesite verificar disponibilidad.
---

# Skill: Calendario

## Herramientas requeridas
- MCP Google Calendar (mcp__claude_ai_Google_Calendar__*)
- Zona horaria: Europe/Madrid

## Cuándo activar
- Jorge pregunta por su agenda del día, semana o un período concreto
- Jorge pide crear, mover o cancelar un evento
- Jeffrey necesita contexto de disponibilidad para planificar tareas
- HEARTBEAT diario activa la lectura de agenda

## Proceso

### Leer agenda
1. Autenticar con `mcp__claude_ai_Google_Calendar__authenticate` si es necesario
2. Obtener eventos del período solicitado
3. Presentar en formato limpio: hora — título — duración — notas relevantes
4. Señalar conflictos o huecos importantes

### Crear evento
1. Confirmar: título, fecha, hora inicio, duración, participantes, descripción
2. Si falta algún dato obligatorio: preguntar antes de crear
3. Crear evento y confirmar a Jorge con los detalles

### Verificar disponibilidad
1. Obtener agenda del período relevante
2. Identificar huecos libres de al menos X minutos
3. Proponer opciones ordenadas por conveniencia (mañanas primero salvo indicación contraria)

## Formato de presentación de agenda
```
09:00 - Título del evento (1h)
11:30 - Título del evento (30min) — nota relevante
```

## Edge cases
- Si hay solapamiento al crear un evento: avisar a Jorge y pedir confirmación
- Si el MCP de Calendar no está disponible: indicarlo y pedir a Jorge los datos manualmente
- Si Jorge pide "mañana" o "el lunes": resolver siempre contra la fecha actual del sistema
- Festivos nacionales (España) y de Madrid: tenerlos en cuenta al sugerir fechas
