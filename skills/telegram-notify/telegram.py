#!/usr/bin/env python3
"""
Opencode helper — kirim pertanyaan ke Telegram, tunggu jawaban.

Usage:
  # Tanya bebas
  python telegram.py ask "Mau patch fitur apa?"

  # Tanya dengan pilihan (inline buttons)
  python telegram.py ask --options "Fix auth,Add login,Refactor db" "Pilih fitur:"

  # Yes/No confirmation
  python telegram.py confirm "Patch file config.yaml?"

  # Kirim notifikasi (no response needed)
  python telegram.py notify "✅ Build selesai"

  # Tunggu jawaban (blocking)
  python telegram.py wait [timeout]

Exit codes:
  0 = success
  1 = timeout / error
  stdout = jawaban user
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

STATE_DIR = Path(os.environ.get("OPENCODE_STATE_DIR", "/tmp/telegram-notify"))
QUESTIONS_DIR = STATE_DIR / "questions"
RESPONSES_DIR = STATE_DIR / "responses"


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)


def ask(text: str, options: list[str] | None = None, qtype: str = "text") -> str:
    """Ask a question and block until answered."""
    import subprocess

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

    qfile = QUESTIONS_DIR / f"{qid}.json"
    qfile.write_text(json.dumps(question, indent=2))

    print(f"📤 Question sent: {qid}", file=sys.stderr)

    # Wait for response
    rfile = RESPONSES_DIR / f"{qid}.json"
    timeout = 300
    start = time.time()

    while time.time() - start < timeout:
        if rfile.exists():
            resp = json.loads(rfile.read_text())
            answer = resp["answer"]
            # Cleanup
            qfile.unlink(missing_ok=True)
            rfile.unlink(missing_ok=True)
            return answer
        time.sleep(0.5)

    # Timeout
    qfile.unlink(missing_ok=True)
    print("⏰ Timeout waiting for response.", file=sys.stderr)
    sys.exit(1)


def confirm(text: str) -> bool:
    """Ask yes/no, return True/False."""
    answer = ask(f"{text}\n\n(Pilih Ya/Tidak)", qtype="confirm")
    return answer == "yes"


def notify(text: str):
    """Send notification (no response)."""
    try:
        import subprocess

        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

        if not bot_token or not chat_id:
            print("⚠️ TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set.", file=sys.stderr)
            return

        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            }),
        ], capture_output=True)
    except Exception as e:
        print(f"⚠️ Notify failed: {e}", file=sys.stderr)


def wait_for_response(timeout: int = 300) -> str:
    """Wait for the oldest pending question's response."""
    import subprocess

    # Find pending questions
    if not QUESTIONS_DIR.exists():
        print("No pending questions.", file=sys.stderr)
        sys.exit(1)

    pending = sorted(QUESTIONS_DIR.glob("*.json"))
    for qfile in pending:
        q = json.loads(qfile.read_text())
        if q["status"] in ("pending", "sent"):
            qid = q["id"]
            rfile = RESPONSES_DIR / f"{qid}.json"
            start = time.time()
            while time.time() - start < timeout:
                if rfile.exists():
                    resp = json.loads(rfile.read_text())
                    qfile.unlink(missing_ok=True)
                    rfile.unlink(missing_ok=True)
                    return resp["answer"]
                time.sleep(0.5)
            print(f"⏰ Timeout for {qid}", file=sys.stderr)
            sys.exit(1)

    print("No pending questions.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Opencode Telegram Bridge Helper")
    sub = parser.add_subparsers(dest="command", required=True)

    # ask
    ask_p = sub.add_parser("ask", help="Ask a question")
    ask_p.add_argument("text", help="Question text")
    ask_p.add_argument("--options", help="Comma-separated options")
    ask_p.add_argument("--type", default="text", choices=["text", "options", "yesno", "multi"])
    ask_p.add_argument("--multi", action="store_true", help="Multi-select mode")

    # confirm
    conf_p = sub.add_parser("confirm", help="Yes/No confirmation")
    conf_p.add_argument("text", help="Confirmation text")

    # notify
    notify_p = sub.add_parser("notify", help="Send notification")
    notify_p.add_argument("text", help="Notification text")

    # wait
    wait_p = sub.add_parser("wait", help="Wait for response")
    wait_p.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()

    if args.command == "ask":
        options = args.options.split(",") if args.options else None
        if args.multi and options:
            qtype = "multi"
        elif options:
            qtype = "options"
        else:
            qtype = args.type
        answer = ask(args.text, options=options, qtype=qtype)
        print(answer)

    elif args.command == "confirm":
        result = confirm(args.text)
        print("yes" if result else "no")

    elif args.command == "notify":
        notify(args.text)

    elif args.command == "wait":
        answer = wait_for_response(args.timeout)
        print(answer)


if __name__ == "__main__":
    main()
