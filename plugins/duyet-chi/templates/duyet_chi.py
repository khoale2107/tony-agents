#!/usr/bin/env python3
"""
Duyệt chi đa cấp qua Telegram.

Định tuyến theo số tiền:
  < 5.000.000       -> Trưởng nhóm
  5.000.000-20.000.000 -> Quản lý
  > 20.000.000      -> CEO
Gửi yêu cầu duyệt (nút Duyệt/Từ chối) tới đúng người, ghi log requests.csv.

  ./run.sh submit "Mua vật tư tiệc cưới" 8000000     gửi 1 yêu cầu duyệt
  ./run.sh submit "..." 8000000 --dry-run            chỉ xem sẽ gửi cho ai
  ./run.sh poll                                       nhận quyết định Duyệt/Từ chối

Ngưỡng và chat id cấu hình trong .env. Dùng thư viện chuẩn (không cần cài gì).
"""
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
LOG = HERE / "requests.csv"
OFFSET_FILE = HERE / ".tg_offset"
HEADERS = ["id", "thời gian", "nội dung", "số tiền", "cấp duyệt", "trạng thái", "người quyết"]


def route(amount: float):
    t1 = fl.parse_amount(fl.cfg("TIER1_MAX", "5000000"))
    t2 = fl.parse_amount(fl.cfg("TIER2_MAX", "20000000"))
    if amount < t1:
        return "Trưởng nhóm", fl.cfg("CHAT_TRUONG_NHOM")
    if amount <= t2:
        return "Quản lý", fl.cfg("CHAT_QUAN_LY")
    return "CEO", fl.cfg("CHAT_CEO")


def tg(method: str, **params):
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


def next_id() -> int:
    if not LOG.exists():
        return 1
    with LOG.open(encoding="utf-8-sig") as f:
        return sum(1 for _ in csv.reader(f))  # gồm header -> = số dòng data + 1... đủ để tăng dần


def log_write(rows: list[dict]):
    with LOG.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def log_read() -> list[dict]:
    if not LOG.exists():
        return []
    with LOG.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def submit(desc: str, amount: float, dry: bool):
    level, chat_id = route(amount)
    print(f"→ {fl.fmt_vnd(amount)} : duyệt bởi <{level}>")
    if dry:
        print("(--dry-run: không gửi)")
        return
    if not chat_id:
        raise SystemExit(f"Chưa cấu hình chat id cho cấp '{level}' trong .env")
    rid = next_id()
    kb = {"inline_keyboard": [[
        {"text": "✅ Duyệt", "callback_data": f"approve:{rid}"},
        {"text": "❌ Từ chối", "callback_data": f"reject:{rid}"},
    ]]}
    text = (f"<b>🧾 YÊU CẦU DUYỆT CHI #{rid}</b>\n"
            f"Nội dung: {desc}\n"
            f"Số tiền: <b>{fl.fmt_vnd(amount)}</b>\n"
            f"Cấp duyệt: {level}")
    tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
       reply_markup=json.dumps(kb))
    rows = log_read()
    rows.append({"id": str(rid), "thời gian": datetime.now().strftime("%d/%m %H:%M"),
                 "nội dung": desc, "số tiền": str(int(amount)), "cấp duyệt": level,
                 "trạng thái": "CHỜ DUYỆT", "người quyết": ""})
    log_write(rows)
    print(f"Đã gửi yêu cầu #{rid} tới {level}. Chạy './run.sh poll' để nhận quyết định.")


def poll():
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có quyết định mới.")
        return
    rows = log_read()
    idx = {r["id"]: r for r in rows}
    for u in updates:
        offset = u["update_id"] + 1
        cq = u.get("callback_query")
        if not cq:
            continue
        action, _, rid = cq.get("data", "").partition(":")
        who = cq.get("from", {}).get("first_name", "?")
        if rid in idx and idx[rid]["trạng thái"] == "CHỜ DUYỆT":
            idx[rid]["trạng thái"] = "ĐÃ DUYỆT" if action == "approve" else "TỪ CHỐI"
            idx[rid]["người quyết"] = who
            msg = cq["message"]
            tg("editMessageText", chat_id=msg["chat"]["id"], message_id=msg["message_id"],
               parse_mode="HTML",
               text=msg.get("text", "") + f"\n\n<b>→ {idx[rid]['trạng thái']}</b> bởi {who}")
            tg("answerCallbackQuery", callback_query_id=cq["id"], text="Đã ghi nhận")
            print(f"#{rid}: {idx[rid]['trạng thái']} bởi {who}")
    OFFSET_FILE.write_text(str(offset))
    log_write(rows)


def main():
    args = sys.argv[1:]
    if not args:
        print("Cách dùng:\n  ./run.sh submit \"nội dung\" <số tiền> [--dry-run]\n  ./run.sh poll")
        return
    cmd = args[0]
    if cmd == "poll":
        poll()
    elif cmd == "submit":
        rest = [a for a in args[1:] if not a.startswith("-")]
        if len(rest) < 2:
            print("Thiếu tham số: submit \"nội dung\" <số tiền>")
            return
        desc = rest[0]
        amount = fl.parse_amount(rest[-1])
        submit(desc, amount, dry="--dry-run" in args)
    else:
        print(f"Lệnh không hiểu: {cmd}")


if __name__ == "__main__":
    main()
