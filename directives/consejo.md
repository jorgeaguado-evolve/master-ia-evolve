# Directiva: Consejo Multi-Agente

## Objetivo
Lanzar un debate estructurado entre múltiples agentes para converger en la mejor solución a una pregunta compleja. Útil cuando la varianza entre ejecuciones es alta o el problema requiere perspectivas múltiples.

## Cuándo usar
- Decisiones estratégicas o arquitectónicas sin respuesta obvia
- Preguntas donde una sola ejecución puede ser insuficiente
- Jorge pide explícitamente un consejo o debate de agentes

## Inputs
- `pregunta`: string con el problema o pregunta a debatir (CLI arg o stdin)

## Proceso

### 1. Preparación
- Ejecutar `python execution/consejo.py "<pregunta>"`
- No se necesita contexto previo: el script es autocontenido

### 2. Estructura del debate
- **4 agentes** con roles fijos: Pragmático, Crítico, Visionario, Implementador
- **Mínimo 3 rondas** (cada agente interviene al menos 3 veces)
- **Máximo 6 rondas** (techo de seguridad)
- Cada agente ve la transcripción acumulada completa antes de responder
- Cada agente señala `[CONSENSO: SÍ/NO]` al final de su turno

### 3. Condición de parada
- Si **todos** los agentes señalan `[CONSENSO: SÍ]` en la misma ronda **y** ya se completaron al menos 3 rondas → el debate termina
- Si se llega a 6 rondas sin consenso → termina igualmente

### 4. Síntesis final
- Un agente sintetizador con modelo **Opus** lee la transcripción completa
- Produce: conclusión principal, ideas clave, plan de acción y riesgos

## Outputs
- Salida en terminal (debate + síntesis)
- `.tmp/consejo_output.json` con transcripción completa y síntesis

## Modelos
| Rol | Modelo |
|-----|--------|
| Agentes del debate (×4) | `claude-sonnet-4-6` |
| Sintetizador final | `claude-opus-4-7` |

## Edge cases
- Si falta `ANTHROPIC_API_KEY` en `.env`: el script aborta con mensaje claro
- Si la pregunta es trivial: el debate convergirá rápido (ronda 3 probable)
- Si hay desacuerdo profundo: llega a ronda 6 y Opus sintetiza igualmente
