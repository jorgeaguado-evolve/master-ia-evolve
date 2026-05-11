---
name: Consejo Multi-Agente
description: Debate multi-agente con 4 perspectivas hasta consenso, seguido de síntesis Opus. Activar cuando Jorge pida "convocar el consejo", varias perspectivas o análisis estratégico complejo.
---

# Skill: Consejo Multi-Agente

## Qué hace
Orquesta un debate estructurado entre 4 agentes especializados (Pragmático, Crítico, Visionario, Implementador) que razonan en rondas secuenciales sobre una pregunta compleja hasta alcanzar consenso, seguido de una síntesis con Opus.

## Cuándo activar
- Jorge pide "convocar el consejo", "debate de agentes", o "necesito varias perspectivas"
- La pregunta es estratégica y una sola ejecución puede ser insuficiente
- Se necesita convergencia documentada, no solo una respuesta

## Cómo activar
```bash
python execution/consejo.py "<pregunta>"
```

## Parámetros del sistema
| Parámetro | Valor | Configurable |
|-----------|-------|-------------|
| Nº de agentes | 4 | En el script |
| Rondas mínimas | 3 | `MIN_ROUNDS` |
| Rondas máximas | 6 | `MAX_ROUNDS` |
| Modelo agentes | claude-sonnet-4-6 | `SONNET` |
| Modelo síntesis | claude-opus-4-7 | `OPUS` |

## Roles fijos

| Agente | Perspectiva |
|--------|-------------|
| **Pragmático** | Viabilidad, recursos, restricciones reales |
| **Crítico** | Riesgos, errores de lógica, puntos ciegos |
| **Visionario** | Impacto a largo plazo, oportunidades estratégicas |
| **Implementador** | Pasos concretos, secuencia, entregables |

## Output
- Debate en terminal con cada turno visible
- Síntesis final estructurada (conclusión, ideas clave, plan, riesgos)
- `.tmp/consejo_output.json` con transcripción completa

## Dependencias
- `anthropic` (SDK Python)
- `python-dotenv`
- `ANTHROPIC_API_KEY` en `.env`
