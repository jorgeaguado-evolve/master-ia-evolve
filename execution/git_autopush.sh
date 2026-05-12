#!/bin/bash

REPO="/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup"
ENV_FILE="$REPO/.env"
LOG="/tmp/jeffrey_autopush.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Iniciando autopush" >> "$LOG"

# Leer GITHUB_TOKEN del .env
if [ -f "$ENV_FILE" ]; then
    GITHUB_TOKEN=$(grep '^GITHUB_TOKEN=' "$ENV_FILE" | cut -d= -f2 | tr -d '[:space:]')
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') — ERROR: GITHUB_TOKEN no encontrado en .env" >> "$LOG"
    exit 1
fi

cd "$REPO" || exit 1

# Configurar remote con token
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/jorgeaguado-evolve/master-ia-evolve.git"

# Comprobar si hay cambios
if git status --porcelain | grep -q .; then
    FECHA=$(date '+%Y-%m-%d %H:%M')
    git add -A
    git commit -m "chore: autopush diario — $FECHA"
    echo "$(date '+%Y-%m-%d %H:%M:%S') — Commit creado: $FECHA" >> "$LOG"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') — Sin cambios, solo push" >> "$LOG"
fi

# Push siempre
git push origin main >> "$LOG" 2>&1
echo "$(date '+%Y-%m-%d %H:%M:%S') — Push completado" >> "$LOG"
