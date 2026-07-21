#!/usr/bin/env python3
"""
Xác nhận thanh toán qua nút bấm Telegram.

Gửi 1 tin nhắn kèm nút [✅ Đã nhận tiền][❌ Chưa] tới kế toán, ghi payments.csv
trạng thái CHỜ. Khi kế toán bấm nút, chạy poll để cập nhật ĐÃ XÁC NHẬN / CHƯA,
sửa lại tin nhắn và lưu offset.

  python3 payment_confirm.py submit DH001 5000000            gửi yêu cầu xác nhận
  python3 payment_confirm.py submit DH001 5000000 --dry-run  chỉ xem sẽ gửi gì
  python3 payment_confirm.py poll                            nhận kết quả bấm nút

Chat id kế toán + token bot cấu hình trong .env. Dùng thư viện chuẩn (urllib).
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
LOG = HERE / "payments.csv"
OFFSET_FILE = HERE / ".tg_offset"
HEADERS = ["id", "mã đơn", "số tiền", "thời gian", "trạng thái", "người xác nhận", "message_id"]


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


def log_write(rows: list[dict]) -> None:
    with LOG.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def next_id(rows: list[dict]) -> int:
    ids = [int(r["id"]) for r in rows if str(r.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


def render(rid: int, ma_don: str, amount: float, status: str, who: str = "") -> str:
    icon = {"CHỜ": "⏳", "ĐÃ XÁC NHẬN": "✅", "CHƯA": "❌"}.get(status, "⏳")
    text = (f"<b>💳 XÁC NHẬN THANH TOÁN #{rid}</b>\n"
            f"Mã đơn: <b>{ma_don}</b>\n"
            f"Số tiền: <b>{fl.fmt_vnd(amount)}</b>\n"
            f"Trạng thái: {icon} <b>{status}</b>")
    if who:
        text += f"\n<i>Kế toán: {who}</i>"
    return text


def submit(ma_don: str, amount: float, dry: bool) -> None:
    rows = log_read()
    rid = next_id(rows)
    text = render(rid, ma_don, amount, "CHỜ")
    kb = {"inline_keyboard": [[
        {"text": "✅ Đã nhận tiền", "callback_data": f"ok:{rid}"},
        {"text": "❌ Chưa", "callback_data": f"no:{rid}"},
    ]]}
    if dry:
        print("=== (--dry-run) SẼ GỬI TỚI KẾ TOÁN ===")
        print(text.replace("<b>", "").replace("</b>", "")
                  .replace("<i>", "").replace("</i>", ""))
        print("Nút: [✅ Đã nhận tiền] [❌ Chưa]")
        print(f"callback_data: ok:{rid} / no:{rid}")
        print("(không gửi Telegram, không ghi payments.csv)")
        return
    chat_id = fl.cfg("TELEGRAM_CHAT_ID")
    if not chat_id:
        raise SystemExit("Thiếu TELEGRAM_CHAT_ID (chat kế toán) trong .env")
    resp = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
              reply_markup=json.dumps(kb))
    msg_id = str(resp.get("result", {}).get("message_id", ""))
    rows.append({
        "id": str(rid), "mã đơn": ma_don, "số tiền": str(int(amount)),
        "thời gian": datetime.now().strftime("%d/%m %H:%M"),
        "trạng thái": "CHỜ", "người xác nhận": "", "message_id": msg_id,
    })
    log_write(rows)
    print(f"Đã gửi yêu cầu xác nhận #{rid} ({ma_don} - {fl.fmt_vnd(amount)}) tới kế toán.")
    print("Chạy: python3 payment_confirm.py poll   để nhận kết quả bấm nút.")


def poll() -> None:
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có thao tác mới.")
        return
    rows = log_read()
    idx = {r["id"]: r for r in rows}
    changed = False
    for u in updates:
        offset = u["update_id"] + 1
        cq = u.get("callback_query")
        if not cq:
            continue
        action, _, rid = cq.get("data", "").partition(":")
        who = cq.get("from", {}).get("first_name", "?")
        r = idx.get(rid)
        if r and r["trạng thái"] == "CHỜ":
            r["trạng thái"] = "ĐÃ XÁC NHẬN" if action == "ok" else "CHƯA"
            r["người xác nhận"] = who
            amount = fl.parse_amount(r["số tiền"])
            msg = cq["message"]
            tg("editMessageText", chat_id=msg["chat"]["id"], message_id=msg["message_id"],
               parse_mode="HTML",
               text=render(int(rid), r["mã đơn"], amount, r["trạng thái"], who))
            tg("answerCallbackQuery", callback_query_id=cq["id"], text="Đã ghi nhận")
            print(f"#{rid} ({r['mã đơn']}): {r['trạng thái']} bởi {who}")
            changed = True
    OFFSET_FILE.write_text(str(offset))
    if changed:
        log_write(rows)
    else:
        print("Không có nút xác nhận nào được bấm.")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Cách dùng:\n"
              "  python3 payment_confirm.py submit <mã đơn> <số tiền> [--dry-run]\n"
              "  python3 payment_confirm.py poll")
        return
    cmd = args[0]
    if cmd == "poll":
        poll()
    elif cmd == "submit":
        rest = [a for a in args[1:] if not a.startswith("-")]
        if len(rest) < 2:
            print("Thiếu tham số: submit <mã đơn> <số tiền>")
            return
        ma_don = rest[0]
        amount = fl.parse_amount(rest[-1])
        submit(ma_don, amount, dry="--dry-run" in args)
    else:
        print(f"Lệnh không hiểu: {cmd}. Dùng: submit | poll")


if __name__ == "__main__":
    main()
