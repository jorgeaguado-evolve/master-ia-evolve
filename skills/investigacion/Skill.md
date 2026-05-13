---
name: Investigacion Multi-Agente
description: N investigadores trabajan en paralelo y de forma completamente independiente sobre el mismo tema, cada uno con una perspectiva distinta y siguiendo los mismos pasos. Opus sintetiza al final. Activar cuando Jorge pida investigar algo con múltiples ángulos, dé un objetivo y una lista de pasos, o quiera explorar un tema con perspectivas diversas.
---

# Skill: Investigación Multi-Agente Paralela

## Qué hace

Lanza N investigadores en paralelo que trabajan de forma completamente aislada: no se conocen, no se leen, no interactúan. Cada uno recorre los mismos pasos desde su perspectiva característica. Al terminar todos, Opus sintetiza los hallazgos independientes y revela lo que el conjunto sabe que ninguno sabía por separado.

**Diferencia clave con Consejo**: en Consejo los agentes debaten en rondas y se reaccionan entre sí. En Investigación los agentes son paralelos e independientes — el valor está en la diversidad de perspectivas, no en el consenso.

## Cuándo activar

- Jorge dice "investiga X" y da pasos o instrucciones
- Jorge quiere "varios ángulos" sobre un tema sin debate
- Jorge pide investigar empresas, canales, personas, debates científicos, mercados, etc.
- Se necesita exploración amplia de un tema antes de tomar una decisión
- Jorge quiere un documento de investigación revisable para luego guardar en Obsidian

## Cómo activar

**Via script** (sin internet o para automatizar):
```bash
python execution/investigacion.py \
  --tema "Canales de YouTube sobre IA en España" \
  --objetivo "Mejorar mis guiones aprendiendo de los mejores" \
  --pasos "Identifica los 3 mejores videos del tema" \
          "Analiza la estructura del guion" \
          "Extrae los 3 patrones de enganche más importantes" \
  --n 4
```

**Via Jeffrey** (con internet, pasos que necesitan WebSearch):
Jeffrey lee `directives/investigacion.md` y orquesta N agentes con el Agent tool. Cada agente tiene acceso a WebSearch y WebFetch.

## Parámetros

| Parámetro | Default | Rango | Descripción |
|-----------|---------|-------|-------------|
| `--tema` | — | string | Qué se investiga |
| `--objetivo` | — | string | Para qué (contexto para Opus) |
| `--pasos` | — | 1-N strings | Instrucciones secuenciales por investigador |
| `--n` | 4 | 1-8 | Número de investigadores |
| `--uniforme` | false | flag | Desactiva perspectivas (todos neutros) |

## Perspectivas disponibles (asignación por posición)

| # | Nombre | Enfoque |
|---|--------|---------|
| 1 | 📊 Analista | Datos, patrones, evidencia empírica |
| 2 | 🔍 Escéptico | Límites, contraejemplos, rigor |
| 3 | 💡 Creativo | Conexiones no obvias, analogías |
| 4 | ⚙️ Pragmático | Aplicabilidad, restricciones, acción |
| 5 | 📚 Historiador | Contexto, evolución, precedentes |
| 6 | 🎯 Estratega | Ventajas, oportunidades, largo plazo |
| 7 | 📣 Divulgador | Claridad, accesibilidad, narrativa |
| 8 | 🔧 Técnico | Mecanismos, implementación, precisión |

## Output

- **`.tmp/investigacion_YYYYMMDD_HHMMSS.md`** — documento revisable con hallazgos por investigador + síntesis Opus
- **`.tmp/investigacion_YYYYMMDD_HHMMSS.json`** — datos estructurados
- Tras aprobación de Jorge: `[DELEGATE:bibliotecaria]` para guardar en Obsidian

## Modelos

| Rol | Modelo |
|-----|--------|
| Investigadores | `claude-sonnet-4-6` |
| Sintetizador | `claude-opus-4-7` (requiere confirmación previa de Jorge) |

## Dependencias

- `anthropic` >= 0.100.0 (requiere `AsyncAnthropic`)
- `python-dotenv`
- `ANTHROPIC_API_KEY` en `.env`
- Para pasos con internet: Jeffrey orquesta via Agent tool (WebSearch nativo)
