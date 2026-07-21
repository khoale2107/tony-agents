#!/usr/bin/env python3
"""
Chấm công qua bot Telegram — nhân viên gõ /checkin khi đến, /checkout khi về.
Bot ghi vào attendance.csv (Nhân viên, Ngày, Giờ vào, Giờ ra) và trả lời xác nhận.

  ./run.sh poll                 đọc tin mới (getUpdates), ghi công, lưu offset .tg_offset
  ./run.sh report --dry-run     in bảng công HÔM NAY ra màn hình (không gửi Telegram)
  ./run.sh report               gửi bảng công hôm nay vào Telegram (chốt ca cuối ngày)
  ./run.sh --dry-run            = report --dry-run

Lệnh nhân viên gõ trong chat với bot (hoặc trong nhóm, tắt Privacy Mode):
  /checkin   -> ghi Giờ vào (lần đầu trong ngày)
  /checkout  -> ghi Giờ ra (ghi đè để lấy lần về mới nhất)
  /congtoi   -> bot trả lời tình trạng công hôm nay của người gõ

Tên người chấm lấy từ chính người gửi trong Telegram (first_name + last_name / username).
AI (GÓI Claude Code, fl.ask_ai) chỉ dùng để viết dòng nhận xét cuối bảng report khi bật AI_SUMMARY=1.
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

OFFSET_FILE = HERE / ".tg_offset"
DATA_FILE = HERE / "attendance.csv"
HEADERS = ["Nhân viên", "Ngày", "Giờ vào", "Giờ ra"]


# ---------- Telegram helper ----------
def tg(method: str, **params):
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


def sender_name(frm: dict) -> str:
    parts = [frm.get("first_name", ""), frm.get("last_name", "")]
    name = " ".join(p for p in parts if p).strip()
    if not name:
        name = frm.get("username", "") or f"user{frm.get('id', '')}"
    return name.strip()


# ---------- đọc / ghi bảng công ----------
def read_rows() -> list[dict]:
    p = DATA_FILE
    if not p.exists():
        alt = HERE / "attendance_example.csv"
        if alt.exists():
            print(f"[i] Chưa có {p.name} — dùng {alt.name} để chạy thử.")
            p = alt
        else:
            return []
    with p.open(encoding="utf-8-sig") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()}
                for row in csv.DictReader(f)]


def write_rows(rows: list[dict]):
    with DATA_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        for r in rows:
            w.writerow({h: r.get(h, "") for h in HEADERS})


def find_today_row(rows: list[dict], name: str, day: str):
    for r in rows:
        if r.get("Nhân viên", "") == name and r.get("Ngày", "") == day:
            return r
    return None


def do_checkin(name: str, now: datetime) -> str:
    day, hm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    rows = read_rows()
    row = find_today_row(rows, name, day)
    if row and row.get("Giờ vào"):
        return f"<b>{name}</b> đã check-in lúc {row['Giờ vào']} rồi. Giữ nguyên giờ vào."
    if row:
        row["Giờ vào"] = hm
    else:
        rows.append({"Nhân viên": name, "Ngày": day, "Giờ vào": hm, "Giờ ra": ""})
    write_rows(rows)
    return f"✅ <b>{name}</b> check-in {hm} ngày {day}. Chúc ngày làm việc tốt!"


def do_checkout(name: str, now: datetime) -> str:
    day, hm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    rows = read_rows()
    row = find_today_row(rows, name, day)
    if not row:
        rows.append({"Nhân viên": name, "Ngày": day, "Giờ vào": "", "Giờ ra": hm})
        write_rows(rows)
        return f"⚠️ <b>{name}</b> check-out {hm} nhưng chưa có giờ vào hôm nay. Đã ghi giờ ra."
    row["Giờ ra"] = hm
    write_rows(rows)
    worked = calc_hours(row.get("Giờ vào", ""), hm)
    extra = f" — làm {worked}" if worked else ""
    return f"👋 <b>{name}</b> check-out {hm}{extra}. Hẹn gặp lại!"


def status_today(name: str, now: datetime) -> str:
    day = now.strftime("%Y-%m-%d")
    row = find_today_row(read_rows(), name, day)
    if not row:
        return f"<b>{name}</b> chưa chấm công hôm nay. Gõ /checkin để bắt đầu."
    vao = row.get("Giờ vào", "") or "—"
    ra = row.get("Giờ ra", "") or "—"
    worked = calc_hours(row.get("Giờ vào", ""), row.get("Giờ ra", ""))
    tail = f"\nSố giờ: {worked}" if worked else ""
    return f"<b>{name}</b> — {day}\nVào: {vao}  ·  Ra: {ra}{tail}"


def calc_hours(vao: str, ra: str) -> str:
    try:
        t1 = datetime.strptime(vao, "%H:%M")
        t2 = datetime.strptime(ra, "%H:%M")
    except Exception:
        return ""
    mins = int((t2 - t1).total_seconds() // 60)
    if mins <= 0:
        return ""
    return f"{mins // 60}h{mins % 60:02d}"


# ---------- report ----------
def build_report(day: str) -> str:
    rows = [r for r in read_rows() if r.get("Ngày", "") == day]
    if not rows:
        return f"<b>Bảng công {day}</b>\nChưa có ai chấm công hôm nay."
    rows.sort(key=lambda r: (r.get("Giờ vào", "") or "~", r.get("Nhân viên", "")))
    lines = [f"<b>Bảng công {day}</b> ({len(rows)} người)"]
    done = 0
    for i, r in enumerate(rows, 1):
        vao = r.get("Giờ vào", "") or "—"
        ra = r.get("Giờ ra", "") or "—"
        worked = calc_hours(r.get("Giờ vào", ""), r.get("Giờ ra", ""))
        if worked:
            done += 1
        flag = ""
        if r.get("Giờ vào") and not r.get("Giờ ra"):
            flag = " ⏳ chưa check-out"
        tail = f"  ({worked})" if worked else ""
        lines.append(f"{i}. {r.get('Nhân viên','')}: vào {vao} · ra {ra}{tail}{flag}")
    lines.append(f"\nĐã đủ vào/ra: {done}/{len(rows)}")
    if fl.cfg("AI_SUMMARY", "0") == "1":
        note = ai_note(day, rows)
        if note:
            lines.append(f"\n<i>{note}</i>")
    return "\n".join(lines)


def ai_note(day: str, rows: list[dict]) -> str:
    sample = json.dumps(rows, ensure_ascii=False)
    prompt = (
        "Bạn là trợ lý nhân sự. Dựa trên bảng chấm công JSON hôm nay, viết ĐÚNG một câu "
        "tiếng Việt ngắn gọn nhận xét (ví dụ ai đi muộn, ai chưa check-out, tổng quan chuyên cần). "
        "Không markdown, không xuống dòng. Chỉ trả về câu đó.\n"
        f"Ngày {day}, dữ liệu: {sample}"
    )
    try:
        return fl.ask_ai(prompt).strip().replace("\n", " ")
    except Exception as e:
        print(f"[i] Bỏ qua nhận xét AI: {e}")
        return ""


# ---------- poll ----------
def poll():
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có tin nhắn mới.")
        return
    handled = 0
    for u in updates:
        offset = u["update_id"] + 1
        msg = u.get("message") or u.get("channel_post")
        if not msg:
            continue
        text = (msg.get("text") or "").strip()
        if not text:
            continue
        cmd = text.split()[0].lstrip("/").split("@")[0].lower()
        frm = msg.get("from", {})
        name = sender_name(frm)
        chat_id = msg.get("chat", {}).get("id")
        mid = msg.get("message_id")
        now = datetime.now()
        if cmd == "checkin":
            reply = do_checkin(name, now)
        elif cmd == "checkout":
            reply = do_checkout(name, now)
        elif cmd in ("congtoi", "cong", "status"):
            reply = status_today(name, now)
        else:
            continue  # không phải lệnh chấm công -> im lặng
        tg("sendMessage", chat_id=chat_id, text=reply, parse_mode="HTML",
           reply_to_message_id=mid)
        handled += 1
        print(f"→ /{cmd} · {name}")
    OFFSET_FILE.write_text(str(offset))
    print(f"Xong. Đã xử lý {len(updates)} update, ghi {handled} lượt chấm công.")


# ---------- main ----------
def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    rest = [a for a in args if a != "--dry-run"]
    cmd = rest[0] if rest else ("report" if dry else "poll")
    today = datetime.now().strftime("%Y-%m-%d")

    if cmd == "report":
        report = build_report(today)
        if dry:
            print(report)
        else:
            fl.send_telegram(report)
            print("Đã gửi bảng công vào Telegram.")
    elif cmd == "poll":
        poll()
    else:
        print("Dùng: ./run.sh poll  |  ./run.sh report --dry-run  |  ./run.sh report")


if __name__ == "__main__":
    main()
