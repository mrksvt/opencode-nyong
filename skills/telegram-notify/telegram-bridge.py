#!/usr/bin/env python3
"""
NaraCLI Telegram Interactive Bridge
====================================
Dua arah: NaraCLI ↔ Telegram.

- NaraCLI kirim pertanyaan → Telegram user jawab
- Telegram user kirim command → NaraCLI jalankan

Shared state via JSON file (no database needed).

Setup:
  pip install python-telegram-bot
  export TELEGRAM_BOT_TOKEN="..."
  export TELEGRAM_CHAT_ID="..."
  python telegram-bridge.py

NaraCLI helper:
  python nara-telegram.py ask "Mau patch fitur apa?"
  python nara-telegram.py ask --options "Fix auth,Add login,Refactor db"
  python nara-telegram.py notify "✅ Build selesai"
  python nara-telegram.py wait  # block sampai user jawab
"""

import os
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ── Config ──────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
AUTHORIZED_CHAT = os.environ.get("TELEGRAM_CHAT_ID")
NARA_CLI = os.environ.get("NARA_CLI_PATH", "naracli")
TIMEOUT = 300
STATE_DIR = Path(os.environ.get("NARA_STATE_DIR", "/tmp/nara-telegram"))
STATE_FILE = STATE_DIR / "state.json"
QUESTIONS_DIR = STATE_DIR / "questions"
RESPONSES_DIR = STATE_DIR / "responses"


# ── State Management ───────────────────────────────────────────────────
def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)


def write_state(data: dict):
    STATE_FILE.write_text(json.dumps(data, indent=2))


def read_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def create_question(text: str, options: list[str] | None = None, qtype: str = "text") -> str:
    """Create a question file for the bridge to pick up."""
    ensure_dirs()
    qid = datetime.now().strftime("%Y%m%d%H%M%S%f")
    question = {
        "id": qid,
        "type": qtype,  # text, options, confirm, yesno
        "text": text,
        "options": options or [],
        "created_at": datetime.now().isoformat(),
        "status": "pending",
    }
    qfile = QUESTIONS_DIR / f"{qid}.json"
    qfile.write_text(json.dumps(question, indent=2))
    return qid


def wait_for_response(qid: str, timeout: int = TIMEOUT) -> dict | None:
    """Block until user responds or timeout."""
    rfile = RESPONSES_DIR / f"{qid}.json"
    start = time.time()
    while time.time() - start < timeout:
        if rfile.exists():
            resp = json.loads(rfile.read_text())
            # Cleanup
            qfile = QUESTIONS_DIR / f"{qid}.json"
            qfile.unlink(missing_ok=True)
            rfile.unlink(missing_ok=True)
            return resp
        time.sleep(0.5)
    return None


# ── Telegram Bot ───────────────────────────────────────────────────────
def is_authorized(update: Update) -> bool:
    if not AUTHORIZED_CHAT:
        return True
    return str(update.effective_chat.id) == AUTHORIZED_CHAT


def find_pending_question() -> Path | None:
    """Find oldest pending question."""
    if not QUESTIONS_DIR.exists():
        return None
    pending = sorted(QUESTIONS_DIR.glob("*.json"))
    for qfile in pending:
        q = json.loads(qfile.read_text())
        if q["status"] == "pending":
            return qfile
    return None



async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    if not is_authorized(update):
        await query.edit_message_text("⛔ Unauthorized.")
        return

    data = query.data
    if not data.startswith("resp:"):
        return

    parts = data.split(":", 3)
    qid = parts[1]
    answer = parts[2] if len(parts) > 2 else ""

    qfile = QUESTIONS_DIR / f"{qid}.json"
    if not qfile.exists():
        await query.edit_message_text("⚠️ Question expired.")
        return

    question = json.loads(qfile.read_text())

    if answer == "opt" and len(parts) > 3:
        # Option selected by index
        idx = int(parts[3])
        answer = question["options"][idx]
    elif answer == "custom":
        # Waiting for free text — mark question as awaiting text
        question["status"] = "awaiting_text"
        qfile.write_text(json.dumps(question, indent=2))
        state = read_state()
        state["awaiting_text_for"] = qid
        write_state(state)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✏️ Ketik jawabanmu di bawah:",
        )
        return
    elif answer == "ack":
        state = read_state()
        state["awaiting_text_for"] = qid
        write_state(state)
        return  # Wait for text message
    elif answer == "toggle" and len(parts) > 3:
        # Multi-select: toggle option
        idx = int(parts[3])
        selected = question.get("selected", [])
        if idx in selected:
            selected.remove(idx)
        else:
            selected.append(idx)
        question["selected"] = selected
        qfile.write_text(json.dumps(question, indent=2))

        # Rebuild buttons with checkmarks
        buttons = []
        row = []
        for i, opt in enumerate(question["options"]):
            prefix = "✅ " if i in selected else ""
            row.append(InlineKeyboardButton(f"{prefix}{opt}", callback_data=f"resp:{qid}:toggle:{i}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([
            InlineKeyboardButton("✅ Selesai", callback_data=f"resp:{qid}:done")
        ])
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        await query.answer(f"{'Dipilih' if idx in selected else 'Dibatal'}: {question['options'][idx]}")
        return
    elif answer == "done":
        # Multi-select: submit selected options
        selected = question.get("selected", [])
        if not selected:
            await query.answer("⚠️ Pilih minimal satu opsi!", show_alert=True)
            return
        answer = ", ".join(question["options"][i] for i in sorted(selected))
    elif answer in ("yes", "no"):
        answer = answer

    # Write response
    resp = {
        "question_id": qid,
        "answer": answer,
        "answered_at": datetime.now().isoformat(),
    }
    rfile = RESPONSES_DIR / f"{qid}.json"
    rfile.write_text(json.dumps(resp, indent=2))

    # Update question status
    question["status"] = "answered"
    qfile.write_text(json.dumps(question, indent=2))

    # Remove buttons only, keep original question visible
    await query.edit_message_reply_markup(reply_markup=None)
    # Send small confirmation below
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"✅ <b>Dijawab:</b> {answer}",
        parse_mode="HTML",
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free text responses."""
    if not is_authorized(update):
        return

    state = read_state()
    awaiting_qid = state.get("awaiting_text_for")

    if not awaiting_qid:
        return  # Not expecting text

    qfile = QUESTIONS_DIR / f"{awaiting_qid}.json"
    if not qfile.exists():
        state.pop("awaiting_text_for", None)
        write_state(state)
        return

    answer = update.message.text.strip()
    resp = {
        "question_id": awaiting_qid,
        "answer": answer,
        "answered_at": datetime.now().isoformat(),
    }
    rfile = RESPONSES_DIR / f"{awaiting_qid}.json"
    rfile.write_text(json.dumps(resp, indent=2))

    question = json.loads(qfile.read_text())
    question["status"] = "answered"
    qfile.write_text(json.dumps(question, indent=2))

    state.pop("awaiting_text_for", None)
    write_state(state)

    await update.message.reply_text(f"✅ Diterima: <code>{answer}</code>", parse_mode="HTML")



async def post_init(app):
    """Start background poller after bot is initialized."""
    asyncio.create_task(poll_questions(app))


async def poll_questions(app):
    """Background task: poll for pending questions and send to Telegram."""
    await asyncio.sleep(2)  # Wait for bot to be ready
    bot = app.bot
    while True:
        try:
            qfile = find_pending_question()
            if qfile:
                question = json.loads(qfile.read_text())
                question["status"] = "sent"
                qfile.write_text(json.dumps(question, indent=2))

                chat_id = int(AUTHORIZED_CHAT) if AUTHORIZED_CHAT else None
                if chat_id:
                    await send_question_to_bot(bot, chat_id, question)
        except Exception as e:
            print(f"Poll error: {e}")
        await asyncio.sleep(1)


async def send_question_to_bot(bot, chat_id: int, question: dict):
    """Send question with optional inline keyboard buttons."""
    qid = question["id"]
    text = question["text"]

    if question["type"] == "confirm" or question["type"] == "yesno":
        keyboard = [
            [
                InlineKeyboardButton("✅ Ya", callback_data=f"resp:{qid}:yes"),
                InlineKeyboardButton("❌ Tidak", callback_data=f"resp:{qid}:no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(
            chat_id=chat_id,
            text=f"❓ <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    elif question["type"] == "options" and question["options"]:
        buttons = []
        row = []
        for i, opt in enumerate(question["options"]):
            row.append(InlineKeyboardButton(opt, callback_data=f"resp:{qid}:opt:{i}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([
            InlineKeyboardButton("✏️ Ketik jawaban...", callback_data=f"resp:{qid}:custom")
        ])
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_id,
            text=f"❓ <b>{text}</b>\n\nPilih salah satu:",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    elif question["type"] == "multi" and question["options"]:
        # Multi-select: toggle buttons + done button
        question["selected"] = []
        qfile = QUESTIONS_DIR / f"{qid}.json"
        qfile.write_text(json.dumps(question, indent=2))
        buttons = []
        row = []
        for i, opt in enumerate(question["options"]):
            row.append(InlineKeyboardButton(opt, callback_data=f"resp:{qid}:toggle:{i}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([
            InlineKeyboardButton("✅ Selesai", callback_data=f"resp:{qid}:done")
        ])
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_id,
            text=f"❓ <b>{text}</b>\n\n📋 Pilih beberapa (ketik\nsatu per satu lalu Selesai):",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    else:
        keyboard = [[
            InlineKeyboardButton("✏️ Ketik jawaban di bawah ↓", callback_data=f"resp:{qid}:ack")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(
            chat_id=chat_id,
            text=f"❓ <b>{text}</b>\n\nKetik jawabanmu:",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )


# ── Commands ───────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized.")
        return

    text = """🤖 <b>NaraCLI Telegram Bridge</b>

<b>Interactive Mode:</b>
NaraCLI akan mengirim pertanyaan ke sini saat butuh input.

<b>Commands:</b>
/run &lt;cmd&gt; - Jalankan shell command
/nara &lt;task&gt; - Jalankan NaraCLI task
/status - Lihat pending questions

Jawaban dikirim langsung atau via inline buttons.
"""
    await update.message.reply_text(text, parse_mode="HTML")


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized.")
        return

    cmd = " ".join(context.args) if context.args else ""
    if not cmd:
        await update.message.reply_text("Usage: /run <command>")
        return

    await update.message.reply_text(f"⏳ <code>{cmd}</code>", parse_mode="HTML")

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd(),
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=TIMEOUT)

        output = stdout.decode(errors="replace").strip()
        err = stderr.decode(errors="replace").strip()
        rc = proc.returncode

        status = "✅" if rc == 0 else "❌"
        parts = [f"{status} <code>{cmd}</code> (rc={rc})"]
        if output:
            if len(output) > 3500:
                output = output[:3500] + "\n... (truncated)"
            parts.append(f"<pre>{output}</pre>")
        if err:
            if len(err) > 1000:
                err = err[:1000] + "\n... (truncated)"
            parts.append(f"<b>stderr:</b>\n<pre>{err}</pre>")

        await update.message.reply_text("\n".join(parts), parse_mode="HTML")

    except asyncio.TimeoutError:
        await update.message.reply_text("❌ Timeout (5 min).")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def run_nara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    task = " ".join(context.args) if context.args else ""
    if not task:
        await update.message.reply_text("Usage: /nara <task>")
        return
    context.args = [f'{NARA_CLI} "{task}"']
    await run_command(update, context)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    pending = list(QUESTIONS_DIR.glob("*.json")) if QUESTIONS_DIR.exists() else []
    count = sum(
        1 for f in pending
        if json.loads(f.read_text())["status"] in ("pending", "sent")
    )
    await update.message.reply_text(f"📋 {count} pertanyaan menunggu jawaban.")


# ── Main ───────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN")
        return

    ensure_dirs()
    # Clear old state
    write_state({})

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("run", run_command))
    app.add_handler(CommandHandler("nara", run_nara))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("🤖 Interactive bridge started.")
    app.run_polling()


if __name__ == "__main__":
    main()
