# Directiva: Backup automático a GitHub

## Objetivo

Mantener una copia de seguridad diaria del proyecto en GitHub.
El backup se ejecuta automáticamente a las 20:55 todos los días, sin intervención manual.

## Arquitectura del sistema

```
execution/backup.sh              ← script principal
execution/com.evolve.jeffrey.backup.plist  ← programación macOS (launchd)
.tmp/backup_log.txt              ← log de ejecuciones
.tmp/backup_error.log            ← errores del sistema operativo
```

Variables en `.env` necesarias:
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx   ← token personal de GitHub
GITHUB_USERNAME=tu_usuario       ← nombre de usuario de GitHub
```

Repositorio: `https://github.com/$GITHUB_USERNAME/master-ia-evolve`

---

## SETUP INICIAL (hacer una sola vez)

### Paso 1 — Crear cuenta en GitHub

1. Ir a https://github.com
2. Clic en "Sign up"
3. Usar el email `iagen@evolve.es`
4. Elegir plan gratuito

### Paso 2 — Crear el repositorio

1. Una vez dentro de GitHub, clic en "+" > "New repository"
2. Nombre: `sistema-agentico-evolve`
3. Visibilidad: **Private** (obligatorio)
4. NO marcar "Add a README file"
5. Clic en "Create repository"
6. Copiar la URL HTTPS que aparece (algo como `https://github.com/TUUSUARIO/sistema-agentico-evolve.git`)

### Paso 3 — Crear token de acceso (PAT)

1. GitHub > clic en tu avatar > Settings
2. Scroll hasta abajo > "Developer settings"
3. "Personal access tokens" > "Tokens (classic)"
4. "Generate new token (classic)"
5. Nota: "Jeffrey backup"
6. Expiración: "No expiration" (o 1 año si prefieres)
7. Marcar solo: `repo` (acceso completo a repositorios)
8. "Generate token"
9. **Copiar el token** — solo se muestra una vez

### Paso 4 — Añadir credenciales al .env

Abrir `.env` y añadir estas dos líneas:
```
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX
GITHUB_USERNAME=tu_usuario_de_github
```

### Paso 5 — Inicializar el repositorio local

Abrir Terminal y ejecutar estos comandos en orden:

```bash
cd "/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup"

# Inicializar git
git init

# Configurar identidad (solo la primera vez)
git config user.name "Jorge Valero"
git config user.email "iagen@evolve.es"

# Primer commit
git add -A
git commit -m "init: primer backup del sistema Jeffrey"

# Conectar con GitHub (sustituir TUUSUARIO por tu usuario real)
git remote add origin https://github.com/TUUSUARIO/sistema-agentico-evolve.git
git branch -M main

# Subir todo a GitHub
git push -u origin main
```

### Paso 6 — Instalar la tarea programada (launchd)

En Terminal, ejecutar:

```bash
cp "/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup/execution/com.evolve.jeffrey.backup.plist" ~/Library/LaunchAgents/

launchctl load ~/Library/LaunchAgents/com.evolve.jeffrey.backup.plist
```

Verificar que está activo:
```bash
launchctl list | grep evolve
```
Debe aparecer `com.evolve.jeffrey.backup` en la lista.

---

## Operación diaria

El sistema funciona sin intervención. A las 20:55 cada día:
1. macOS lanza `execution/backup.sh`
2. El script detecta los archivos modificados
3. Hace commit con timestamp (`backup: 2026-05-11 20:55 (N archivos)`)
4. Hace push a GitHub
5. Registra el resultado en `.tmp/backup_log.txt`

**Si no hay cambios:** el script termina sin hacer commit (no crea commits vacíos).

---

## Verificación del estado

Para ver los últimos backups:
```bash
tail -20 "/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup/.tmp/backup_log.txt"
```

Para ver el historial de commits en GitHub:
- Ir a `https://github.com/TUUSUARIO/sistema-agentico-evolve/commits/main`

---

## Cómo restaurar un archivo

Si se borra o corrompe un archivo accidentalmente:

1. Ir al repositorio en GitHub
2. Navegar al archivo en cuestión
3. Clic en "History" para ver versiones anteriores
4. Clic en el commit con la versión correcta
5. Clic en "Raw" y copiar el contenido, o usar el botón de descarga

Alternativa desde Terminal:
```bash
cd "/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup"

# Ver historial
git log --oneline -20

# Restaurar un archivo concreto desde un commit anterior
git checkout HASH_DEL_COMMIT -- ruta/al/archivo.md
```

---

## Qué se guarda y qué no

**Se guarda** (todo el proyecto):
- Directivas, skills, agents, memory, execution, context
- CLAUDE.md, HEARTBEAT.md, DREAMS.md, SOUL.md, IDENTITY.md
- dashboard.html
- Scripts Python

**No se guarda** (excluido por .gitignore):
- `.env` — API keys y tokens (NUNCA al repositorio)
- `.tmp/` — archivos temporales de trabajo
- `__pycache__/` — caché de Python
- `.DS_Store` — metadatos de macOS

---

## Resolución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| "ERROR: Faltan GITHUB_TOKEN..." | Variables no en .env | Añadir GITHUB_TOKEN y GITHUB_USERNAME a .env |
| "ERROR: No hay repositorio git..." | No se hizo git init | Ejecutar Paso 5 del setup |
| El backup no se ejecuta solo | launchd no cargado | Ejecutar Paso 6 del setup |
| "Authentication failed" | Token expirado o incorrecto | Generar nuevo token en GitHub y actualizar .env |

---

## Activación por Jeffrey

Jeffrey puede verificar el estado del último backup como parte del briefing diario:

```
tail -5 .tmp/backup_log.txt
```

Si el último registro tiene más de 24h o contiene "ERROR", notificarlo a Jorge.
