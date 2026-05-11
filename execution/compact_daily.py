#!/usr/bin/env python3
"""
compact_daily.py — Compactación diaria del historial de Telegram.

Diseñado para ejecutarse sin que el bot esté en marcha (cron, HEARTBEAT, CLI).
Compacta todos los chats con historial activo >= 3 mensajes.

Uso:
    python3 execution/compact_daily.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Añadir execution/ al path para importar compact_telegram
sys.path.insert(0, str(Path(__file__).parent))

from compact_telegram import (
    MIN_MESSAGES_FOR_LLM,
    compact,
)

PROJECT_DIR = Path(__file__).parent.parent
HISTORY_FILE = PROJECT_DIR / ".tmp" / "telegram_history.json"


def find_claude_bin() -> str:
    import os
    custom = os.getenv("CLAUDE_BIN", "")
    if custom and Path(custom).exists():
        return custom
    candidates = sorted(
        Path.home().glob(".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude"),
        reverse=True,
    )
    if candidates:
        return str(candidates[0])
    raise RuntimeError("Binario de claude no encontrado. Añade CLAUDE_BIN=/ruta/al/claude en .env")


def call_claude(prompt: str, claude_bin: str) -> str:
    import subprocess, re
    result = subprocess.run(
        [claude_bin, "-p", prompt],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),
        timeout=180,
    )
    output = re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", result.stdout).strip()
    if not output:
        raise RuntimeError(result.stderr.strip() or "Sin respuesta del subprocess")
    return output


def notify_telegram(token: str, chat_id: str, text: str) -> None:
    """Envía un mensaje de Telegram vía Bot API sin depender del bot en marcha."""
    import urllib.request, urllib.parse, json
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[compact_daily] Aviso: no se pudo enviar notificación Telegram: {e}")


def load_history() -> dict:
    import json
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_history(history: dict) -> None:
    import json
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run() -> None:
    import os
    from dotenv import load_dotenv
    load_dotenv(PROJECT_DIR / ".env")

    tg_token = os.getenv("TELEGRAM_TOKEN_JEFFREY", "")
    tg_user  = os.getenv("TELEGRAM_ALLOWED_USER_ID", "")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n[compact_daily] {now} — Iniciando compactación diaria")

    history = load_history()
    if not history:
        print("[compact_daily] Historial vacío. Nada que compactar.")
        if tg_token and tg_user:
            notify_telegram(tg_token, tg_user,
                "Compactación 20:55 — historial ya estaba vacío. Contexto fresco para mañana.")
        return

    try:
        claude_bin = find_claude_bin()
    except RuntimeError as e:
        print(f"[compact_daily] ERROR: {e}")
        sys.exit(1)

    chats_procesados = 0
    chats_saltados = 0
    errores = []

    for chat_id, messages in list(history.items()):
        if chat_id == "_meta":
            continue
        if not isinstance(messages, list) or len(messages) < MIN_MESSAGES_FOR_LLM:
            chats_saltados += 1
            continue

        print(f"[compact_daily] Compactando chat {chat_id} ({len(messages)} mensajes)…")
        ok, msg = compact(
            chat_id=chat_id,
            chat_history=messages,
            history=history,
            call_claude_fn=call_claude,
            claude_bin=claude_bin,
        )
        if ok:
            chats_procesados += 1
            print(f"  ✓ {msg}")
        else:
            errores.append(msg)
            print(f"  ✗ {msg}")

    if chats_procesados > 0 or chats_saltados > 0:
        save_history(history)

    resumen = f"[compact_daily] Completado — {chats_procesados} compactados, {chats_saltados} saltados."
    print(resumen)

    # Notificación Telegram
    if tg_token and tg_user:
        if errores:
            detalle = "\n".join(f"• {e}" for e in errores)
            texto = (
                f"Compactación 20:55 completada con errores.\n"
                f"Compactados: {chats_procesados} | Saltados: {chats_saltados}\n\n"
                f"Errores:\n{detalle}"
            )
        elif chats_procesados > 0:
            texto = (
                f"Compactación 20:55 completada.\n"
                f"{chats_procesados} chat(s) compactados. Contexto fresco para mañana."
            )
        else:
            texto = "Compactación 20:55 — sin mensajes suficientes. Contexto sin cambios."
        notify_telegram(tg_token, tg_user, texto)


if __name__ == "__main__":
    run()
