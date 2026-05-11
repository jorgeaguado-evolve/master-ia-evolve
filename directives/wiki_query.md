# Wiki: Query de consulta

## Objetivo

Responder una pregunta de Jorge usando el wiki como base de conocimiento, con opcion de archivar la sintesis como nueva pagina.

## Inputs

- Pregunta o tema de Jorge
- Alcance (opcional):
  - `wiki` (por defecto): buscar solo en el wiki
  - `ampliado`: wiki + busqueda web con la skill de research

## Herramientas

Lectura de `wiki/index.md` y paginas relevantes.
Web search (solo si Jorge especifica alcance ampliado o si el wiki no tiene respuesta suficiente).

## Pasos

1. Leer `wiki/index.md` para identificar paginas potencialmente relevantes
2. Leer las paginas relevantes identificadas
3. Si el wiki no cubre el tema: informar a Jorge e indicar que fuentes habria que ingerir para cubrirlo
4. Si el wiki cubre el tema parcialmente: indicarlo en la respuesta ("esto es lo que tenemos; falta X")
5. Sintetizar la respuesta usando lo que esta en el wiki. Citar las paginas usadas con `[[wikilinks]]`
6. Presentar la respuesta a Jorge: primero la respuesta, luego las fuentes del wiki usadas
7. Preguntar a Jorge si quiere archivar la sintesis como nueva pagina del wiki:
   - Si si: crear `sintesis-[tema].md` con frontmatter correcto, actualizar index, entrada en log
   - Si no: no crear ningun archivo adicional

## Formato de respuesta

```
[Respuesta directa en bullets o parrafos segun complejidad]

Fuentes usadas del wiki:
- [[nombre-pagina-1]]
- [[nombre-pagina-2]]
```

## Edge cases

- **Wiki vacio o con muy pocas paginas**: indicarlo y proponer que fuentes ingerir primero
- **Pregunta requiere informacion muy reciente**: ejecutar web search con skill research y proponer ingerir el resultado como nueva fuente
- **Contradiccion entre dos paginas del wiki**: presentar ambas versiones, indicar la contradiccion, no elegir unilateralmente
- **Pregunta muy amplia**: pedir a Jorge que la acote o dividirla en subpreguntas
