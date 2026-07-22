---
name: telegram-notify
description: "Real-time bidirectional communication with Telegram. Send notifications, ask questions, get answers — all from Telegram. For interactive prompts like permission requests, feature selection, and confirmations."
---

# Telegram Notify — Interactive Bridge

## Files

- `mcp-server.py` — MCP server (auto-starts with NaraCLI/Opencode)
- `telegram-bridge.py` — Standalone bot server (alternative)
- `nara-telegram.py` — CLI helper (alternative)

## Setup (MCP - Recommended)

MCP server otomatis aktif saat NaraCLI/Opencode start.

### 1. Install dependency
```bash
pip install python-telegram-bot mcp
```

### 2. Set environment variables
Tambahkan ke `~/.bashrc`:
```bash
export TELEGRAM_BOT_TOKEN="token dari @BotFather"
export TELEGRAM_CHAT_ID="chat ID kamu"
```

### 3. MCP config sudah aktif
File: `~/.bynara/agent/mcp.json` sudah include:
```json
{
  "mcpServers": {
    "nara-telegram": {
      "command": "python",
      "args": ["/home/mrksvt/.bynara/agent/skills/telegram-notify/mcp-server.py"]
    }
  }
}
```

### 4. Restart NaraCLI/Opencode
MCP server akan start otomatis.

## MCP Tools

| Tool | Fungsi | Return |
|------|--------|--------|
| `telegram_ask(question, options?)` | Tanya bebas / single choice | Jawaban text |
| `telegram_ask_multi(question, options)` | Multi-select (pilih beberapa) | Comma-separated |
| `telegram_confirm(question)` | Ya/Tidak | "yes" / "no" |
| `telegram_notify(message)` | Notifikasi (no response) | "ok" |

## Flow

```
NaraCLI                    Telegram                  Kamu
   │                          │                       │
   │── telegram_ask() ──────▶ │                       │
   │   (MCP server write      │── ❓ Question? ──▶   │
   │    question file)         │   [Button]           │
   │                          │                       │
   │                          │  ◀── tap button ────  │
   │  ◀── answer ──────────   │                       │
   │   (MCP server read       │                       │
   │    response file)         │                       │
```

## Usage dari NaraCLI

NaraCLI akan otomatis pakai MCP tools saat ada di environment yang support MCP.

Contoh flow yang NaraCLI bisa lakukan:
1. `telegram_ask("Fitur mana?", options="Auth,DB,API")` → user pilih
2. `telegram_ask_multi("Pilih semua yang perlu:", options="A,B,C")` → user pilih banyak
3. `telegram_confirm("Patch sekarang?")` → user ya/tidak
4. `telegram_notify("✅ Done")` → kirim notifikasi

## Anti-Patterns

- Jangan jalankan MCP server + bridge bersamaan (conflict)
- Jangan pakai secrets di question text
- Timeout default 120s — adjust via `TELEGRAM_TIMEOUT` env
