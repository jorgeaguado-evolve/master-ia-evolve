# Wiki: Ingest de fuente nueva

## Objetivo

Procesar una fuente nueva e integrarla en el wiki delegando el trabajo pesado a un subagente, para preservar el contexto principal de Jeffrey.

## Inputs

- Ruta de la fuente: proporcionada por Jorge
- Nivel de profundidad (opcional):
  - `rapido`: solo resumen ejecutivo y entrada en index
  - `estandar` (por defecto): resumen completo + actualizar conceptos y entidades existentes
  - `profundo`: estandar + crear nuevas paginas de concepto si aparecen terminos nuevos relevantes

---

## Protocolo Jeffrey (contexto principal)

Jeffrey NO lee la fuente ni los archivos del wiki. Solo hace esto:

1. Identificar la ruta de la fuente y el nivel de profundidad (default: `estandar`)
2. Construir el briefing para el subagente usando la plantilla de abajo, sustituyendo `{{RUTA_FUENTE}}` y `{{NIVEL}}`
3. Lanzar el subagente con `Agent(subagent_type="general-purpose", prompt=<briefing>)`
4. Cuando el subagente reporta: transmitir el resumen a Jorge en 3-5 lineas

Jeffrey no lee ningun archivo del wiki durante este proceso. Todo lo hace el subagente.

---

## Plantilla de briefing para el subagente

```
Eres un agente de ingestion de wiki. Tu tarea es procesar una fuente nueva e integrarla en el wiki de conocimiento personal de Jorge Aguado.

VAULT ROOT: /Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Master Agentes IA/Master Agentes IA/

FUENTE A INGESTAR: {{RUTA_FUENTE}}
NIVEL DE PROFUNDIDAD: {{NIVEL}}

---

PASOS A EJECUTAR (en orden):

1. Lee `wiki/schema.md` — carga las reglas de estructura y frontmatter
2. Lee la fuente completa en la ruta indicada
3. Lee `wiki/index.md` — identifica paginas existentes relacionadas con el tema
4. Lee las paginas relacionadas identificadas (para evitar duplicados y detectar conexiones)
5. Comprueba `wiki/log.md` — verifica que esta fuente no haya sido ingestada antes. Si ya existe entrada para esta fuente: detente y reporta "FUENTE YA INGESTADA" con la fecha del ingest previo
6. Escribe la pagina de resumen en `wiki/` siguiendo el schema:
   - Nombre: `resumen-[nombre-corto-descriptivo].md`
   - Frontmatter completo: tipo, creado, actualizado, fuentes, tags, confianza
   - En el campo `fuentes`: incluir siempre el nombre del archivo original Y cualquier URL de origen que aparezca en el contenido del archivo (para poder recuperar la fuente aunque se elimine el RAW)
   - Estructura segun tipo de pagina en schema.md (resumen ejecutivo, contexto, ideas principales, por que importa para Jorge/Evolve, conexiones, citas destacadas)
7. Si nivel es `estandar` o `profundo` y aparecen conceptos nuevos relevantes:
   - Si existe pagina de concepto: actualiza anadiendo referencia
   - Si no existe y el concepto aparece en 2+ paginas del wiki: crea `concepto-[nombre].md`
   - Si solo aparece en esta fuente: anotalo como placeholder en la pagina de resumen
8. Si aparecen entidades (personas, empresas, proyectos) que ya estan en el wiki:
   - Actualiza la pagina de entidad existente anadiendo referencia a esta fuente
9. Actualiza `wiki/index.md`:
   - Anade la nueva pagina en la categoria correcta
   - Incrementa `total_paginas` en el frontmatter
   - Actualiza la fecha `actualizado`
10. Anade entrada en `wiki/log.md`:
    - Formato: `## [YYYY-MM-DD] ingest | [Titulo de la fuente]`
    - Incluye: fuente, paginas creadas, paginas actualizadas, tags principales
11. Elimina el archivo original de `RAW/` con la herramienta Bash (`rm`):
    - Solo si los pasos 6, 9 y 10 se completaron sin error
    - Si algo fallo antes: NO eliminar el archivo, incluirlo como issue en el reporte

REGLAS INVARIABLES:
- Los archivos en `RAW/README-raw.md` son permanentes — no eliminar nunca.
- Las referencias cruzadas usan [[wikilinks]] de Obsidian.
- Si el contenido contradice una pagina existente: anota la contradiccion en ambas paginas y en el log. No resuelvas sin consultar.
- Si la fuente esta en ingles: escribe el resumen en espanol.
- La fecha de hoy es {{FECHA_HOY}}.

FORMATO DEL REPORTE FINAL (maximo 200 palabras):
- Paginas creadas: lista con nombre y una frase descriptiva
- Paginas actualizadas: lista
- Issues encontrados: cualquier contradiccion, ambiguedad o decision tomada
- Tags principales del ingest
```

---

## Edge cases

- **Fuente es solo una URL**: pedir a Jorge que copie el contenido en un archivo en `RAW/` antes de ingestar; anotar la URL en el nombre del archivo o dentro del archivo para que el subagente la capture en el frontmatter
- **Nivel no especificado**: usar `estandar`
- **Subagente reporta FUENTE YA INGESTADA**: informar a Jorge con la fecha del ingest previo y preguntar si hay version actualizada
- **Subagente reporta contradiccion**: transmitir el issue a Jorge antes de resolver
- **Subagente falla o reporta error**: intentar una vez mas con el mismo briefing; si falla de nuevo, reportar el error a Jorge con detalle
