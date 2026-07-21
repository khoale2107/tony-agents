#!/usr/bin/env python3
"""
Human-in-the-loop — AI soạn câu trả lời khách, đẩy qua Telegram để bạn
DUYỆT / SỬA / BỎ trước khi gửi cho khách.

  ./run.sh submit --dry-run    xem các câu AI soạn (không gửi Telegram)
  ./run.sh submit              soạn + đẩy lên Telegram chờ bạn bấm
  ./run.sh poll                nhận quyết định, câu đã Duyệt sẽ gửi cho khách (qua connector seam)

Đọc queue.csv (cột: Khách | Kênh | Tin nhắn). Kiến thức để trả lời ở knowledge.md (tuỳ chọn).
- Bấm ✅ Duyệt: gửi nguyên văn cho khách.
- Bấm ❌ Bỏ: không gửi.
- Muốn SỬA: trả lời (reply) tin đó trên Telegram bằng nội dung mới -> sẽ gửi bản của bạn.
Dùng GÓI Claude Code để soạn, không cần API key.
"""
from __future__ import annotations

import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")
LOG = HERE / "replies.csv"
OFFSET_FILE = HERE / ".tg_offset"
MAP_FILE = HERE / ".tg_msgmap.json"   # message_id -> request id
HEADERS = ["id", "thời gian", "khách", "kênh", "tin khách", "câu trả lời", "trạng thái"]


def tg(method: str, **params):
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


def log_read() -> list[dict]:
    if not LOG.exists():
        return []
    with LOG.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def log_write(rows: list[dict]):
    with LOG.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def read_queue() -> list[dict]:
    p = HERE / "queue.csv"
    if not p.exists():
        p = HERE / "queue_example.csv"
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def load_knowledge() -> str:
    for name in ("knowledge.md", "knowledge_example.md"):
        p = HERE / name
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    return ""


def draft_reply(khach: str, tin: str, kb: str) -> str:
    ct = fl.cfg("COMPANY_NAME", "công ty")
    prompt = (f"Bạn là CSKH của {ct}, trả lời khách thân thiện, chuyên nghiệp, ngắn gọn. "
              + (f"CHỈ dùng kiến thức sau, không bịa giá/chính sách:\n{kb}\n\n" if kb else "")
              + f"Khách '{khach}' nhắn: \"{tin}\". Soạn câu trả lời. Chỉ trả về nội dung.")
    return fl.ask_ai(prompt)


def submit(dry: bool):
    rows_q = read_queue()
    kb = load_knowledge()
    chat_id = fl.cfg("TELEGRAM_CHAT_ID")
    log = log_read()
    start_id = len(log) + 1
    msgmap = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}

    for i, r in enumerate(rows_q):
        rid = start_id + i
        khach = r.get("Khách", "khách")
        tin = r.get("Tin nhắn", "")
        reply = draft_reply(khach, tin, kb)
        if dry:
            print(f"\n#{rid} · {khach} ({r.get('Kênh','')}):\n  Khách: {tin}\n  AI: {reply}")
            continue
        if not chat_id:
            raise SystemExit("Thiếu TELEGRAM_CHAT_ID trong .env")
        kbd = {"inline_keyboard": [[
            {"text": "✅ Duyệt", "callback_data": f"ok:{rid}"},
            {"text": "❌ Bỏ", "callback_data": f"skip:{rid}"},
        ]]}
        text = (f"<b>✉️ TRẢ LỜI KHÁCH #{rid}</b> ({r.get('Kênh','')})\n"
                f"👤 {khach}: {tin}\n\n"
                f"🤖 <b>Đề xuất:</b>\n{reply}\n\n"
                f"<i>Duyệt để gửi nguyên văn, hoặc reply tin này bằng nội dung mới để SỬA.</i>")
        resp = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
                  reply_markup=json.dumps(kbd))
        mid = resp.get("result", {}).get("message_id")
        if mid:
            msgmap[str(mid)] = rid
        log.append({"id": str(rid), "thời gian": datetime.now().strftime("%d/%m %H:%M"),
                    "khách": khach, "kênh": r.get("Kênh", ""), "tin khách": tin,
                    "câu trả lời": reply, "trạng thái": "CHỜ DUYỆT"})
    if not dry:
        log_write(log)
        MAP_FILE.write_text(json.dumps(msgmap, ensure_ascii=False))
        print(f"Đã đẩy {len(rows_q)} câu trả lời lên Telegram. Chạy './run.sh poll' để nhận quyết định.")


def deliver(rec: dict):
    """Gửi câu đã duyệt cho khách qua connector (seam)."""
    try:
        import connector as conn
    except ImportError:
        print(f"  [i] (Chưa có connector.py — chưa gửi thật cho {rec['khách']}. "
              "Nhờ Claude Code viết connector để nối Zalo/Messenger.)")
        return
    conn.send_message(rec.get("kênh", ""), rec.get("khách", ""), rec.get("câu trả lời", ""))
    print(f"  → Đã gửi cho {rec['khách']}.")


def poll():
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có quyết định mới.")
        return
    rows = log_read()
    idx = {r["id"]: r for r in rows}
    msgmap = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}

    for u in updates:
        offset = u["update_id"] + 1
        cq = u.get("callback_query")
        msg = u.get("message")
        if cq:
            action, _, rid = cq.get("data", "").partition(":")
            who = cq.get("from", {}).get("first_name", "?")
            if rid in idx and idx[rid]["trạng thái"] == "CHỜ DUYỆT":
                if action == "ok":
                    idx[rid]["trạng thái"] = "ĐÃ DUYỆT"
                    m = cq["message"]
                    tg("editMessageText", chat_id=m["chat"]["id"], message_id=m["message_id"],
                       parse_mode="HTML", text=m.get("text", "") + f"\n\n<b>→ ĐÃ DUYỆT</b> bởi {who}")
                    print(f"#{rid}: ĐÃ DUYỆT bởi {who}")
                    deliver(idx[rid])
                else:
                    idx[rid]["trạng thái"] = "BỎ"
                    m = cq["message"]
                    tg("editMessageText", chat_id=m["chat"]["id"], message_id=m["message_id"],
                       parse_mode="HTML", text=m.get("text", "") + f"\n\n<b>→ BỎ</b> bởi {who}")
                    print(f"#{rid}: BỎ bởi {who}")
                tg("answerCallbackQuery", callback_query_id=cq["id"], text="Đã ghi nhận")
        elif msg and msg.get("reply_to_message"):
            parent = str(msg["reply_to_message"].get("message_id"))
            rid = str(msgmap.get(parent, ""))
            if rid in idx and idx[rid]["trạng thái"] == "CHỜ DUYỆT":
                idx[rid]["câu trả lời"] = msg.get("text", "")
                idx[rid]["trạng thái"] = "ĐÃ SỬA & DUYỆT"
                print(f"#{rid}: ĐÃ SỬA & DUYỆT")
                deliver(idx[rid])
    OFFSET_FILE.write_text(str(offset))
    log_write(rows)


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "submit"
    if cmd == "submit":
        submit(dry="--dry-run" in args)
    elif cmd == "poll":
        poll()
    else:
        print("Dùng: ./run.sh submit [--dry-run]  |  ./run.sh poll")


if __name__ == "__main__":
    main()
