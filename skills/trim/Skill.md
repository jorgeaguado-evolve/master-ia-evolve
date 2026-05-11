---
name: Trim
description: Análisis de archivos base para detectar contenido extraíble y validar integridad referencial. Activar con /trim, cuando Jorge pida optimizar contexto, o en HEARTBEAT diario.
---

# Skill: Trim

## Qué hace
Analiza los archivos base del proyecto (CLAUDE.md, memory/*.md, SOUL.md, IDENTITY.md y otros del hot path) para detectar contenido extraíble, validar integridad referencial y acumular datos de uso.

## Cuándo activar
- Jorge dice `/trim`, "limpia los archivos", "optimiza el contexto", "están muy grandes los archivos de memoria"
- HEARTBEAT diario (modo `--solo-reporte`, sin modificar nada)
- Al final de sesión: registrar uso con `--registrar-uso`

## Cómo ejecutar

### Análisis completo (bajo demanda)
```
python execution/trim.py
```
Genera `.tmp/trim_report.md`, muestra candidatos y links rotos en pantalla, registra uso.

### Solo reporte (HEARTBEAT diario)
```
python execution/trim.py --solo-reporte
```
Genera `.tmp/trim_report.md` sin modificar nada ni registrar uso.

### Solo registrar uso (fin de sesión)
```
python execution/trim.py --registrar-uso CLAUDE.md memory/user.md ...
```
Añade entrada a `.tmp/trim_usage.json` con los archivos leídos en la sesión.

## Después del análisis

1. Mostrar el reporte al usuario (o resumirlo si es largo)
2. Para candidatos en **archivos modificables**: preguntar confirmación antes de extraer
3. Para candidatos en **archivos protegidos** (CLAUDE.md, SOUL.md, IDENTITY.md): mostrar como sugerencias, dejar la decisión a Jorge
4. Nunca modificar archivos protegidos automáticamente

## Herramientas
- `execution/trim.py` — script principal
- `execution/trim_config.json` — configuración (archivos a analizar, protegidos, umbrales)
- `.tmp/trim_report.md` — reporte generado
- `.tmp/trim_usage.json` — tracker de uso por sesión (base para decisiones tras 30 días)

## Heurísticas automáticas

| Patrón | Umbral | Acción propuesta |
|--------|--------|-----------------|
| Sección `## Edge cases` | > 8 líneas | Extraer a directiva específica |
| Tabla de contenido estático | > 6 filas | Extraer a archivo de referencia |
| Bloque de ejemplos | > 10 líneas | Extraer a apéndice o directiva |
| Sección similar en dos archivos | > 75% similitud | Consolidar y referenciar |

## Output esperado
- `.tmp/trim_report.md` con candidatos, links rotos y top secciones por tokens
- Resumen en pantalla: número de candidatos y links rotos
