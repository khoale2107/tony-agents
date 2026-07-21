#!/usr/bin/env python3
"""
Xin nghỉ phép / chi phí có luồng duyệt qua Telegram.

Nhân viên gửi yêu cầu -> bot bắn tin có nút [✅ Duyệt][❌ Từ chối] tới quản lý
(TELEGRAM_CHAT_ID trong .env), ghi vào requests.csv. Quản lý bấm nút, chạy 'poll'
để nhận quyết định: cập nhật trạng thái và sửa lại nội dung tin đã gửi.

  ./run.sh submit-leave "Nguyễn Văn A" 25/07/2026 "Về quê có việc"     xin nghỉ
  ./run.sh submit-expense "Trần Thị B" 850000 "Taxi đi khảo sát"       xin chi phí
  ./run.sh submit-leave "..." 25/07/2026 "..." --dry-run               chỉ xem, không gửi
  ./run.sh poll                                                        nhận quyết định

Chỉ dùng thư viện chuẩn (urllib) — không cần cài gì.
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

LOG = HERE / "requests.csv"
OFFSET_FILE = HERE / ".tg_offset"
HEADERS = ["id", "thời gian", "loại", "nhân viên", "chi tiết", "số tiền",
           "trạng thái", "người quyết", "message_id"]


# ---------- Telegram raw Bot API ----------
def tg(method: str, **params):
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


# ---------- log CSV ----------
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
    ids = [int(r.get("id", 0)) for r in rows if str(r.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


# ---------- gửi yêu cầu ----------
def submit(kind: str, employee: str, detail: str, amount: float, dry: bool) -> None:
    rows = log_read()
    rid = next_id(rows)
    if kind == "leave":
        icon, tieu_de = "🌴", "XIN NGHỈ PHÉP"
        chi_tiet = f"Ngày nghỉ: <b>{detail}</b>"
        detail_plain = f"ngày {detail}"
        amount_str = ""
    else:
        icon, tieu_de = "💸", "XIN CHI PHÍ"
        chi_tiet = f"Nội dung: {detail}\nSố tiền: <b>{fl.fmt_vnd(amount)}</b>"
        detail_plain = detail
        amount_str = str(int(amount))

    text = (f"<b>{icon} {tieu_de} #{rid}</b>\n"
            f"Nhân viên: <b>{employee}</b>\n"
            f"{chi_tiet}\n"
            f"Trạng thái: <i>CHỜ DUYỆT</i>")

    print(f"→ [{tieu_de}] #{rid} — {employee} — {detail_plain}"
          + (f" — {fl.fmt_vnd(amount)}" if kind == "expense" else ""))
    if dry:
        print("--- Nội dung sẽ gửi tới quản lý ---")
        print(text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        print("[✅ Duyệt]  [❌ Từ chối]")
        print("(--dry-run: không gửi Telegram, không ghi log)")
        return

    chat_id = fl.cfg("TELEGRAM_CHAT_ID")
    if not chat_id:
        raise SystemExit("Thiếu TELEGRAM_CHAT_ID (chat id quản lý duyệt) trong .env")
    kb = {"inline_keyboard": [[
        {"text": "✅ Duyệt", "callback_data": f"approve:{rid}"},
        {"text": "❌ Từ chối", "callback_data": f"reject:{rid}"},
    ]]}
    resp = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
              reply_markup=json.dumps(kb))
    msg_id = str(resp.get("result", {}).get("message_id", ""))

    rows.append({
        "id": str(rid),
        "thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "loại": "Nghỉ phép" if kind == "leave" else "Chi phí",
        "nhân viên": employee,
        "chi tiết": detail,
        "số tiền": amount_str,
        "trạng thái": "CHỜ DUYỆT",
        "người quyết": "",
        "message_id": msg_id,
    })
    log_write(rows)
    print(f"Đã gửi yêu cầu #{rid} tới quản lý. Chạy './run.sh poll' để nhận quyết định.")


# ---------- nhận quyết định ----------
def poll() -> None:
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có quyết định mới.")
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
        if rid in idx and idx[rid]["trạng thái"] == "CHỜ DUYỆT":
            idx[rid]["trạng thái"] = "ĐÃ DUYỆT" if action == "approve" else "TỪ CHỐI"
            idx[rid]["người quyết"] = who
            changed = True
            msg = cq["message"]
            new_text = (msg.get("text", "").split("\nTrạng thái")[0]
                        + f"\n<b>→ {idx[rid]['trạng thái']}</b> bởi {who}")
            tg("editMessageText", chat_id=msg["chat"]["id"], message_id=msg["message_id"],
               parse_mode="HTML", text=new_text)
            tg("answerCallbackQuery", callback_query_id=cq["id"], text="Đã ghi nhận")
            print(f"#{rid} [{idx[rid]['loại']}] {idx[rid]['nhân viên']}: "
                  f"{idx[rid]['trạng thái']} bởi {who}")
    OFFSET_FILE.write_text(str(offset))
    if changed:
        log_write(rows)
    else:
        print("Không có yêu cầu nào cần cập nhật.")


# ---------- CLI ----------
def _usage() -> None:
    print("Cách dùng:\n"
          '  ./run.sh submit-leave "<Nhân viên>" <ngày> "<lý do>" [--dry-run]\n'
          '  ./run.sh submit-expense "<Nhân viên>" <số tiền> "<nội dung>" [--dry-run]\n'
          "  ./run.sh poll")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        _usage()
        return
    cmd = args[0]
    dry = "--dry-run" in args
    rest = [a for a in args[1:] if not a.startswith("-")]

    if cmd == "poll":
        poll()
    elif cmd == "submit-leave":
        if len(rest) < 3:
            print('Thiếu tham số: submit-leave "<Nhân viên>" <ngày> "<lý do>"')
            return
        employee, ngay = rest[0], rest[1]
        ly_do = " ".join(rest[2:])
        submit("leave", employee, f"{ngay} — {ly_do}", 0.0, dry)
    elif cmd == "submit-expense":
        if len(rest) < 3:
            print('Thiếu tham số: submit-expense "<Nhân viên>" <số tiền> "<nội dung>"')
            return
        employee = rest[0]
        amount = fl.parse_amount(rest[1])
        noi_dung = " ".join(rest[2:])
        submit("expense", employee, noi_dung, amount, dry)
    else:
        print(f"Lệnh không hiểu: {cmd}")
        _usage()


if __name__ == "__main__":
    main()
