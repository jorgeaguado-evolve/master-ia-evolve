---
name: Bibliotecaria
description: Interfaz completa con el vault Obsidian a través de Amalia. Delegar toda operación sobre el vault: ingest, query, lint, captura de ideas, reorganización y optimización de wikilinks.
---

# Skill: Bibliotecaria

## Qué hace
Interfaz con el vault de Obsidian de Jorge a través de Amalia la Bibliotecaria.
Cubre todas las operaciones sobre el vault: ingest de fuentes, consulta de conocimiento, captura de ideas, revisión de salud y optimización de estructura y conexiones.

## Cuándo activar
- Jorge menciona Obsidian, vault, wiki, RAW, ingest
- Jorge hace una pregunta sobre conocimiento acumulado ("qué tenemos sobre X", "qué sabes de Y")
- Jorge dice "anota esto", "guarda esta idea", "registra en Obsidian"
- Jorge pide reorganizar o limpiar el vault
- Jeffrey detecta archivos en `RAW/` sin procesar
- Toca el lint semanal del wiki (HEARTBEAT semanal-domingo)
- Jeffrey necesita consultar o escribir en el vault para completar otra tarea

## Delegación

Esta skill se activa siempre delegando en Amalia la Bibliotecaria:

```
[DELEGATE:bibliotecaria]
```

Jeffrey no opera directamente sobre el vault. Todo pasa por Amalia.

## Agente responsable
`agents/Bibliotecaria/` — leer `CLAUDE.md` al activar

## Seis operaciones

| Operación | Cuándo | Directiva |
|-----------|--------|-----------|
| INGEST | Procesar nueva fuente en RAW/ | `directives/wiki_ingest.md` |
| QUERY | Consulta de conocimiento almacenado | `directives/wiki_query.md` |
| LINT | Revisión semanal de salud del wiki | `directives/wiki_lint.md` |
| IDEA CAPTURE | Guardar idea de Jorge en Obsidian | `directives/idea_capture.md` |
| VAULT REORG | Reorganizar estructura del vault | `agents/Bibliotecaria/directives/vault_reorg.md` |
| VAULT LINKS | Optimizar wikilinks y conexiones | `agents/Bibliotecaria/directives/vault_links.md` |

## Rutas del vault
```
Vault root: /Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Master Agentes IA/Master Agentes IA/
Wiki:       [vault]/wiki/
Fuentes:    [vault]/RAW/
Ideas:      [vault]/Ideas/
```

## Reglas invariables
1. Todo documento nuevo para ingestar va primero a `RAW/`. Sin excepción.
2. Los archivos en `RAW/` son inmutables. Amalia los lee, nunca los modifica.
3. Toda operación genera entrada en `wiki/log.md`.
4. Ningún movimiento o renombrado sin confirmación de Jorge.
5. Las referencias cruzadas usan `[[wikilinks]]` de Obsidian.
6. Información no se borra. Se reorganiza, segmenta o mejora.
