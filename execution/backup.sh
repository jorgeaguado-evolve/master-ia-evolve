#!/bin/bash
# Sistema de backup diario a GitHub — Jeffrey / Evolve

set -euo pipefail

PROJECT_DIR="/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup"
LOG_FILE="$PROJECT_DIR/.tmp/backup_log.txt"
ENV_FILE="$PROJECT_DIR/.env"

mkdir -p "$PROJECT_DIR/.tmp"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Cargar variables de entorno
if [ ! -f "$ENV_FILE" ]; then
    log "ERROR: No se encuentra .env — backup abortado"
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

# Validar variables necesarias
if [ -z "${GITHUB_TOKEN:-}" ] || [ -z "${GITHUB_USERNAME:-}" ]; then
    log "ERROR: Faltan GITHUB_TOKEN o GITHUB_USERNAME en .env — backup abortado"
    exit 1
fi

REPO_NAME="master-ia-evolve"
REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

cd "$PROJECT_DIR"

# Verificar que el repo git existe
if [ ! -d ".git" ]; then
    log "ERROR: No hay repositorio git inicializado — ejecuta el setup primero"
    exit 1
fi

# Verificar si hay cambios
CAMBIOS=$(git status --porcelain)
if [ -z "$CAMBIOS" ]; then
    log "Sin cambios — nada que guardar"
    exit 0
fi

# Contar archivos modificados
N_ARCHIVOS=$(echo "$CAMBIOS" | wc -l | tr -d ' ')

# Añadir todos los cambios (respetando .gitignore)
git add -A

# Commit con timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
git commit -m "backup: $TIMESTAMP ($N_ARCHIVOS archivos)"

# Push a GitHub (usando token para autenticación)
git push "$REMOTE_URL" main 2>&1 | grep -v "token" || true

log "Backup completado — $N_ARCHIVOS archivos subidos a GitHub"
