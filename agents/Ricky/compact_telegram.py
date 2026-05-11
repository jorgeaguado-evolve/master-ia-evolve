#!/usr/bin/env python3
"""
compact_telegram.py — Compactación de historial Telegram con guardado en memory/.

Uso desde telegram_bridge.py:
    from compact_telegram import is_close_topic, should_compact_periodic, compact
"""

import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).parent  # agents/Ricky/
COMPACTIONS_DIR = PROJECT_DIR / "memory" / "telegram_compactions"
MEMORY_INDEX = PROJECT_DIR / "memory" / "MEMORY.md"

COMPACT_INTERVAL_DAYS = int(os.getenv("COMPACT_INTERVAL_DAYS", "7"))
MIN_MESSAGES_FOR_LLM = 3

CLOSE_TOPIC_RE = re.compile(r"^tema\s+cerrado[.,!?]?$", re.IGNORECASE)


# ── Detección ──────────────────────────────────────────────────────────────────

def is_close_topic(text: str) -> bool:
    """True si el mensaje completo es 'tema cerrado' (con puntuación opcional)."""
    return bool(CLOSE_TOPIC_RE.match(text.strip()))


# ── Periódico ──────────────────────────────────────────────────────────────────

def should_compact_periodic(meta: dict, n_messages: int) -> bool:
    """
    True si han pasado >= COMPACT_INTERVAL_DAYS desde la última compactación
    y hay suficientes mensajes para que valga la pena.
    meta: history["_meta"].get(chat_id, {})
    """
    if COMPACT_INTERVAL_DAYS == 0:
        return False
    if n_messages < MIN_MESSAGES_FOR_LLM:
        return False
    last = meta.get("last_compaction")
    if not last:
        return False
    last_dt = datetime.fromisoformat(last)
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - last_dt
    return delta.days >= COMPACT_INTERVAL_DAYS


# ── Prompt ─────────────────────────────────────────────────────────────────────

def build_compaction_prompt(chat_history: list, today: str) -> str:
    """Prompt que exige YAML frontmatter + resumen narrativo."""
    lines = [
        "Eres Ricky el Project Manager. Resume el siguiente hilo de conversación de Telegram entre Jorge y Ricky.",
        "",
        "FORMATO OBLIGATORIO — responde empezando EXACTAMENTE con este bloque YAML:",
        "---",
        "título: <título conciso del tema, máximo 8 palabras>",
        "etiquetas: [<tag1>, <tag2>, <tag3>]",
        "decisiones:",
        "  - <decisión tomada, si la hay; si no, escribe []>",
        "pendientes:",
        "  - <acción pendiente, si la hay; si no, escribe []>",
        f"fecha_cierre: {today}",
        f"mensajes_compactados: {len(chat_history)}",
        "---",
        "",
        "Tras el bloque YAML escribe el resumen narrativo en español (mínimo 2 párrafos).",
        "Incluye: contexto del tema, decisiones clave, aprendizajes relevantes para sesiones futuras.",
        "No incluyas el mensaje 'tema cerrado' como parte del contenido.",
        "",
        "HISTORIAL:",
    ]
    for msg in chat_history:
        label = "Jorge" if msg["role"] == "user" else "Ricky"
        content = msg["content"]
        if is_close_topic(content):
            continue
        lines.append(f"[{label}]: {content}")

    return "\n".join(lines)


# ── Validación ─────────────────────────────────────────────────────────────────

def validate_summary(summary: str) -> bool:
    """Validación mínima: longitud + estructura YAML presente."""
    s = summary.strip()
    if len(s) < 50:
        return False
    if not s.startswith("---"):
        return False
    if "título:" not in s and "title:" not in s:
        return False
    return True


# ── Escritura ──────────────────────────────────────────────────────────────────

def write_compaction(chat_id: str, summary: str) -> Path:
    """Escribe el resumen en memory/telegram_compactions/ y devuelve el Path."""
    COMPACTIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"{timestamp}_chat{chat_id}.md"
    path = COMPACTIONS_DIR / filename
    path.write_text(summary, encoding="utf-8")
    return path


def verify_written(path: Path, summary: str) -> bool:
    """Relee el archivo del disco y confirma que el contenido es correcto."""
    try:
        written = path.read_text(encoding="utf-8")
        return written.strip() == summary.strip()
    except Exception:
        return False


# ── Índice de memoria ──────────────────────────────────────────────────────────

def update_memory_index(chat_id: str, path: Path, n_messages: int) -> None:
    """Añade una línea en memory/MEMORY.md referenciando la compactación."""
    if not MEMORY_INDEX.exists():
        return
    content = MEMORY_INDEX.read_text(encoding="utf-8")
    rel_path = path.relative_to(PROJECT_DIR)
    fecha = datetime.now().strftime("%Y-%m-%d")
    entry = f"- [Compactación Telegram {chat_id} {fecha}]({rel_path}) — resumen de {n_messages} mensajes\n"
    if path.name not in content:
        MEMORY_INDEX.write_text(content.rstrip() + "\n" + entry, encoding="utf-8")


# ── Archivo mínimo para historial trivial ──────────────────────────────────────

def _trivial_summary(chat_id: str, chat_history: list, today: str) -> str:
    """Genera resumen sin LLM para hilos con pocos mensajes."""
    msgs = "\n".join(
        f"- [{'Jorge' if m['role'] == 'user' else 'Ricky'}]: {m['content']}"
        for m in chat_history
        if not is_close_topic(m["content"])
    )
    return (
        f"---\n"
        f"título: Tema cerrado (trivial)\n"
        f"etiquetas: [trivial, sin-resumen]\n"
        f"decisiones: []\n"
        f"pendientes: []\n"
        f"fecha_cierre: {today}\n"
        f"mensajes_compactados: {len(chat_history)}\n"
        f"---\n\n"
        f"Hilo cerrado con {len(chat_history)} mensaje(s). Contenido mínimo, sin resumen LLM.\n\n"
        f"{msgs}\n"
    )


# ── Orquestador principal ──────────────────────────────────────────────────────

def compact(
    chat_id: str,
    chat_history: list,
    history: dict,
    call_claude_fn,
    claude_bin: str,
) -> tuple[bool, str]:
    """
    Orquesta el proceso completo de compactación.
    Devuelve (éxito, mensaje_para_jorge).
    NUNCA borra el historial si falla en cualquier paso previo.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    n_messages = len(chat_history)

    if n_messages == 0:
        return False, "El historial ya está vacío."

    if n_messages < MIN_MESSAGES_FOR_LLM:
        summary = _trivial_summary(chat_id, chat_history, today)
    else:
        prompt = build_compaction_prompt(chat_history, today)
        try:
            summary = call_claude_fn(prompt, claude_bin)
        except Exception as e:
            return False, f"[Error generando resumen: {e}] Historial conservado."

    if not validate_summary(summary):
        return False, f"[Resumen inválido o vacío] Historial conservado."

    try:
        path = write_compaction(chat_id, summary)
    except Exception as e:
        return False, f"[Error escribiendo a disco: {e}] Historial conservado."

    if not verify_written(path, summary):
        return False, f"[Error verificando escritura en disco] Historial conservado."

    history[chat_id] = []

    try:
        update_memory_index(chat_id, path, n_messages)
    except Exception:
        pass

    history.setdefault("_meta", {}).setdefault(chat_id, {})["last_compaction"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return True, "Tema cerrado. Resumen guardado en memoria."
