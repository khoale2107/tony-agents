#!/usr/bin/env python3
"""
Bot lệnh trong group Telegram — nhân viên gõ keyword, bot đọc file dữ liệu
và trả lời ngay trong nhóm.

  ./run.sh --dry-run /donmoi   mô phỏng 1 lệnh, in kết quả ra màn hình (không gửi Telegram)
  ./run.sh --dry-run /tonkho   thử lệnh khác
  ./run.sh poll                đọc getUpdates, khớp keyword, trả lời trong group
  ./run.sh help                liệt kê các lệnh đang cấu hình

Map keyword -> hành động khai báo trong .env, ví dụ:
  CMD_donmoi=orders.csv | filter:TrangThai=Mới | title:Đơn mới
  CMD_tonkho=stock.csv  | lowstock:1 | title:Tồn kho hiện tại
File thật (orders.csv/stock.csv) chưa có thì tự đọc <ten>_example.csv để chạy thử.
Dùng GÓI Claude Code (fl.ask_ai) khi lệnh bật cờ ai:1 để diễn đạt tự nhiên.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")
OFFSET_FILE = HERE / ".tg_offset"

# Lệnh mặc định để chạy thử ngay khi .env chưa khai báo CMD_*
DEFAULT_COMMANDS = {
    "donmoi": "orders.csv | filter:TrangThai=Mới | title:Đơn mới",
    "tonkho": "stock.csv | lowstock:1 | title:Tồn kho hiện tại",
}


# ---------- Telegram helper ----------
def tg(method: str, **params):
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


# ---------- đọc cấu hình lệnh ----------
def norm_kw(kw: str) -> str:
    return kw.strip().lstrip("/").lower()


def load_commands() -> dict:
    cmds = {}
    for k, v in os.environ.items():
        if k.startswith("CMD_") and v.strip():
            cmds[norm_kw(k[4:])] = v.strip()
    if not cmds:
        print("[i] Chưa khai báo CMD_* trong .env — đang dùng lệnh mặc định để chạy thử.")
        cmds = dict(DEFAULT_COMMANDS)
    return cmds


def parse_spec(spec: str) -> dict:
    parts = [p.strip() for p in spec.split("|") if p.strip()]
    out = {"file": parts[0] if parts else "", "filters": [], "cols": None,
           "title": "", "ai": False, "lowstock": False}
    for p in parts[1:]:
        key, _, val = p.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "filter" and "=" in val:
            col, _, want = val.partition("=")
            out["filters"].append((col.strip(), want.strip()))
        elif key == "title":
            out["title"] = val
        elif key == "cols":
            out["cols"] = [c.strip() for c in val.split(",") if c.strip()]
        elif key == "ai":
            out["ai"] = val in ("1", "true", "on", "yes")
        elif key == "lowstock":
            out["lowstock"] = val in ("1", "true", "on", "yes")
    return out


# ---------- đọc dữ liệu ----------
def read_data(filename: str) -> list[dict]:
    p = HERE / filename
    if not p.exists():
        stem = Path(filename).stem
        alt = HERE / f"{stem}_example{Path(filename).suffix}"
        if alt.exists():
            print(f"[i] Chưa có {filename} — dùng {alt.name} để chạy thử.")
            p = alt
        else:
            raise SystemExit(f"Không tìm thấy {filename} (cũng không có {alt.name}).")
    with p.open(encoding="utf-8-sig") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()}
                for row in csv.DictReader(f)]


def _to_int(x: str):
    try:
        return int(fl.parse_amount(x))
    except Exception:
        return None


def apply_filters(rows: list[dict], filters: list) -> list[dict]:
    out = rows
    for col, want in filters:
        w = want.lower()
        out = [r for r in out if w in (r.get(col, "") or "").lower()]
    return out


# ---------- dựng câu trả lời ----------
def format_rows(rows: list[dict], spec: dict) -> str:
    title = spec.get("title") or "Kết quả"
    if not rows:
        return f"<b>{title}</b>\nKhông có dòng nào khớp."
    lines = [f"<b>{title}</b> ({len(rows)} dòng)"]
    cols = spec["cols"]
    for i, r in enumerate(rows, 1):
        keys = cols if cols else list(r.keys())
        flag = ""
        if spec["lowstock"]:
            sl, ng = _to_int(r.get("SoLuong", "")), _to_int(r.get("Nguong", ""))
            if sl is not None and ng is not None and sl < ng:
                flag = " ⚠️ dưới ngưỡng"
        body = " · ".join(f"{k}: {r.get(k,'')}" for k in keys if r.get(k, ""))
        lines.append(f"{i}. {body}{flag}")
    return "\n".join(lines)


def ai_phrasing(rows: list[dict], spec: dict) -> str:
    title = spec.get("title") or "Kết quả"
    if not rows:
        return f"<b>{title}</b>\nHiện chưa có dữ liệu phù hợp."
    sample = json.dumps(rows[:20], ensure_ascii=False)
    prompt = (f"Bạn là trợ lý trong group nội bộ. Dựa trên dữ liệu JSON sau ({title}), "
              f"viết một tin nhắn tiếng Việt ngắn gọn, tự nhiên, có gạch đầu dòng, "
              f"nêu bật thông tin quan trọng. Dùng thẻ HTML <b> cho tiêu đề, không dùng markdown. "
              f"Chỉ trả về nội dung tin nhắn.\nDữ liệu: {sample}")
    return fl.ask_ai(prompt).strip()


def run_command(keyword: str, cmds: dict) -> str:
    spec = parse_spec(cmds[keyword])
    rows = apply_filters(read_data(spec["file"]), spec["filters"])
    return ai_phrasing(rows, spec) if spec["ai"] else format_rows(rows, spec)


def help_text(cmds: dict) -> str:
    lines = ["<b>Các lệnh của bot:</b>"]
    for kw, spec in cmds.items():
        title = parse_spec(spec).get("title") or ""
        lines.append(f"/{kw} — {title}".rstrip(" —"))
    return "\n".join(lines)


# ---------- chế độ ----------
def dry_run(keyword: str):
    cmds = load_commands()
    kw = norm_kw(keyword)
    if kw in ("help", "lenh", "menu"):
        print(help_text(cmds))
        return
    if kw not in cmds:
        print(f"Không có lệnh '/{kw}'. Lệnh khả dụng: " +
              ", ".join(f"/{k}" for k in cmds) + " (hoặc /help)")
        return
    print(f"[dry-run] /{kw}\n" + "-" * 40)
    print(run_command(kw, cmds))


def poll():
    cmds = load_commands()
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có tin nhắn mới.")
        return
    answered = 0
    for u in updates:
        offset = u["update_id"] + 1
        msg = u.get("message") or u.get("channel_post")
        if not msg:
            continue
        text = (msg.get("text") or "").strip()
        if not text:
            continue
        kw = norm_kw(text.split()[0])
        chat_id = msg.get("chat", {}).get("id")
        mid = msg.get("message_id")
        if kw in ("help", "lenh", "menu"):
            tg("sendMessage", chat_id=chat_id, text=help_text(cmds),
               parse_mode="HTML", reply_to_message_id=mid)
            answered += 1
            continue
        if kw not in cmds:
            continue  # không phải lệnh của bot -> im lặng
        try:
            reply = run_command(kw, cmds)
        except SystemExit as e:
            reply = f"⚠️ {e}"
        tg("sendMessage", chat_id=chat_id, text=reply, parse_mode="HTML",
           reply_to_message_id=mid, disable_web_page_preview="true")
        answered += 1
        print(f"→ Đã trả lời /{kw} trong chat {chat_id}")
    OFFSET_FILE.write_text(str(offset))
    print(f"Xong. Đã xử lý {len(updates)} update, trả lời {answered} lệnh.")


def main():
    args = sys.argv[1:]
    if "--dry-run" in args:
        rest = [a for a in args if a != "--dry-run"]
        keyword = rest[0] if rest else "help"
        dry_run(keyword)
        return
    cmd = args[0] if args else "poll"
    if cmd == "poll":
        poll()
    elif cmd == "help":
        print(help_text(load_commands()))
    else:
        print("Dùng: ./run.sh poll  |  ./run.sh --dry-run /donmoi  |  ./run.sh help")


if __name__ == "__main__":
    main()
