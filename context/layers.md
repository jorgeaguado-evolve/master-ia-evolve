# Cadena de resolución de contexto

Define la jerarquía que Jeffrey sigue para resolver qué contexto aplicar cuando hay información en múltiples niveles. Inspirado en el modelo de resolución de configuración de OpenClaw.

## Jerarquía (mayor prioridad primero)

```
Capa 1: .tmp/session_context.md     ← sesión actual (efímero, se regenera)
Capa 2: memory/*.md                  ← preferencias y recuerdos del usuario
Capa 3: agents/<perfil>_agent.md     ← comportamiento del agente activo
Capa 4: skills/<skill>.md            ← proceso concreto de la capacidad usada
Capa 5: CLAUDE.md                    ← defaults globales e identidad
```

## Reglas de resolución

1. Si hay conflicto entre capas, gana la capa de menor número (mayor prioridad).
2. La Capa 1 es volátil: no persiste entre sesiones. Sólo aplica durante la sesión activa.
3. La Capa 2 puede tener entradas con `confidence: low` — verificar antes de aplicar.
4. Las Capas 3 y 4 se activan juntas cuando Jeffrey entra en un modo especializado.
5. La Capa 5 siempre está activa como base.

## Ejemplo de resolución

Tarea: "redacta un email para un alumno del máster"

1. `.tmp/session_context.md` — ¿hay instrucciones específicas de esta sesión? No.
2. `memory/user.md` — tono de Jorge: directo, sin rodeos, en español. Aplica.
3. `agents/email_agent.md` — no enviar directamente, crear draft primero. Aplica.
4. `skills/email.md` — proceso de redacción: leer contexto, redactar, presentar borrador. Aplica.
5. `CLAUDE.md` — identidad Jeffrey, español siempre. Aplica como base.

Resultado: Jeffrey redacta en español, directo, sin relleno, crea draft, presenta antes de enviar.

## Cuándo releer capas

- Inicio de sesión: leer Capas 2, 3 (si hay perfil activo), 5
- Al activar un nuevo perfil de agente: leer Capa 3
- Al ejecutar un skill específico: leer Capa 4
- Si hay instrucción en `.tmp/`: leer Capa 1 primero
