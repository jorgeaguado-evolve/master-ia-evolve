# Directiva: Investigación Multi-Agente Paralela

## Objetivo

Lanzar N investigadores en paralelo, completamente aislados entre sí, para que investiguen el mismo tema desde perspectivas distintas siguiendo una secuencia de pasos. Cuando todos terminan, un sintetizador Opus consolida los hallazgos independientes en conclusiones que ningún investigador solo habría alcanzado.

## Diferencia con Consejo

| | Investigación | Consejo |
|---|---|---|
| **Flujo** | Paralelo e independiente | Secuencial, reactivo |
| **Comunicación** | Los agentes no se conocen | Los agentes se leen entre sí |
| **Objetivo** | Síntesis de perspectivas aisladas | Consenso por debate |
| **Estructura** | Pasos fijos por agente | Rondas de intercambio |
| **Usar cuando** | Explorar un tema con amplitud | Tomar una decisión compleja |

## Inputs

- `tema`: qué se investiga (string)
- `objetivo`: para qué sirve la investigación — contexto que recibe el sintetizador
- `pasos`: lista de instrucciones que ejecuta cada investigador en secuencia
- `n_agentes`: cuántos investigadores (1-8, default: 4)
- `uniforme`: si true, todos los investigadores son neutros (sin perspectiva diferenciada)

## Perspectivas predefinidas

Se asignan por posición según el orden de la lista. Con 4 agentes se usan las primeras 4.

| # | Nombre | Enfoque |
|---|--------|---------|
| 1 | Analista | Datos, métricas, evidencia empírica |
| 2 | Escéptico | Límites, contraejemplos, rigor crítico |
| 3 | Creativo | Conexiones no obvias, analogías, originalidad |
| 4 | Pragmático | Aplicabilidad real, restricciones, siguiente paso |
| 5 | Historiador | Contexto histórico, evolución, precedentes |
| 6 | Estratega | Ventajas competitivas, oportunidades a largo plazo |
| 7 | Divulgador | Claridad, accesibilidad, narrativa central |
| 8 | Técnico | Mecanismos exactos, implementación, precisión |

## Proceso

### 1. Extraer inputs

Del mensaje de Jorge extraer:
- `tema`: el objeto de investigación
- `objetivo`: para qué se investiga (si no lo dice, preguntar — es clave para el sintetizador)
- `pasos`: la secuencia que seguirá cada investigador
- `n_agentes`: cuántos quiere (si no lo dice, proponer 4)

### 2. Mostrar el plan y pedir confirmación para Opus

Antes de ejecutar, mostrar a Jorge:
```
Investigadores: [lista de perspectivas asignadas]
Pasos por investigador:
  1. [paso 1]
  2. [paso 2]
  ...
Llamadas API: N×M Sonnet + 1 Opus
```

Pedir confirmación explícita para Opus (obligatorio según model_routing.md).

### 3. Decidir modo de ejecución

**Via script** (sin necesidad de internet o para programar con HEARTBEAT):
```bash
python execution/investigacion.py \
  --tema "..." \
  --objetivo "..." \
  --pasos "paso 1" "paso 2" "paso 3" \
  --n 4
```

**Via Jeffrey con Agent tool** (cuando los pasos requieren WebSearch o acceso a URLs):
Jeffrey orquesta N agentes en paralelo con el `Agent` tool (model: "sonnet"), cada uno con su perspectiva y sus pasos. Los agentes tienen acceso a WebSearch y WebFetch.

### 4. Monitorear y recopilar

- El script muestra progreso por investigador y paso
- Los agentes vía Agent tool reportan al completar

### 5. Sintetizar

- El script llama a Opus automáticamente al final
- Si usa Agent tool, Jeffrey lanza un agente sintetizador (model: "opus") con todos los outputs

### 6. Presentar y gestionar el output

Jeffrey presenta a Jorge:
- Ruta del documento: `.tmp/investigacion_YYYYMMDD_HHMMSS.md`
- La síntesis Opus directamente en pantalla
- Pregunta: "¿Lo guardamos en Obsidian o quieres hacer cambios primero?"

Si Jorge aprueba: `[DELEGATE:bibliotecaria]` para guardar en el vault.

## Outputs

- `.tmp/investigacion_YYYYMMDD_HHMMSS.md` — documento completo (hallazgos por investigador + síntesis)
- `.tmp/investigacion_YYYYMMDD_HHMMSS.json` — datos estructurados para procesamiento posterior

### Estructura del documento

```markdown
# Investigación: [Tema]
**Fecha**: YYYY-MM-DD | **Agentes**: N | **Pasos**: X
**Objetivo**: [objetivo]

---

## Hallazgos por Investigador

### 📊 Analista
**Paso 1: [instrucción]**
[output]

**Paso 2: [instrucción]**
[output]

### 🔍 Escéptico
[...]

---

## Síntesis (Opus)

### Hallazgos Clave
### Patrones Transversales
### Tensiones y Contradicciones
### Perspectivas Únicas
### Conclusión Sintetizada
### Líneas Abiertas
```

## Modelos

| Rol | Modelo |
|-----|--------|
| Investigadores (×N) | `claude-sonnet-4-6` |
| Sintetizador final | `claude-opus-4-7` |

## Edge cases

- **Agente falla**: continuar con los demás. El documento anota el fallo. El sintetizador opera con los que completaron.
- **Más de 8 agentes**: avisar a Jorge. Proponer 8 (perspectivas únicas) o activar `--uniforme` para N sin límite.
- **Sin necesidad de internet**: usar el script Python directamente.
- **Con necesidad de internet**: Jeffrey orquesta con el Agent tool (WebSearch y WebFetch disponibles).
- **Sin objetivo claro**: preguntar antes de ejecutar — el objetivo es clave para que Opus sintetice bien.
- **Confirmación Opus siempre obligatoria**: nunca ejecutar sin confirmar el uso de Opus con Jorge.
