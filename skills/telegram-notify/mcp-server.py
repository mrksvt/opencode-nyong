#!/usr/bin/env python3
"""
Opencode Telegram MCP Server
============================
MCP server untuk interactive Telegram bridge.
Hidup saat Opencode session aktif.

Tools:
  telegram_ask       - Tanya bebas
  telegram_ask_multi - Multi-select (pilih beberapa)
  telegram_confirm   - Ya/Tidak
  telegram_notify    - Kirim notifikasi
"""
import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ── Config ──────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_DIR = Path(os.environ.get("OPENCODE_STATE_DIR", "/tmp/telegram-notify"))
QUESTIONS_DIR = STATE_DIR / "questions"
RESPONSES_DIR = STATE_DIR / "responses"
TIMEOUT = int(os.environ.get("TELEGRAM_TIMEOUT", "120"))

# ── State ───────────────────────────────────────────────────────────────
def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

def create_question(text: str, options: list[str] | None = None, qtype: str = "text") -> str:
    ensure_dirs()
    qid = datetime.now().strftime("%Y%m%d%H%M%S%f")
    question = {
        "id": qid,
        "type": qtype,
        "text": text,
        "options": options or [],
        "created_at": datetime.now().isoformat(),
        "status": "pending",
    }
    (QUESTIONS_DIR / f"{qid}.json").write_text(json.dumps(question, indent=2))
    return qid

def wait_for_response(qid: str, timeout: int = TIMEOUT) -> str:
    """Block until user responds or timeout."""
    rfile = RESPONSES_DIR / f"{qid}.json"
    start = time.time()
    while time.time() - start < timeout:
        if rfile.exists():
            resp = json.loads(rfile.read_text())
            (QUESTIONS_DIR / f"{qid}.json").unlink(missing_ok=True)
            rfile.unlink(missing_ok=True)
            return resp["answer"]
        time.sleep(0.5)
    # Cleanup on timeout
    (QUESTIONS_DIR / f"{qid}.json").unlink(missing_ok=True)
    raise TimeoutError(f"Telegram response timeout ({timeout}s)")

# ── MCP Server ──────────────────────────────────────────────────────────
mcp = FastMCP("telegram-notify")


@mcp.tool()
def telegram_ask(question: str, options: Optional[str] = None) -> str:
    """
    Kirim pertanyaan ke Telegram, tunggu jawaban.
    
    Args:
        question: Teks pertanyaan
        options: Opsi dipisah koma (opsional). Contoh: "Fix auth,Add login,Refactor DB"
    
    Returns:
        Jawaban dari user Telegram
    """
    opts = options.split(",") if options else None
    qtype = "options" if opts else "text"
    qid = create_question(question, opts, qtype)
    return wait_for_response(qid)


@mcp.tool()
def telegram_ask_multi(question: str, options: str) -> str:
    """
    Kirim pertanyaan multi-select ke Telegram.
    User bisa pilih lebih dari 1 opsi.
    
    Args:
        question: Teks pertanyaan
        options: Opsi dipisah koma. Contoh: "Auth,Database,API,UI"
    
    Returns:
        Opsi yang dipilih, dipisah koma
    """
    opts = options.split(",")
    qid = create_question(question, opts, "multi")
    return wait_for_response(qid)


@mcp.tool()
def telegram_confirm(question: str) -> str:
    """
    Konfirmasi Ya/Tidak ke Telegram.
    
    Args:
        question: Teks konfirmasi
    
    Returns:
        "yes" atau "no"
    """
    qid = create_question(question, qtype="confirm")
    return wait_for_response(qid)


@mcp.tool()
def telegram_notify(message: str) -> str:
    """
    Kirim notifikasi ke Telegram (tanpa response).
    
    Args:
        message: Teks notifikasi
    
    Returns:
        "ok" jika berhasil
    """
    import subprocess
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    if not bot_token or not chat_id:
        return "error: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set"
    
    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
            }),
        ], capture_output=True, text=True, timeout=10)
        
        resp = json.loads(result.stdout)
        return "ok" if resp.get("ok") else f"error: {resp.get('description', 'unknown')}"
    except Exception as e:
        return f"error: {e}"




# ── Telegram Bot (inline, runs with MCP server) ────────────────────────
_bot_app = None
_poll_task = None


async def _handle_callback(update, context):
    """Handle inline keyboard button presses."""
    from telegram import Update
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("resp:"):
        return
    
    parts = data.split(":", 3)
    qid = parts[1]
    answer = parts[2] if len(parts) > 2 else ""
    
    qfile = QUESTIONS_DIR / f"{qid}.json"
    if not qfile.exists():
        return
    
    question = json.loads(qfile.read_text())
    
    if answer == "toggle" and len(parts) > 3:
        idx = int(parts[3])
        selected = question.get("selected", [])
        if idx in selected:
            selected.remove(idx)
        else:
            selected.append(idx)
        question["selected"] = selected
        qfile.write_text(json.dumps(question, indent=2))
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
        buttons.append([InlineKeyboardButton("✅ Selesai", callback_data=f"resp:{qid}:done")])
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        await query.answer(f"{'Dipilih' if idx in selected else 'Dibatal'}: {question['options'][idx]}")
        return
    
    elif answer == "done":
        selected = question.get("selected", [])
        if not selected:
            await query.answer("⚠️ Pilih minimal satu opsi!", show_alert=True)
            return
        answer = ", ".join(question["options"][i] for i in sorted(selected))
    
    elif answer == "opt" and len(parts) > 3:
        idx = int(parts[3])
        answer = question["options"][idx]
    
    elif answer == "custom":
        question["status"] = "awaiting_text"
        qfile.write_text(json.dumps(question, indent=2))
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✏️ Ketik jawabanmu di bawah:",
        )
        return
    
    elif answer == "ack":
        return
    
    resp = {
        "question_id": qid,
        "answer": answer,
        "answered_at": datetime.now().isoformat(),
    }
    (RESPONSES_DIR / f"{qid}.json").write_text(json.dumps(resp, indent=2))
    
    question["status"] = "answered"
    qfile.write_text(json.dumps(question, indent=2))
    
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"✅ <b>Dijawab:</b> {answer}",
        parse_mode="HTML",
    )


async def _handle_text(update, context):
    """Handle free text responses."""
    state_file = STATE_DIR / "state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    awaiting_qid = state.get("awaiting_text_for")
    
    if not awaiting_qid:
        return
    
    qfile = QUESTIONS_DIR / f"{awaiting_qid}.json"
    if not qfile.exists():
        state.pop("awaiting_text_for", None)
        state_file.write_text(json.dumps(state))
        return
    
    answer = update.message.text.strip()
    resp = {
        "question_id": awaiting_qid,
        "answer": answer,
        "answered_at": datetime.now().isoformat(),
    }
    (RESPONSES_DIR / f"{awaiting_qid}.json").write_text(json.dumps(resp, indent=2))
    
    question = json.loads(qfile.read_text())
    question["status"] = "answered"
    qfile.write_text(json.dumps(question, indent=2))
    
    state.pop("awaiting_text_for", None)
    state_file.write_text(json.dumps(state))
    
    await update.message.reply_text(f"✅ <b>Dijawab:</b> <code>{answer}</code>", parse_mode="HTML")


_poll_task = None


async def _question_poll_loop():
    """Poll for pending questions and send to Telegram (no JobQueue dependency)."""
    if not BOT_TOKEN or not CHAT_ID:
        return
    while True:
        try:
            await _poll_questions()
        except Exception as e:
            print(f"Poll error: {e}", file=sys.stderr)
        await asyncio.sleep(1)


async def _poll_questions():
    """Single poll iteration — send pending questions to Telegram."""
    if not _bot_app or not _bot_app.bot:
        return
    pending = sorted(QUESTIONS_DIR.glob("*.json")) if QUESTIONS_DIR.exists() else []
    for qfile in pending:
        q = json.loads(qfile.read_text())
        if q["status"] != "pending":
            continue

        q["status"] = "sent"
        qfile.write_text(json.dumps(q, indent=2))

        qid = q["id"]
        text = q["text"]
        bot = _bot_app.bot
        chat_id = int(CHAT_ID)

        if q["type"] in ("confirm", "yesno"):
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[
                InlineKeyboardButton("✅ Ya", callback_data=f"resp:{qid}:yes"),
                InlineKeyboardButton("❌ Tidak", callback_data=f"resp:{qid}:no"),
            ]]
            await bot.send_message(
                chat_id=chat_id,
                text=f"❓ <b>{text}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif q["type"] == "multi" and q["options"]:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            q["selected"] = []
            qfile.write_text(json.dumps(q, indent=2))
            buttons = []
            row = []
            for i, opt in enumerate(q["options"]):
                row.append(InlineKeyboardButton(opt, callback_data=f"resp:{qid}:toggle:{i}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton("✅ Selesai", callback_data=f"resp:{qid}:done")])
            await bot.send_message(
                chat_id=chat_id,
                text=f"❓ <b>{text}</b>\n\n📋 Pilih beberapa (ketik\nsatu per satu lalu Selesai):",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons),
            )

        elif q["type"] == "options" and q["options"]:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            buttons = []
            row = []
            for i, opt in enumerate(q["options"]):
                row.append(InlineKeyboardButton(opt, callback_data=f"resp:{qid}:opt:{i}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton("✏️ Ketik jawaban...", callback_data=f"resp:{qid}:custom")])
            await bot.send_message(
                chat_id=chat_id,
                text=f"❓ <b>{text}</b>\n\nPilih salah satu:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons),
            )

        else:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("✏️ Ketik jawaban di bawah ↓", callback_data=f"resp:{qid}:ack")]]
            await bot.send_message(
                chat_id=chat_id,
                text=f"❓ <b>{text}</b>\n\nKetik jawabanmu:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )


async def _start_bot():
    """Start Telegram bot in background."""
    global _bot_app, _poll_task
    if not BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not set, bot disabled", file=sys.stderr)
        return
    
    try:
        from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, filters
        
        _bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
        _bot_app.add_handler(CallbackQueryHandler(_handle_callback))
        _bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_text))
        
        await _bot_app.initialize()
        await _bot_app.start()
        await _bot_app.updater.start_polling(drop_pending_updates=True)
        
        _poll_task = asyncio.create_task(_question_poll_loop())
        
        print(f"🤖 Telegram bot started (@{BOT_TOKEN.split(':')[0]}...)", file=sys.stderr)
    except Exception as e:
        print(f"❌ Telegram bot failed to start: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


async def _stop_bot():
    """Stop Telegram bot."""
    global _bot_app, _poll_task
    if _poll_task:
        _poll_task.cancel()
        try:
            await _poll_task
        except asyncio.CancelledError:
            pass
    if _bot_app:
        await _bot_app.updater.stop()
        await _bot_app.stop()
        await _bot_app.shutdown()
        print("🤖 Telegram bot stopped.", file=sys.stderr)


# ── Run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ensure_dirs()
    # Clean old state
    for f in QUESTIONS_DIR.glob("*.json"):
        f.unlink(missing_ok=True)
    for f in RESPONSES_DIR.glob("*.json"):
        f.unlink(missing_ok=True)
    
    async def _run_bot_safe():
        try:
            await _start_bot()
        except Exception as e:
            print(f"❌ Bot startup crashed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    async def main():
        print("🤖 Opencode Telegram MCP Server starting...", file=sys.stderr)
        asyncio.create_task(_run_bot_safe())
        await mcp.run_stdio_async()
    
    try:
        asyncio.run(main())
    finally:
        if _bot_app:
            asyncio.run(_stop_bot())
