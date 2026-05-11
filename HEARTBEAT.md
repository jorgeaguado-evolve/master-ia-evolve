# HEARTBEAT — Agenda automática

Tareas periódicas que Jeffrey debe ejecutar cuando reciba un pulso.
Si no hay nada programado para el momento actual, responder: `OK`.

## Formato de entrada

```
- [frecuencia] descripción → directiva o script a ejecutar
```

## Diario

- [diario] Verificar backup GitHub → revisar `.tmp/backup_log.txt`: si el último registro tiene más de 24h o contiene "ERROR", incluirlo en el briefing como alerta roja con el mensaje exacto del error
- [diario] Trim report silencioso → ejecutar `python execution/trim.py --solo-reporte` (genera `.tmp/trim_report.md` sin modificar nada). Si hay links rotos o candidatos críticos: incluirlos en el briefing como alerta.
- [diario] Briefing de inicio del día → activar `admin_agent`, ejecutar `directives/calendario.md` (briefing), revisar emails urgentes con `directives/email.md` (revisar bandeja, filtro `is:unread is:important`)
- [diario-20:00-Madrid] Resumen de jornada en borrador → activar `email_agent`; revisar `memory/session_log.md` y `.tmp/session_context.md` para extraer lo trabajado hoy; redactar borrador de correo dirigido a `iagen@evolve.es` con asunto "Resumen del día — [fecha]" que incluya: tareas completadas, decisiones tomadas, pendientes para mañana; crear draft en Gmail con `mcp__claude_ai_Gmail__create_draft`
- [diario] Verificar fuentes sin ingerir → revisar si hay archivos en `fuentes/` con fecha posterior a la ultima entrada `[ingest]` en `wiki/log.md`. Si los hay: notificarlo en el briefing como "Fuentes pendientes de procesar: [lista]"

Formato de respuesta esperado:
```
HOY — [fecha]

AGENDA
[eventos del día]

PENDIENTE
[tareas urgentes o correos que requieren acción]

PARA TU ATENCIÓN
[alertas o temas a decidir hoy]
```

## Semanal

- [semanal-lunes] Prep de semana → activar `clase_agent`, revisar qué sesiones hay esta semana en calendario, identificar materiales que faltan, proponer plan de preparación
- [semanal-viernes] Cierre de semana → revisar progreso del módulo (días impartidos / 10), señalar si hay desvío de ritmo, resumir temas cubiertos esta semana
- [semanal-domingo] Lint del wiki → activar skill wiki, ejecutar `directives/wiki_lint.md`, preparar informe de salud para incluirlo en el briefing del lunes

## Mensual

- [mensual] Revisión de progreso del máster → contar días de clase impartidos, calcular % de avance, listar temas pendientes, revisar si el objetivo pedagógico principal (alumnos que construyen su primer agente) va en buen camino
