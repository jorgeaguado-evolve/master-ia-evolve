---
name: Crear Agente
description: Crea un agente nuevo completo (SOUL, IDENTITY, CLAUDE, skill, slash command y entradas en índices) a partir de un input mínimo: nombre, funciones y posición jerárquica.
---

# Skill: Crear Agente

## Qué hace

Construye la estructura completa de un agente especializado a partir de tres datos básicos:
- **Nombre** del agente (y nombre del personaje si tiene uno)
- **Funciones** — qué tareas cubre, qué dominio gestiona
- **Jerarquía** — relación con Jeffrey, con otros agentes y con Jorge

A partir de eso infiere personalidad, permisos, tono y protocolo de arranque siguiendo los patrones establecidos en el proyecto.

## Cuándo activar

- Jorge dice "crea un agente para X"
- Jorge dice "necesito un agente que haga Y"
- Jorge usa `/crear-agente`

---

## Protocolo de ejecución

### Paso 1 — Recoger el input mínimo

Si Jorge no ha proporcionado los tres datos, preguntar de una vez (no en tres mensajes separados):

```
Necesito tres cosas para crear el agente:
1. Nombre (y nombre de personaje si quieres darle uno)
2. Funciones — qué hace, qué dominio cubre
3. Jerarquía — ¿quién lo invoca? ¿puede Jorge llamarlo directamente? ¿colabora con algún agente existente?
```

Si el input ya viene en el mensaje (`$ARGUMENTS` o cuerpo del mensaje), extraer los tres datos sin preguntar.

### Paso 2 — Inferir lo que falta

Con los tres datos, derivar:

| Qué inferir | Cómo |
|-------------|------|
| Personalidad | Del dominio. Ej: análisis → metódico, frío; comunicación → claro, empático |
| Tono | Del dominio y la relación con Jorge |
| Permisos sin confirmación | Lo que es reversible y local (leer, escribir archivos propios) |
| Permisos con confirmación | Lo que es irreversible, externo o afecta a más de un sistema |
| Modelo de subagentes | Haiku para tareas efímeras, Sonnet para síntesis — ver `directives/model_routing.md` |
| Identificador | Nombre en kebab-case minúsculas, sin tildes (ej: `gestor-leads`, `analista`) |

### Paso 3 — Presentar resumen antes de crear

Antes de escribir ningún archivo, mostrar a Jorge:

```
## Agente a crear: [Nombre]

**Identificador:** `[kebab-case]`
**Carpeta:** `agents/[NombreCarpeta]/`
**Slash command:** `/[identificador]`

**Funciones:**
- [lista derivada del input]

**Personalidad inferida:** [2 líneas]
**Puede hacer sin permiso:** [lista]
**Requiere confirmación:** [lista]

**Relaciones:**
- Jeffrey → delega con `[DELEGATE:[id]]` cuando: [condición]
- [otros agentes si aplica]: [relación]
- Jorge → puede invocar directamente: sí/no

¿Creo con esta configuración? (responde OK o ajusta lo que no cuadre)
```

### Paso 4 — Crear archivos (solo con OK de Jorge)

Crear en este orden:

#### 4.1 — Carpeta del agente

```
agents/[NombreCarpeta]/
  SOUL.md
  IDENTITY.md
  CLAUDE.md
  directives/
    README.md     ← placeholder
  memory/
    README.md     ← placeholder
```

**SOUL.md** — incluir siempre:
- Identidad central (qué es, qué no es)
- Tono y voz (2-3 reglas concretas)
- Cómo piensa y toma decisiones (orden de pasos)
- Sección explícita `## Lo que [Nombre] NO es` con 4-5 items

**IDENTITY.md** — incluir siempre:
- Nombre, rol, identificador de delegación
- Tabla de accesos a recursos (qué puede tocar y con qué permisos)
- Lista de permisos sin confirmación
- Lista de permisos con confirmación
- Tabla de operaciones con directiva correspondiente

**CLAUDE.md** — incluir siempre:
- Bloque de identidad (quién es, nunca presentarse como Claude)
- Protocolo de inicio de sesión (qué leer al arrancar, en qué orden)
- Tabla de operaciones y directivas
- Formato de respuesta (longitud, estilo, sin intro/cierre)
- Tabla de modelos para subagentes
- Protocolo de fin de sesión (qué actualizar en memory/)

**directives/README.md**:
```markdown
# directives/ — [Nombre]
Directivas específicas de [Nombre]. Se crean cuando se define una operación nueva.
```

**memory/README.md**:
```markdown
# memory/ — [Nombre]
Memoria persistente de [Nombre]. Los archivos se crean durante la operación.
```

#### 4.2 — Skill

Crear `skills/[identificador]/Skill.md` con:
```yaml
---
name: [Nombre legible]
description: [cuándo activar, max 200 chars — lo usa Claude para decidir]
---
```
Cuerpo: qué hace, cuándo activar, cómo delegar, operaciones disponibles.

#### 4.3 — Slash command

Crear `.claude/commands/[identificador].md`:
```markdown
Activa a [Nombre] para [dominio].

Lee `agents/[NombreCarpeta]/CLAUDE.md` y `agents/[NombreCarpeta]/IDENTITY.md` para asumir el rol completamente.

Atiende la solicitud del usuario según las operaciones disponibles: [lista].

Si el usuario no especifica la operación, inferirla del contexto.

Argumento recibido: $ARGUMENTS
```

#### 4.4 — Actualizar índices (los tres, siempre)

1. **`agents/AGENTS.md`** — añadir fila en la tabla de agentes especializados:
   `| [Nombre con link] | \`[id]\` | [dominio en una línea] |`

2. **`skills/SKILLS.md`** — añadir fila en la tabla:
   `| [Nombre] | [ruta/Skill.md] | [descripción] |`

3. **`CLAUDE.md` (raíz)** — añadir fila en la tabla de agentes especializados:
   `| [Nombre con link] | \`[id]\` | [dominio] |`
   Y añadir el trigger de delegación en la lista de "cuándo delegar".

### Paso 5 — Confirmar

Una vez creados todos los archivos:

```
Agente [Nombre] creado.

Archivos creados:
- agents/[Carpeta]/SOUL.md, IDENTITY.md, CLAUDE.md
- skills/[id]/Skill.md
- .claude/commands/[id].md

Índices actualizados: AGENTS.md, SKILLS.md, CLAUDE.md raíz

Slash command listo: /[id]
```

---

## Reglas invariables

1. Nunca crear el agente sin presentar el resumen del paso 3 primero.
2. El identificador (kebab-case) debe ser idéntico en: nombre de carpeta del agente, skill, comando y entradas en índices.
3. Si el nombre de carpeta del agente usa mayúsculas (ej: `Bibliotecaria`), el identificador de delegación y el comando siempre en minúsculas (ej: `bibliotecaria`).
4. Siempre crear los tres archivos de índice. Nunca omitir uno.
5. El slash command es obligatorio. Sin él, el agente no es invocable directamente.

## Edge cases

- **Nombre ya existe**: verificar con `ls agents/` antes de crear. Si existe, avisar a Jorge y preguntar si es una actualización o un agente distinto.
- **Funciones solapan con un agente existente**: señalarlo en el resumen del paso 3. No bloquear, pero informar.
- **Jerarquía no especificada**: asumir que Jeffrey puede delegarle y Jorge puede invocarlo directamente. Indicarlo en el resumen.
- **Input muy escueto** (solo el nombre): pedir las funciones antes de inferir nada.
