# dashboard.md — Mantenimiento del dashboard de capacidades

## Objetivo

Mantener `dashboard.html` sincronizado con el estado real del proyecto en todo momento.
El dashboard es la fuente visual de verdad del sistema: si algo cambia en el proyecto, cambia aqui.

## Cuándo actualizar (actuar sin pedir permiso)

| Cambio en el proyecto | Que actualizar en dashboard.html |
|---|---|
| Nueva skill o capacidad en `skills/` | Anadir nodo hijo al dominio correspondiente en `DATA` |
| Modificar nombre o descripcion de una capacidad | Actualizar `name` / `description` del nodo en `DATA` |
| Cambiar el estado de una capacidad | Actualizar `status` del nodo: `active` / `in-progress` / `planned` |
| Nueva directiva en `directives/` | Evaluar si representa una nueva capacidad visible en el dashboard |
| Modificar HEARTBEAT.md | Actualizar el array `SCHEDULED_TASKS` en el dashboard |
| MCP autenticado (Calendar, Drive, etc.) | Cambiar `status: 'in-progress'` o `status: 'planned'` a `status: 'active'` |
| Nuevo modulo completo (nueva skill de dominio) | Anadir nuevo objeto hijo en `DATA.children` |
| Retirar una capacidad | No eliminar el nodo — cambiar `status` a `planned` |

## Proceso de actualización

1. Abrir `dashboard.html`
2. Localizar el objeto afectado en el array `DATA.children` (buscar por `id`)
3. Editar el campo correspondiente
4. Si el cambio afecta tareas programadas: localizar `SCHEDULED_TASKS` y actualizar
5. Verificar que el HTML sigue siendo valido (sin comas sueltas ni llaves mal cerradas)

## Estructura del objeto DATA (referencia rapida)

```javascript
// Modulo (nivel 1)
{
  id: "string-unico",        // no cambiar una vez creado
  name: "Nombre visible",
  subtitle: "Subtitulo breve",
  status: "active",          // active | in-progress | planned
  color: "#hexcolor",
  icon: "emoji",
  description: "Descripcion completa para el panel lateral.",
  children: [ /* capacidades */ ]
}

// Capacidad (nivel 2)
{
  id: "modulo-N",            // patron: id-del-modulo + numero
  name: "Nombre de la capacidad",
  status: "active",          // active | in-progress | planned
  description: "Descripcion de lo que hace esta capacidad concretamente."
}
```

## Estructura de SCHEDULED_TASKS (referencia rapida)

```javascript
{
  id: 'hb-identificador',
  name: 'Nombre legible',
  schedule: 'daily',          // daily | weekly | monthly
  freq: 'diario',             // para el badge visual
  time: 'Momento del dia',    // "Manana", "20:00 Madrid", "Lunes", etc.
  cronExpr: 'daily-morning',  // daily-morning | daily-20:00 | weekly-monday | weekly-friday | weekly-sunday | monthly
  agent: 'nombre_agente',
  skill: 'skill1 + skill2',
  description: 'Descripcion de la tarea.',
  output: 'Que produce.',
  status: 'active',
}
```

## Colores de dominio (no cambiar sin razon)

| Modulo | Color |
|---|---|
| Gmail | #4285f4 |
| Google Calendar | #34a853 |
| Wiki / Obsidian | #9b59b6 |
| Clase | #e67e22 |
| Research | #1abc9c |
| HEARTBEAT | #f39c12 |
| Memoria | #e74c3c 	|
| Ejecucion | #546e7a |

## Reglas de estilo del dashboard

- Los `id` son estables: una vez creados no se cambian (son clave de seleccion en JS)
- Al añadir un modulo nuevo: elegir color que no exista ya, seguir el patron de iconos emoji
- Las descripciones van sin acentos ni caracteres especiales (evitar problemas de encoding)
- El orden de `DATA.children` determina la posicion radial: no reordenar sin motivo
