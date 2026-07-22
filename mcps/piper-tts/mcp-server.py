#!/usr/bin/env python3
"""
Piper TTS MCP Server
====================
MCP server for Indonesian text-to-speech via Piper TTS.
Converts text to WAV audio, optionally plays it.

Tools:
  piper_speak      - Convert text to speech, return file path
  piper_speak_file - Read file, convert to speech, return file path
"""

import os
import sys
import json
import subprocess
import tempfile
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ── Config ──────────────────────────────────────────────────────────────
MODEL_DIR = Path(os.environ.get("PIPER_MODEL_DIR", "/home/mrksvt/ModelPiper/id"))
MODEL_FILE = MODEL_DIR / "id_ID-news_tts-medium.onnx"
MODEL_CONFIG = MODEL_DIR / "id_ID-news_tts-medium.onnx.json"
OUTPUT_DIR = Path(os.environ.get("PIPER_OUTPUT_DIR", "/tmp/piper-tts"))

SPEED_MAP = {
    "lambat": 0.8,
    "slow": 0.8,
    "sedang": 1.0,
    "medium": 1.0,
    "normal": 1.0,
    "cepat": 1.3,
    "fast": 1.3,
}

# ── Helpers ─────────────────────────────────────────────────────────────

def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def text_to_speech(text: str, speed: float = 1.0, output_path: Optional[str] = None) -> str:
    """Convert text to speech using Piper CLI, return output WAV path."""
    ensure_output_dir()

    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(OUTPUT_DIR / f"piper_{ts}.wav")

    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_FILE}")
    if not MODEL_CONFIG.exists():
        raise FileNotFoundError(f"Model config not found: {MODEL_CONFIG}")

    # Piper CLI: echo text | piper -m model.onnx --length-scale SPEED -f output.wav
    cmd = [
        "piper",
        "-m", str(MODEL_FILE),
        "--config", str(MODEL_CONFIG),
        "--length-scale", str(speed),
        "-f", output_path,
    ]

    result = subprocess.run(
        cmd,
        input=text,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Piper failed: {result.stderr}")

    if not Path(output_path).exists():
        raise RuntimeError(f"Output file not created: {output_path}")

    return output_path

def play_audio(file_path: str) -> bool:
    """Play audio file. Returns True on success."""
    try:
        # Try aplay (ALSA)
        subprocess.run(["aplay", file_path], capture_output=True, timeout=300)
        return True
    except FileNotFoundError:
        pass

    try:
        # Try paplay (PulseAudio)
        subprocess.run(["paplay", file_path], capture_output=True, timeout=300)
        return True
    except FileNotFoundError:
        pass

    try:
        # Try ffplay (FFmpeg)
        subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path],
                       capture_output=True, timeout=300)
        return True
    except FileNotFoundError:
        pass

    raise RuntimeError("No audio player found. Install aplay, paplay, or ffplay.")

# ── MCP Server ──────────────────────────────────────────────────────────
mcp = FastMCP("piper-tts")


@mcp.tool()
def piper_speak(
    text: str,
    speed: Optional[str] = "sedang",
    play: bool = False,
) -> str:
    """
    Convert Indonesian text to speech using Piper TTS.

    Args:
        text: Teks bahasa Indonesia yang akan dikonversi
        speed: Kecepatan bicara: "lambat"/"slow", "sedang"/"medium"/"normal", "cepat"/"fast"
        play: Jika True, langsung putar audio setelah konversi

    Returns:
        JSON string: {"file": "/path/to/output.wav", "played": true/false}
    """
    speed_val = SPEED_MAP.get(speed.lower(), 1.0)
    output_path = text_to_speech(text, speed=speed_val)

    played = False
    if play:
        play_audio(output_path)
        played = True

    return json.dumps({
        "file": output_path,
        "played": played,
        "text_length": len(text),
        "speed": speed_val,
    })


@mcp.tool()
def piper_speak_file(
    file_path: str,
    speed: Optional[str] = "sedang",
    play: bool = False,
) -> str:
    """
    Read a text/markdown file and convert its content to speech using Piper TTS.

    Args:
        file_path: Path ke file teks (.txt, .md, dll)
        speed: Kecepatan bicara: "lambat"/"slow", "sedang"/"medium"/"normal", "cepat"/"fast"
        play: Jika True, langsung putar audio setelah konversi

    Returns:
        JSON string: {"file": "/path/to/output.wav", "played": true/false, "source": "file_path"}
    """
    fp = Path(file_path)
    if not fp.exists():
        return json.dumps({"error": f"File not found: {file_path}"})

    text = fp.read_text(encoding="utf-8")

    speed_val = SPEED_MAP.get(speed.lower(), 1.0)
    output_path = text_to_speech(text, speed=speed_val)

    played = False
    if play:
        play_audio(output_path)
        played = True

    return json.dumps({
        "file": output_path,
        "played": played,
        "source": str(fp.absolute()),
        "text_length": len(text),
        "speed": speed_val,
    })


@mcp.tool()
def piper_cleanup(file_path: str) -> str:
    """
    Delete a generated audio file (for cleanup after sending to Telegram).

    Args:
        file_path: Path ke file WAV yang akan dihapus

    Returns:
        "deleted" atau "error: ..."
    """
    fp = Path(file_path)
    if not fp.exists():
        return f"error: file not found: {file_path}"

    # Safety: only delete files in the output directory
    if not str(fp.absolute()).startswith(str(OUTPUT_DIR.absolute())):
        return f"error: file outside output directory, not deleted: {fp}"

    fp.unlink()
    return "deleted"


# ── Run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ensure_output_dir()
    import asyncio
    asyncio.run(mcp.run_stdio_async())