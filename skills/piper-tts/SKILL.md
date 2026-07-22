---
name: piper-tts
description: "Indonesian text-to-speech via Piper TTS. Convert text/markdown to speech, play audio, send to Telegram, auto-cleanup. Triggers: bacakan, bacakan untuk saya, baca, konversi ke suara, text to speech, piper, suarakan, tts."
---

# Piper TTS — Indonesian Text-to-Speech

## Files

- `mcp-server.py` — MCP server (auto-starts with OpenCode)
- Model: `/home/mrksvt/ModelPiper/id/id_ID-news_tts-medium.onnx`

## MCP Tools

| Tool | Fungsi | Return |
|------|--------|--------|
| `piper_speak(text, speed?, play?)` | Konversi teks ke suara | JSON: `{file, played, text_length, speed}` |
| `piper_speak_file(file_path, speed?, play?)` | Baca file, konversi ke suara | JSON: `{file, played, source, text_length, speed}` |
| `piper_cleanup(file_path)` | Hapus file audio hasil konversi | `"deleted"` atau error |

### Speed Options

| Label | Nilai |
|-------|-------|
| `lambat` / `slow` | 0.8 |
| `sedang` / `medium` / `normal` | 1.0 (default) |
| `cepat` / `fast` | 1.3 |

## Workflow

### Mode 1: "Bacakan" (Read Aloud + Play)

User says: `bacakan LAPORAN.md`, `bacakan untuk saya`, `bacakan dengan kecepatan cepat`

```
1. piper_speak_file(file_path, speed, play=true)
2. Tunggu playback selesai (blocking)
3. telegram_notify("🔊 Selesai membacakan: {file_path}")
4. piper_cleanup(file_path)
```

### Mode 2: "Konversi ke Suara" (Convert Only)

User says: `konversi ke suara`, `tts`, `suarakan`, `text to speech`

```
1. piper_speak_file(file_path, speed, play=false)
2. telegram_notify("🎙️ Hasil konversi: {file_path}")
3. piper_cleanup(file_path)
```

## Trigger Phrases

| Frasa | Mode | Play? |
|-------|------|-------|
| `bacakan`, `bacakan untuk saya`, `baca`, `bacakan ...` | Read Aloud | ✅ Yes |
| `konversi ke suara`, `suarakan`, `tts`, `text to speech`, `piper` | Convert Only | ❌ No |

## Telegram Integration

Gunakan MCP `nara-telegram` yang sudah ada untuk mengirim file audio ke Telegram. Setelah file terkirim, hapus dengan `piper_cleanup`.

## Anti-Patterns

- Jangan lupa hapus file audio setelah dikirim ke Telegram
- Jangan gunakan file di luar `/tmp/piper-tts/` (safety cleanup)
- Model bahasa Indonesia only — teks Inggris tetap bisa tapi kualitas kurang optimal