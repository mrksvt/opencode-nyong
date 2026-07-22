# INSTALL.md — OpenCode Nyong Setup Guide

Prompt ini bisa langsung diberikan ke agent untuk install otomatis seluruh konfigurasi.

---

## Agent Self-Install Prompt

```
Clone repo https://github.com/mrksvt/opencode-nyong, lalu install semua skills dan MCP servers ke ~/.config/opencode/ mengikuti struktur di INSTALL.md. Jangan overwrite opencode.json dan opencode.jsonc yang sudah ada — hanya merge MCP entries yang belum ada. Setelah install, verifikasi semua 24 skills ada di ~/.config/opencode/skills/ dan semua 11 MCP servers bisa connect.
```

---

## PREREQUISITES

```bash
opencode --version   # Harus terinstall
node --version       # >= 18
python3 --version    # >= 3.10
git --version
```

## PLUGIN SETUP (opencode.jsonc)

Buat/edit `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "plugin": [
    "oh-my-openagent@latest",
    "superpowers@git+https://github.com/obra/superpowers.git"
  ],
  "model": "nararouter/mimo-v2.5-pro",
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "postman": {
      "type": "local",
      "command": ["npx", "-y", "@postman/postman-mcp-server"],
      "enabled": true,
      "environment": {
        "POSTMAN_API_KEY": "{{POSTMAN_API_KEY}}"
      }
    },
    "mcp-mermaid": {
      "type": "local",
      "command": ["node", "/home/{{USER}}/Documents/Github/mcp-mermaid/build/index.js"],
      "enabled": true
    }
  }
}
```

## AGENT & CATEGORY SETUP (oh-my-openagent.json)

Copy dari repo ke `~/.config/opencode/oh-my-openagent.json`.

### Agents (11)

| Agent | Model | Variant | Purpose |
|-------|-------|---------|---------|
| `sisyphus` | 9router/nararouter2/mimo-v2.5-pro-hermes | max | Main orchestrator — decompose, delegate, verify |
| `sisyphus-junior` | 9router/nararouter2/mimo-v2.5-hermes | medium | Task executor via categories |
| `oracle` | 9router/cc/claude-opus-4-8 | high | Read-only high-IQ debugging & architecture |
| `hephaestus` | 9router/nararouter2/mimo-v2.5-hermes | medium | Build/implementation agent |
| `librarian` | 9router/cc/claude-sonnet-5 | medium | External reference search (docs, OSS, web) |
| `explore` | 9router/nararouter/mistral-large | medium | Codebase contextual grep |
| `prometheus` | 9router/cc/claude-opus-4-8 | max | Planning consultant |
| `metis` | 9router/cc/claude-sonnet-5 | high | Pre-planning analysis |
| `momus` | 9router/cc/claude-opus-4-7 | xhigh | Plan review & QA |
| `atlas` | 9router/nararouter2/mimo-v2.5-hermes | medium | Codebase indexing |
| `multimodal-looker` | 9router/ag/gemini-3-flash | medium | Media file analysis |

### Categories (8)

| Category | Model | Variant | Use For |
|----------|-------|---------|---------|
| `visual-engineering` | 9router/nararouter/mistral-large | high | Frontend, UI/UX, styling, animation |
| `ultrabrain` | 9router/cc/claude-opus-4-8 | xhigh | Hard logic, architecture, algorithms |
| `deep` | 9router/nararouter2/mimo-v2.5-pro-hermes | high | Autonomous end-to-end implementation |
| `artistry` | 9router/cc/claude-fable-5 | high | Creative, unconventional solutions |
| `quick` | 9router/nararouter2/mimo-v2.5-hermes | medium | Trivial single-file changes |
| `unspecified-low` | 9router/nararouter2/mimo-v2.5-hermes | medium | Low-effort misc tasks |
| `unspecified-high` | 9router/nararouter2/mimo-v2.5-pro-hermes | high | High-effort misc tasks |
| `writing` | 9router/cc/claude-fable-5 | high | Documentation, prose, technical writing |

## ACID DISCIPLINE (ACID.md)

Copy dari repo ke `~/.config/opencode/ACID.md`.

Di `opencode.json`, tambahkan:
```json
"instructions": ["~/.config/opencode/ACID.md"]
```

## MCP SERVERS (opencode.json)

Buat/edit `~/.config/opencode/opencode.json`.

### Provider Config

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "9router": {
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://127.0.0.1:20128/v1",
        "apiKey": "{{NINEROUTER_API_KEY}}"
      }
    }
  },
  "mcp": { ... }
}
```

### 5 Built-in MCPs (auto-enabled, no config)

| MCP | Fungsi |
|-----|--------|
| `codegraph` | Codebase indexing & structure |
| `context7` | Context-aware documentation retrieval |
| `grep_app` | Content search |
| `lsp` | Language Server Protocol |
| `websearch` | Web search |

### 3 External MCPs

```json
"pentest-ai": {
  "type": "local",
  "command": ["ptai", "mcp"],
  "enabled": true
},
"headroom": {
  "type": "local",
  "command": ["/home/{{USER}}/.local/bin/headroom", "mcp", "serve"],
  "enabled": true
}
```

Install:
```bash
pip install pentest-ai
# headroom binary dari release
```

### 4 Custom MCPs (source di repo)

```json
"nara-telegram": {
  "type": "local",
  "command": ["python", "/home/{{USER}}/.config/opencode/skills/telegram-notify/mcp-server.py"],
  "enabled": true
},
"piper-tts": {
  "type": "local",
  "command": ["python", "/home/{{USER}}/.config/opencode/skills/piper-tts/mcp-server.py"],
  "enabled": true
},
"postman": {
  "type": "local",
  "command": ["npx", "-y", "@postman/postman-mcp-server"],
  "enabled": true,
  "environment": {
    "POSTMAN_API_KEY": "{{POSTMAN_API_KEY}}"
  }
},
"mcp-mermaid": {
  "type": "local",
  "command": ["node", "/home/{{USER}}/Documents/Github/mcp-mermaid/build/index.js"],
  "enabled": true
}
```

Install dependencies:
```bash
pip install python-telegram-bot mcp  # telegram-notify
# piper-tts sudah terinstall
# npm install di folder mcp-mermaid
```

### MCP Tools Summary

**nara-telegram** (4 tools)
| Tool | Fungsi |
|------|--------|
| `telegram_ask(question, options?)` | Tanya single choice |
| `telegram_ask_multi(question, options)` | Multi-select |
| `telegram_confirm(question)` | Ya/Tidak |
| `telegram_notify(message)` | Kirim notifikasi |

**piper-tts** (3 tools)
| Tool | Fungsi |
|------|--------|
| `piper_speak(text, speed?, play?)` | Teks → suara |
| `piper_speak_file(file_path, speed?, play?)` | File → suara |
| `piper_cleanup(file_path)` | Hapus file audio |

**mcp-mermaid** (1 tool)
| Tool | Fungsi |
|------|--------|
| `generate_mermaid_diagram(mermaid, outputType?, theme?)` | Generate diagram |

**pentest-ai** — 60+ security probes, recon, vulnerability scanning

**postman** — API collection runner, workspace management

**headroom** — Context window compression

## SKILLS INSTALLATION (24 skills)

```bash
cp -r skills/* ~/.config/opencode/skills/
```

| # | Skill | Deskripsi | Dependencies |
|---|-------|-----------|-------------|
| 1 | academic-paper | 12-agent paper writing pipeline | — |
| 2 | academic-paper-reviewer | Multi-perspective peer review | — |
| 3 | academic-pipeline | Full research→write→review pipeline | — |
| 4 | acid-transactions | Database transaction patterns | — |
| 5 | agents-sdk | Cloudflare Agents SDK | — |
| 6 | cloudflare | Full Cloudflare platform (40+ services) | — |
| 7 | cloudflare-email-service | Transactional email | — |
| 8 | deep-research | 13-agent research pipeline | — |
| 9 | docx | Word document manipulation | python-docx, lxml |
| 10 | durable-objects | Cloudflare Durable Objects | — |
| 11 | gambling-detection | Gambling pattern detection | — |
| 12 | humanizer | Remove AI writing signs | — |
| 13 | model-router | Model selection automation | — |
| 14 | pdf | PDF manipulation | PyPDF2, qpdf, pdfplumber |
| 15 | piper-tts | Indonesian text-to-speech | piper-tts, piper binary |
| 16 | plantuml-skill | Diagram generation (PlantUML) | Java (plantuml.jar) |
| 17 | postman | API testing | Postman MCP |
| 18 | sandbox-sdk | Cloudflare Sandbox SDK | — |
| 19 | telegram-notify | Telegram bidirectional bridge | python-telegram-bot, mcp |
| 20 | turnstile-spin | Cloudflare Turnstile setup | Cloudflare account |
| 21 | use-case-mermaid | Use case diagrams | mcp-mermaid |
| 22 | web-perf | Web performance analysis | Chrome DevTools |
| 23 | workers-best-practices | Workers code review | — |
| 24 | wrangler | Cloudflare Wrangler CLI | wrangler |

## ENVIRONMENT VARIABLES

```bash
cp .env.example ~/.config/opencode/.env
```

Isi:
```
NINEROUTER_API_KEY=sk-xxxxxxxx
POSTMAN_API_KEY=PMAK-xxxxxxxx
TELEGRAM_BOT_TOKEN=123:abc
TELEGRAM_CHAT_ID=123456
CLOUDFLARE_API_TOKEN=xxxxxxxx
PIPER_MODEL_DIR=/home/{{USER}}/ModelPiper/id
```

## EXECUTION SCRIPT

```bash
# 1. Clone repo
git clone git@github.com:mrksvt/opencode-nyong.git /tmp/opencode-nyong

# 2. Copy skills
mkdir -p ~/.config/opencode/skills
cp -r /tmp/opencode-nyong/skills/* ~/.config/opencode/skills/

# 3. Copy config files
cp /tmp/opencode-nyong/oh-my-openagent.json ~/.config/opencode/
cp /tmp/opencode-nyong/ACID.md ~/.config/opencode/
cp /tmp/opencode-nyong/.env.example ~/.config/opencode/.env.example

# 4. Copy MCP servers
mkdir -p ~/.config/opencode/skills/telegram-notify
cp /tmp/opencode-nyong/mcps/telegram-notify/mcp-server.py ~/.config/opencode/skills/telegram-notify/
mkdir -p ~/.config/opencode/skills/piper-tts
cp /tmp/opencode-nyong/mcps/piper-tts/mcp-server.py ~/.config/opencode/skills/piper-tts/

# 5. Install Python dependencies
pip install python-telegram-bot mcp

# 6. Setup environment
cp ~/.config/opencode/.env.example ~/.config/opencode/.env
# EDIT .env dengan kredensial asli

# 7. Cleanup
rm -rf /tmp/opencode-nyong

# 8. Restart OpenCode
echo "✅ Done. Restart OpenCode."
```

## VERIFICATION

```bash
# Config valid
python3 -c "import json; json.load(open('$HOME/.config/opencode/opencode.json'))" && echo "✅ opencode.json valid"
python3 -c "import json; json.load(open('$HOME/.config/opencode/oh-my-openagent.json'))" && echo "✅ oh-my-openagent.json valid"

# Skills count
count=$(ls ~/.config/opencode/skills/ | wc -l)
[ "$count" -eq 24 ] && echo "✅ 24 skills installed" || echo "❌ Expected 24, got $count"

# MCP servers
echo "Cek di OpenCode: semua 11 MCP harus Connected"
```

## TROUBLESHOOTING

| Masalah | Solusi |
|---------|--------|
| MCP tidak connect | Cek path di command MCP, pastikan file exists |
| piper-tts error | Pastikan model di `/home/{{USER}}/ModelPiper/id/` |
| telegram-notify error | Set `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID` di env |
| postman error | Set `POSTMAN_API_KEY` di env |
| plantuml error | Java harus terinstall (`java -version`) |
| pentest-ai error | Install `ptai` CLI tool |
| headroom error | Install headroom binary |
| mcp-mermaid error | `cd ~/Documents/Github/mcp-mermaid && npm install` |