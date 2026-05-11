---
name: Wiki
description: Gestión del wiki de conocimiento en Obsidian: ingest, consulta, lint y captura de ideas. Activar cuando Jorge mencione Obsidian, wiki, RAW, o pregunte sobre conocimiento acumulado.
---

# Skill: Wiki

## Qué hace
Gestión del wiki de conocimiento personal de Jorge en Obsidian.
Jeffrey mantiene el wiki: lee fuentes, escribe resúmenes, actualiza el índice y mantiene la coherencia interna.
Jorge lee el wiki y dirige qué analizar. Jorge no escribe en el wiki directamente.

## Rutas del sistema
- Vault: `/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Master Agentes IA/Master Agentes IA/`
- Wiki: `[vault]/wiki/`
- Fuentes: `[vault]/RAW/`
- Schema: `[vault]/wiki/schema.md`
- Index: `[vault]/wiki/index.md`
- Log: `[vault]/wiki/log.md`

## Herramientas requeridas
- Lectura y escritura de archivos Markdown
- Sin dependencia de APIs externas — opera sobre el sistema de archivos local

## Cuatro operaciones principales

### INGEST
Activar cuando Jorge quiere procesar una fuente nueva (archivo en RAW/).
Ejecutar directiva: `directives/wiki_ingest.md`

### QUERY
Activar cuando Jorge hace una pregunta que puede responderse desde el wiki.
Ejecutar directiva: `directives/wiki_query.md`

### LINT
Activar para revisión de salud del wiki. Frecuencia: semanal.
Ejecutar directiva: `directives/wiki_lint.md`

### IDEA CAPTURE
Activar cuando Jorge comparte una idea, reflexión o propuesta durante la conversación que debe quedar registrada en Obsidian.
Ejecutar directiva: `directives/idea_capture.md`
**Regla**: usar siempre subagente. Jeffrey nunca escribe directamente en Ideas/.

## Reglas invariables
1. Jeffrey escribe el wiki. Jorge lo lee y dirige.
2. Los archivos en `RAW/` son inmutables. Jeffrey nunca los modifica.
3. Toda operación genera una entrada en `wiki/log.md` con el prefijo correcto.
4. Toda creación o modificación de página actualiza `wiki/index.md`.
5. El frontmatter YAML es obligatorio en todas las páginas del wiki.
6. Las referencias cruzadas usan `[[wikilinks]]` de Obsidian.

## Edge cases
- **Fuente en formato no legible**: pedir a Jorge que copie el contenido en un archivo de texto en `RAW/`
- **Contradicción entre páginas del wiki**: no resolver unilateralmente. Anotar en `wiki/log.md` y consultar con Jorge.
- **Página desactualizada**: marcar `confianza: baja` en el frontmatter, anotar en el log antes de actualizar
- **Pregunta sin cobertura en el wiki**: informar a Jorge e indicar qué fuentes habría que ingerir
- **Fuente en inglés**: procesar en inglés, escribir el resumen en español
