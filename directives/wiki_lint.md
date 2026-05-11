# Wiki: Lint de salud

## Objetivo

Revisar el estado del wiki y detectar problemas: paginas huerfanas, afirmaciones desactualizadas, referencias rotas, contradicciones y oportunidades de mejora.

## Inputs

Ninguno obligatorio. Opera sobre el estado actual del wiki completo.

## Herramientas

Lectura de todos los archivos en `wiki/`.
Escritura en `wiki/log.md` (solo para registrar el resultado del lint).

## Pasos

1. Leer `wiki/index.md` -- cargar lista completa de paginas registradas
2. Verificar que cada pagina listada en el index existe como archivo real en `wiki/`
3. Para cada pagina del wiki, verificar:
   - Frontmatter completo: tipo, creado, actualizado, fuentes, tags, confianza
   - Al menos un `[[wikilink]]` saliente a otra pagina del wiki
   - La fecha `actualizado` no tiene mas de 90 dias sin revision
4. Verificar que cada pagina del index aparece referenciada en al menos otra pagina (detectar huerfanas)
5. Verificar que los `[[wikilinks]]` en cada pagina apuntan a archivos que existen (detectar referencias rotas)
6. Identificar terminos que aparecen en 3+ paginas sin tener su propia pagina de concepto
7. Identificar entidades que aparecen en 2+ paginas sin tener su propia pagina de entidad
8. Verificar que `wiki/index.md` tiene el `total_paginas` correcto
9. Generar informe de lint con estas secciones:
   - Paginas huerfanas (ninguna otra las enlaza)
   - Referencias rotas (wikilinks a paginas que no existen)
   - Paginas desactualizadas (mas de 90 dias sin revision)
   - Conceptos sin pagina propia (aparecen en 3+ paginas)
   - Entidades sin pagina propia (aparecen en 2+ paginas)
   - Oportunidades: temas con muchas referencias que podrian merecer una sintesis
10. Presentar el informe a Jorge con acciones concretas propuestas para cada problema
11. Ejecutar las correcciones que Jorge apruebe
12. Anadir entrada en `wiki/log.md`:
    - Formato: `## [YYYY-MM-DD] lint | Revision de salud del wiki`
    - Contenido: numero de paginas revisadas, problemas encontrados, acciones tomadas

## Frecuencia

Semanal (HEARTBEAT semanal-domingo). Informe disponible para el briefing del lunes.

## Edge cases

- **Wiki con menos de 5 paginas**: ejecutar el lint igualmente pero indicar que los resultados son limitados con tan pocas paginas
- **Contradicciones detectadas entre paginas**: no resolverlas sin consultar a Jorge. Anotar y presentar ambas versiones.
- **Archivos en RAW/ sin ingerir**: mencionarlo como oportunidad en el informe. No ingerir automaticamente.
- **Paginas con `confianza: baja`**: listarlas como prioridad para actualizacion
