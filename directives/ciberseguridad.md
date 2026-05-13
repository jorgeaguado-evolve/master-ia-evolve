# Directiva: Auditoría de ciberseguridad

**Agente responsable:** Flora la Auditora (`[DELEGATE:flora]`)
**Frecuencia:** Semanal (o bajo demanda)
**Duración estimada:** 10-15 minutos

---

## Objetivo

Revisar el estado de seguridad del proyecto Evolve / Jeffrey, detectar nuevas vulnerabilidades o cambios de estado en las conocidas, y proponer fixes con impacto mínimo en el funcionamiento del sistema.

---

## Inputs

- El proyecto completo en `/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup/`
- `agents/Flora/memory/audit_log.md` — auditorías anteriores (baseline de comparación)
- `agents/Flora/memory/rejected_items.md` — propuestas ya rechazadas (no volver a proponer)

---

## Proceso de auditoría

### Fase 1: Preparación (leer antes de escanear)

1. Leer `audit_log.md` — ¿qué estaba pendiente de la última auditoría?
2. Leer `rejected_items.md` — ¿qué no hay que volver a proponer?
3. Identificar cambios desde la última auditoría: `git log --since="7 days ago" --oneline`

### Fase 2: Escaneo por áreas

Ejecutar en paralelo con subagentes haiku cuando sea posible:

#### A. Scripts de ejecución (`execution/`)

```bash
# Buscar tokens hardcodeados o patrones de credencial
grep -rn "token\|password\|secret\|api_key\|Bearer\|ghp_\|sk-" execution/ --include="*.py" --include="*.sh" -i

# Buscar subprocess con shell=True (inyección de comandos)
grep -rn "shell=True" execution/

# Verificar permisos de scripts bash
ls -la execution/*.sh

# Verificar que __pycache__ no está rastreado
git ls-files execution/__pycache__/
```

#### B. Backup y tokens en git

```bash
# Verificar URL de remote (no debe contener token)
git remote -v

# Buscar tokens en historial git (últimos 10 commits)
git log -10 --all --full-diff -p -- execution/backup.sh | grep -i "token\|ghp_\|github"

# Verificar que .env no está rastreado
git ls-files .env
```

#### C. Configuración de Claude

```bash
# Listar permisos MCP activos
cat .claude/settings.json
cat .claude/settings.local.json 2>/dev/null

# Verificar que memory/ y .claude/ no están rastreados
git ls-files memory/ .claude/
```

#### D. Logs y ficheros temporales

```bash
# Verificar tamaño de logs (alerta si >1MB)
du -sh .tmp/*.log .tmp/*.json 2>/dev/null

# Contar líneas en historial de Telegram
wc -l .tmp/telegram_history.json 2>/dev/null
```

#### E. Telegram — verificación de ALLOWED_USER_ID

```bash
# Verificar que ALLOWED_USER_ID está configurado y no es 0
grep "ALLOWED_USER_ID" execution/telegram_bridge.py
# Verificar que el .env tiene un valor real (sin mostrar el valor)
grep -c "TELEGRAM_ALLOWED_USER_ID" .env
```

#### F. Dependencias Python

```bash
# Listar paquetes instalados con versión
pip list 2>/dev/null | grep -E "telegram|anthropic|openai|python-dotenv"

# Buscar imports de paquetes no declarados
grep -rh "^import\|^from" execution/*.py | sort -u
```

#### G. LaunchAgents activos

```bash
ls -la /Users/jvalero/Library/LaunchAgents/ | grep -i evolve
```

### Fase 3: Clasificación de hallazgos

Para cada hallazgo nuevo (no presente en `audit_log.md`):

| Criterio | Severidad |
|----------|-----------|
| Credencial o token expuesto, vector de ataque directo | CRITICO |
| Configuración incorrecta que puede ser explotada con acceso local o conocimiento del sistema | ALTO |
| Acumulación de datos, configuración subóptima, riesgo bajo pero real | MEDIO |
| Sin impacto práctico, solo buena práctica | BAJO / MONITORIZAR |

### Fase 4: Informe a Jorge

Estructura obligatoria del informe:

```
## Auditoría de seguridad — [FECHA]

### Implementar ahora (aprobación pendiente)
[Lista de fixes que Flora puede ejecutar inmediatamente si Jorge dice "adelante"]

### Revisar contigo
[Hallazgos que requieren una decisión de Jorge]

### Monitorizar
[Sin acción inmediata, registrado para seguimiento]

### Sin cambios respecto a auditoría anterior
[Confirmar qué sigue igual y en qué estado]

### Estado general
[3-5 líneas del estado de seguridad del proyecto]
```

### Fase 5: Implementación (solo con aprobación)

1. Jorge aprueba explícitamente los fixes de "Implementar ahora"
2. Flora ejecuta los cambios
3. Verifica que el sistema sigue funcionando
4. Registra en `audit_log.md`: fecha, fix aplicado, resultado

### Fase 6: Cierre

1. Actualizar `audit_log.md` con la auditoría completa
2. Actualizar `rejected_items.md` si Jorge rechazó algún punto nuevo
3. Informar a Jeffrey del resultado en 2 líneas

---

## Fixes de referencia (los más comunes)

### F-001: Token de GitHub en backup.sh

**Problema:** `git push "https://${GITHUB_TOKEN}@github.com/..."` expone el token en el proceso list.

**Fix aprobado cuando Jorge diga "adelante":**
```bash
# En lugar de pasar el token en la URL, usar credential store de git
git config credential.helper store
# O configurar SSH key para el repositorio y cambiar el remote a git@github.com:...
```
Alternativa más simple: usar `git push origin main` con el remote configurado previamente una vez con el token, sin pasarlo en cada ejecución.

### F-002: __pycache__ en git

**Fix:**
```bash
git rm -r --cached execution/__pycache__/
git commit -m "fix: eliminar __pycache__ del repositorio"
```

### F-003: Rotación de logs

**Fix:** Añadir al final de `backup.sh` o como cron separado:
```bash
# Truncar logs > 500 líneas
tail -500 .tmp/backup_log.txt > .tmp/backup_log.tmp && mv .tmp/backup_log.tmp .tmp/backup_log.txt
```

---

## Registro de cambios de esta directiva

| Fecha | Cambio |
|-------|--------|
| 2026-05-13 | Creación inicial |
