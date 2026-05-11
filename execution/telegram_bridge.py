#!/usr/bin/env python3
"""
Puente Telegram <-> Jeffrey (Claude Code).
Mantiene historial de conversación persistente por chat.
"""
import asyncio
import html
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from compact_telegram import is_close_topic, should_compact_periodic, compact

PROJECT_DIR = Path(__file__).parent.parent
HISTORY_FILE = PROJECT_DIR / ".tmp" / "telegram_history.json"

load_dotenv(PROJECT_DIR / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN_JEFFREY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))
MAX_HISTORY = 30  # mensajes por chat (15 turnos)

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def find_claude_bin() -> str:
    custom = os.getenv("CLAUDE_BIN", "")
    if custom and Path(custom).exists():
        return custom
    candidates = sorted(
        Path.home().glob(".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude"),
        reverse=True,
    )
    if candidates:
        return str(candidates[0])
    raise RuntimeError(
        "Binario de claude no encontrado. Añade CLAUDE_BIN=/ruta/al/claude en .env"
    )


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_history(history: dict) -> None:
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def build_prompt(chat_history: list, new_message: str) -> str:
    if not chat_history:
        return new_message

    lines = [
        "Estás en una conversación continua con Jorge vía Telegram.",
        "Historial previo de esta conversación:\n",
    ]
    for msg in chat_history:
        label = "Jorge" if msg["role"] == "user" else "Jeffrey"
        lines.append(f"[{label}]: {msg['content']}")

    lines.append(f"\nNuevo mensaje de Jorge: {new_message}")
    lines.append("\nResponde como Jeffrey continuando esta conversación.")
    return "\n".join(lines)


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", text)


def md_to_html(text: str) -> str:
    """Convierte markdown de Claude a HTML compatible con Telegram."""
    text = html.escape(text)

    # Sustituir bloques de código por placeholders para que los regex
    # de negrita/cursiva no toquen su contenido interior
    placeholders: dict[str, str] = {}
    counter = 0

    def protect(tag: str) -> str:
        nonlocal counter
        key = f"\x00{counter}\x00"
        counter += 1
        placeholders[key] = tag
        return key

    text = re.sub(
        r"```(?:\w+)?\n?(.*?)```",
        lambda m: protect("<pre><code>" + m.group(1).strip() + "</code></pre>"),
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"`([^`\n]+)`",
        lambda m: protect("<code>" + m.group(1) + "</code>"),
        text,
    )

    # Negrita, cursiva y encabezados (solo sobre texto normal, no sobre código)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)
    text = re.sub(r"\*([^*\n]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"_([^_\n]+)_", r"<i>\1</i>", text)
    text = re.sub(r"^#{1,6}\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)

    for key, value in placeholders.items():
        text = text.replace(key, value)

    return text


def call_claude(prompt: str, claude_bin: str) -> str:
    result = subprocess.run(
        [claude_bin, "-p", prompt],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),
        timeout=180,
    )
    response = strip_ansi(result.stdout).strip()
    if not response:
        error = result.stderr.strip()
        response = f"[Error al contactar con Jeffrey: {error[:300]}]" if error else "[Sin respuesta]"
    return response


async def typing_loop(bot, chat_id: int, done: asyncio.Event) -> None:
    """Envía 'escribiendo...' cada 4s hasta que done se active."""
    try:
        while not done.is_set():
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            print(f"[typing] enviado a {chat_id}")
            # Espera 4s o hasta que done se active (lo que ocurra antes)
            try:
                await asyncio.wait_for(done.wait(), timeout=4)
            except asyncio.TimeoutError:
                pass
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[typing] error: {e}")


async def safe_edit(message, text: str) -> None:
    """Edita un mensaje con HTML; si falla, reintenta en texto plano."""
    formatted = md_to_html(text)
    limit = 4096
    try:
        if len(formatted) <= limit:
            await message.edit_text(formatted, parse_mode=ParseMode.HTML)
        else:
            await message.edit_text(formatted[:limit], parse_mode=ParseMode.HTML)
            # Los trozos extra van como mensajes nuevos al chat del placeholder
            chat_id = message.chat_id
            bot = message.get_bot()
            for i in range(limit, len(formatted), limit):
                await bot.send_message(chat_id, formatted[i : i + limit], parse_mode=ParseMode.HTML)
    except Exception:
        # Fallback: texto plano sin formato
        plain = text[:limit] if len(text) <= limit else text[:limit]
        await message.edit_text(plain)


async def send_text(update: Update, text: str) -> None:
    """Envía texto con HTML, partiendo si supera el límite de Telegram."""
    formatted = md_to_html(text)
    limit = 4096
    try:
        if len(formatted) <= limit:
            await update.message.reply_text(formatted, parse_mode=ParseMode.HTML)
        else:
            for i in range(0, len(formatted), limit):
                await update.message.reply_text(formatted[i : i + limit], parse_mode=ParseMode.HTML)
    except Exception:
        await update.message.reply_text(text[:limit])


def is_authorized(update: Update) -> bool:
    return update.effective_user.id == ALLOWED_USER_ID


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    chat_id: int = update.effective_chat.id
    chat_key = str(chat_id)
    user_text = update.message.text.strip()

    history = load_history()
    chat_history = history.get(chat_key, [])

    # ── Bloque compactación manual ("tema cerrado") ────────────────────────────
    if is_close_topic(user_text):
        claude_bin = find_claude_bin()
        ok, msg = compact(chat_key, chat_history, history, call_claude, claude_bin)
        if ok:
            save_history(history)
        await send_text(update, msg)
        return
    # ── Bloque compactación periódica ──────────────────────────────────────────
    meta = history.get("_meta", {}).get(chat_key, {})
    if should_compact_periodic(meta, len(chat_history)):
        claude_bin = find_claude_bin()
        ok, _ = compact(chat_key, chat_history, history, call_claude, claude_bin)
        if ok:
            save_history(history)
            chat_history = history.get(chat_key, [])
            await send_text(update, "Compactación automática ejecutada. Contexto guardado.")
    # ──────────────────────────────────────────────────────────────────────────

    prompt = build_prompt(chat_history, user_text)

    # Mensaje visible de espera (funciona aunque la pantalla esté bloqueada)
    placeholder = await update.message.reply_text("⏳")

    done = asyncio.Event()
    task = asyncio.create_task(typing_loop(context.bot, chat_id, done))

    try:
        claude_bin = find_claude_bin()
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, call_claude, prompt, claude_bin)
    except Exception as e:
        response = f"[Error: {e}]"
    finally:
        done.set()
        await task

    chat_history.append({"role": "user", "content": user_text})
    chat_history.append({"role": "assistant", "content": response})
    history[str(chat_id)] = chat_history[-MAX_HISTORY:]
    save_history(history)

    await safe_edit(placeholder, response)


def transcribe_audio(file_path: str) -> str:
    """Transcribe un archivo de audio con Whisper via OpenAI API."""
    with open(file_path, "rb") as f:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="es",
        )
    return result.text.strip()


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    chat_id: int = update.effective_chat.id
    voice = update.message.voice or update.message.audio

    placeholder = await update.message.reply_text("⏳")

    try:
        # Descargar el audio a un archivo temporal
        tg_file = await context.bot.get_file(voice.file_id)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name
        await tg_file.download_to_drive(tmp_path)

        # Transcribir con Whisper API
        loop = asyncio.get_running_loop()
        transcription = await loop.run_in_executor(None, transcribe_audio, tmp_path)
        Path(tmp_path).unlink(missing_ok=True)

        print(f"[voz] transcripción: {transcription}")

        if not transcription:
            await placeholder.edit_text("No he podido entender el audio.")
            return

        # Reutilizar el pipeline de texto con la transcripción
        history = load_history()
        chat_key = str(chat_id)
        chat_history = history.get(chat_key, [])

        # ── Bloque compactación manual por voz ("tema cerrado") ───────────────
        if is_close_topic(transcription):
            claude_bin = find_claude_bin()
            ok, msg = compact(chat_key, chat_history, history, call_claude, claude_bin)
            if ok:
                save_history(history)
            await safe_edit(placeholder, msg)
            return
        # ── Bloque compactación periódica ─────────────────────────────────────
        meta = history.get("_meta", {}).get(chat_key, {})
        if should_compact_periodic(meta, len(chat_history)):
            claude_bin = find_claude_bin()
            ok, _ = compact(chat_key, chat_history, history, call_claude, claude_bin)
            if ok:
                save_history(history)
                chat_history = history.get(chat_key, [])
                await safe_edit(placeholder, "Compactación automática ejecutada. Contexto guardado.")
        # ─────────────────────────────────────────────────────────────────────

        prompt = build_prompt(chat_history, transcription)

        done = asyncio.Event()
        task = asyncio.create_task(typing_loop(context.bot, chat_id, done))

        try:
            claude_bin = find_claude_bin()
            response = await loop.run_in_executor(None, call_claude, prompt, claude_bin)
        except Exception as e:
            response = f"[Error: {e}]"
        finally:
            done.set()
            await task

        chat_history.append({"role": "user", "content": f"[Audio] {transcription}"})
        chat_history.append({"role": "assistant", "content": response})
        history[str(chat_id)] = chat_history[-MAX_HISTORY:]
        save_history(history)

        await safe_edit(placeholder, response)

    except Exception as e:
        print(f"[voz] error: {e}")
        await placeholder.edit_text(f"[Error procesando el audio: {e}]")


def main() -> None:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN_JEFFREY no está definido en .env")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

    print("Jeffrey Telegram bridge activo. Esperando mensajes...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
