#!/usr/bin/env python3
"""
transcribe_yt.py — Descarga audio de YouTube y transcribe con Whisper API (OpenAI).

Uso:
    python execution/transcribe_yt.py "https://youtube.com/watch?v=VIDEO_ID"
    python execution/transcribe_yt.py VIDEO_ID

Cachea la transcripción en .tmp/transcript_<video_id>.txt para no repetir descargas.
"""

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MAX_BYTES = 24 * 1024 * 1024  # 24 MB (límite Whisper API: 25 MB)
CHUNK_SECONDS = 600            # 10 minutos por chunk


def extract_video_id(url_or_id: str) -> str:
    if "v=" in url_or_id:
        return url_or_id.split("v=")[-1].split("&")[0]
    if "youtu.be/" in url_or_id:
        return url_or_id.split("youtu.be/")[-1].split("?")[0]
    return url_or_id.strip()


def download_audio(url: str, output_path: str) -> None:
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "5",
        "--output", output_path,
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp falló: {result.stderr.strip()}")


def get_audio_duration(audio_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", audio_path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip() or "0")


def split_audio(audio_path: str, base_path: str, n_chunks: int) -> list[str]:
    chunks = []
    for i in range(n_chunks):
        start = i * CHUNK_SECONDS
        chunk_path = f"{base_path}_chunk{i:02d}.mp3"
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path,
             "-ss", str(start), "-t", str(CHUNK_SECONDS),
             "-q:a", "5", chunk_path],
            capture_output=True,
        )
        if result.returncode == 0 and os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 0:
            chunks.append(chunk_path)
    return chunks


def transcribe_file(client: OpenAI, path: str, language: str) -> str:
    with open(path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language=language,
            response_format="text",
        )
    return resp


def transcribe_audio(client: OpenAI, audio_path: str, base_path: str, language: str) -> str:
    size = os.path.getsize(audio_path)

    if size <= MAX_BYTES:
        print("  Transcribiendo (archivo único)...")
        return transcribe_file(client, audio_path, language)

    print(f"  Archivo grande ({size // (1024*1024)} MB) — dividiendo en chunks de 10 min...")
    duration = get_audio_duration(audio_path)
    n_chunks = int(duration / CHUNK_SECONDS) + 1
    chunks = split_audio(audio_path, base_path, n_chunks)

    parts = []
    for i, chunk_path in enumerate(chunks):
        print(f"  Transcribiendo chunk {i+1}/{len(chunks)}...")
        try:
            parts.append(transcribe_file(client, chunk_path, language))
        finally:
            os.remove(chunk_path)

    return "\n\n".join(parts)


def transcribe_video(url_or_id: str, language: str = "es") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("ERROR: OPENAI_API_KEY no encontrada en .env")

    client = OpenAI(api_key=api_key)
    video_id = extract_video_id(url_or_id)

    tmp_dir = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    transcript_path = os.path.join(tmp_dir, f"transcript_{video_id}.txt")

    # Caché — no repetir si ya existe
    if os.path.exists(transcript_path):
        print(f"[Caché] Transcripción ya disponible: .tmp/transcript_{video_id}.txt")
        with open(transcript_path, "r", encoding="utf-8") as f:
            return f.read()

    # URL completa si solo se dio el ID
    if not url_or_id.startswith("http"):
        url_or_id = f"https://www.youtube.com/watch?v={video_id}"

    audio_path = os.path.join(tmp_dir, f"audio_{video_id}.mp3")
    base_path  = os.path.join(tmp_dir, f"audio_{video_id}")

    try:
        print(f"Descargando audio: {url_or_id}")
        download_audio(url_or_id, audio_path)

        if not os.path.exists(audio_path):
            raise FileNotFoundError("yt-dlp no generó el archivo de audio esperado.")

        transcript = transcribe_audio(client, audio_path, base_path, language)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"[OK] Transcripción guardada: .tmp/transcript_{video_id}.txt")
        return transcript

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe vídeos de YouTube con Whisper API.",
    )
    parser.add_argument("url", help="URL o ID del vídeo de YouTube")
    parser.add_argument("--lang", default="es", help="Idioma del audio (default: es)")
    args = parser.parse_args()

    transcript = transcribe_video(args.url, args.lang)

    preview = transcript[:3000]
    print("\n" + "─" * 60)
    print(preview)
    if len(transcript) > 3000:
        print(f"\n[... {len(transcript) - 3000} caracteres adicionales en el archivo .tmp/]")
