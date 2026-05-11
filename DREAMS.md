# DREAMS.md — Consolidación de memoria

DREAMS es el proceso semanal por el que Jeffrey convierte notas diarias efímeras en recuerdos de largo plazo.

Inspirado en cómo el cerebro procesa y consolida durante el sueño lo que aprendió durante el día.

---

## Cuándo ejecutar

Cada domingo (o cuando el HEARTBEAT lo active).
También se puede lanzar manualmente: "Jeffrey, ejecuta DREAMS".

---

## Proceso

### Paso 1 — Recopilar
Leer todos los archivos en `memory/daily/` con más de 1 día de antigüedad.

### Paso 2 — Analizar
Para cada archivo de notas diarias, identificar:
- Decisiones tomadas que siguen siendo válidas
- Preferencias de Jorge que se confirmaron o surgieron
- Errores cometidos que no están ya en `memory/errors.md`
- Contexto de proyecto que pertenece a `memory/project_*.md`
- Cualquier dato estable sobre Jorge que actualice `memory/user.md`

### Paso 3 — Consolidar
Escribir o actualizar los archivos de memoria long-term correspondientes:
- Preferencias o comportamiento de Jorge → `memory/user.md`
- Correcciones o validaciones → nuevo `memory/feedback_*.md`
- Contexto de proyecto → nuevo `memory/project_*.md`
- Errores → `memory/errors.md`

Actualizar el índice `memory/MEMORY.md` si se crearon archivos nuevos.

### Paso 4 — Limpiar
Eliminar los archivos de `memory/daily/` procesados (más de 7 días de antigüedad).
Mantener siempre el de hoy y el de ayer.

### Paso 5 — Registrar
Añadir una línea al final de este archivo con la fecha y un resumen de lo consolidado.

---

## Historial de consolidaciones

| Fecha | Archivos procesados | Qué se consolidó |
|-------|---------------------|------------------|
| 2026-05-04 | (inicio del sistema) | Primera sesión — arquitectura DOES implementada |

---

## Reglas

- Si una nota diaria no contiene nada consolidable, simplemente eliminarla.
- No duplicar recuerdos que ya existen en memory/.
- Si hay duda sobre si algo es permanente o efímero: dejarlo en daily hasta la próxima semana.
- DREAMS nunca modifica `memory/errors.md` para marcar errores como resueltos — eso lo hace Jeffrey explícitamente cuando Jorge confirma la corrección.
