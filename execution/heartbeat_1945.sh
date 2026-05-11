#!/bin/bash
# Disparador del HEARTBEAT diario de las 19:45
# Lanzado por cron — no editar la ruta del proyecto

PROJECT_DIR="/Users/jvalero/Desktop/JORGE/Flujos de Trabajo Agenticos/Mi Startup"
LOG_FILE="/tmp/heartbeat_1945.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Buscar el binario de Claude mas reciente instalado en VSCode
CLAUDE_BIN=$(ls -t ~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | head -1)

if [ -z "$CLAUDE_BIN" ]; then
    echo "[$TIMESTAMP] ERROR: Claude binary no encontrado" >> "$LOG_FILE"
    exit 1
fi

echo "[$TIMESTAMP] Iniciando HEARTBEAT 19:45..." >> "$LOG_FILE"

cd "$PROJECT_DIR" && "$CLAUDE_BIN" \
    --print "HEARTBEAT diario-19:45-Madrid" \
    --output-format text \
    >> "$LOG_FILE" 2>&1

echo "[$TIMESTAMP] HEARTBEAT completado" >> "$LOG_FILE"
