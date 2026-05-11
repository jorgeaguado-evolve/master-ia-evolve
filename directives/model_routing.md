# Model Routing

## Objetivo
Distribuir el uso de modelos según la complejidad de la tarea para optimizar coste, velocidad y calidad.

## Regla general

Antes de lanzar cualquier subagente o sugerir cambio de modelo, consultar esta tabla.

## Tabla de enrutamiento

| Modelo | Parámetro | Cuándo usarlo |
|--------|-----------|---------------|
| `haiku` | `model: "haiku"` | Subagentes efímeros: leer documentos, consultar archivos, ejecutar scripts, tareas de extracción o escritura simple sin lógica compleja |
| `sonnet` | `model: "sonnet"` | Sesión principal con Jorge, desarrollo de skills, actualizar documentos, tareas con lógica moderada, redacción |
| `opus` | `model: "opus"` | Planes de arquitectura, tareas muy complejas de razonamiento, sesiones programadas sin Jorge presente |

## Reglas de aplicación

### Subagentes (Agent tool)
- Por defecto: `model: "haiku"` para cualquier subagente efímero
- Excepción: si el subagente necesita razonar, sintetizar o tomar decisiones con matices — usar `sonnet`
- No usar `opus` en subagentes salvo que Jorge lo pida explícitamente

### Cambio a Opus
- Jeffrey propone el cambio cuando detecta una tarea que cumple **todos** estos criterios:
  1. Requiere planificación compleja o razonamiento profundo
  2. No es urgente (puede esperar o programarse)
  3. Jorge no está en modo conversacional activo
- Formato de propuesta: "Esta tarea encaja bien para Opus — ¿la programamos o la lanzas tú cuando tengas un momento?"

### Sesión principal
- Siempre corre en Sonnet (lo gestiona Claude Code, no Jeffrey)
- Jeffrey no cambia el modelo de la sesión principal

## Edge cases
- Si una tarea parecía Haiku pero resulta compleja durante la ejecución: relanzar en Sonnet, registrar el patrón
- Si Jorge pide explícitamente un modelo concreto: respetar sin discutir
- Si hay duda entre Haiku y Sonnet: Haiku primero, Sonnet si falla o el resultado es insuficiente
