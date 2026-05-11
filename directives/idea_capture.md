# Captura de ideas desde conversación

## Objetivo

Registrar en Obsidian una idea o conjunto de ideas que Jorge ha compartido verbalmente o por texto durante la sesión, delegando la escritura a un subagente para preservar el contexto de Jeffrey.

## Cuándo activar

- Jorge comparte una idea, reflexión o propuesta durante la conversación
- Jorge dice "anota esto", "guarda esta idea", "regístralo en Obsidian" o similar
- Jeffrey detecta que el mensaje de Jorge contiene ideas con potencial de implementación o reflexión futura

**Regla**: siempre que haya que escribir algo en el vault de Obsidian que no sea una sesión wiki (ingest/query/lint), usar esta directiva con subagente.

---

## Protocolo Jeffrey (contexto principal)

Jeffrey NO escribe directamente en Obsidian. Solo hace esto:

1. Extraer las ideas del mensaje de Jorge y organizarlas mentalmente
2. Construir el briefing para el subagente usando la plantilla de abajo, sustituyendo `{{IDEAS_RAW}}` con el contenido a capturar
3. Lanzar el subagente con `Agent(subagent_type="general-purpose", prompt=<briefing>)`
4. Cuando el subagente reporta: confirmar a Jorge en 2-3 líneas qué se ha guardado y dónde

---

## Plantilla de briefing para el subagente

```
Eres un agente de captura de ideas para el vault Obsidian de Jorge Aguado.

VAULT ROOT: /Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Master Agentes IA/Master Agentes IA/
IDEAS_FOLDER: [vault]/Ideas/
FECHA_HOY: {{FECHA_HOY}}

IDEAS A CAPTURAR:
{{IDEAS_RAW}}

---

PASOS A EJECUTAR (en orden):

1. Lee `Ideas/README.md` para entender las normas de la carpeta
2. Lee `Ideas/Inbox.md` para ver el estado actual del inbox
3. Decide el formato adecuado:
   - Si la idea es simple y cabe en una línea: añádela al Inbox.md como item de lista
   - Si la idea es compleja (múltiples componentes, preguntas abiertas, pasos posibles): crea una nota independiente en `Ideas/`
4. Si creas una nota independiente:
   - Nombre del archivo: kebab-case descriptivo, ej: `organizacion-agentica.md`
   - Frontmatter obligatorio: title, fecha, origen (de donde viene la idea), estado (sin procesar), tags
   - Estructura: sección de idea central, componentes/detalles, preguntas abiertas, siguientes pasos posibles
   - Al final: nota de captura con las palabras exactas o paráfrasis fiel de cómo Jorge lo describió
5. Si la nota es independiente, añade también una línea en `Ideas/Inbox.md` apuntando a ella con `[[nombre-archivo]]`

REGLAS:
- Captura fiel: no interpreta ni filtra. Registra lo que Jorge dijo, aunque parezca vago o incompleto.
- No descarta nada aunque parezca redundante o poco viable.
- Usa español.
- No modifiques ningún otro archivo del vault fuera de `Ideas/`.

FORMATO DEL REPORTE FINAL (máximo 100 palabras):
- Qué se ha creado o modificado (nombre del archivo y carpeta)
- Resumen de las ideas capturadas en 2-3 líneas
- Cualquier ambigüedad o decisión tomada
```

---

## Edge cases

- **Idea ya existe en el Inbox o como nota**: el subagente detecta el solapamiento, anota la conexión y no duplica
- **Jorge no da nombre ni contexto claro**: el subagente usa la fecha y el primer concepto mencionado como nombre de archivo
- **Ideas múltiples y heterogéneas**: el subagente puede crear una nota por grupo temático o agruparlas si hay coherencia temática clara
- **Jorge pide guardar en una carpeta específica**: respetar la indicación; si la carpeta no existe, crear la nota en `Ideas/` e informar
