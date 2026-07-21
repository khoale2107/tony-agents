#!/usr/bin/env python3
"""
Dept Handoff — điều phối đơn giữa các bộ phận.

Chuỗi bộ phận: SALES -> SẢN XUẤT -> GIAO.
Đọc orders.csv (cột: Mã đơn,Khách,SĐT,Sản phẩm,Bộ phận,Ghi chú,Cập nhật).

  ./run.sh list                  in bảng đơn theo bộ phận (in ra màn hình)
  ./run.sh handoff DH001         chuyển đơn DH001 sang bộ phận kế: AI soạn thông báo,
                                 gửi Telegram vào chat của bộ phận NHẬN + ghi lại orders.csv
  ./run.sh handoff DH001 --dry-run   xem thử, KHÔNG ghi file, KHÔNG gửi Telegram

Không cấu hình gì vẫn chạy được: tự đọc orders_example.csv và --dry-run.
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

# Trình tự bộ phận (chuỗi bàn giao)
STAGES = ["SALES", "SẢN XUẤT", "GIAO"]
ICON = {"SALES": "💼", "SẢN XUẤT": "🏭", "GIAO": "🚚"}
# Bộ phận -> biến chat id trong .env
CHAT_ENV = {"SALES": "CHAT_SALES", "SẢN XUẤT": "CHAT_SANXUAT", "GIAO": "CHAT_GIAO"}
# Nhãn thân thiện cho AI
LABEL = {"SALES": "Sales / Kinh doanh", "SẢN XUẤT": "Sản xuất", "GIAO": "Giao hàng"}
FIELDS = ["Mã đơn", "Khách", "SĐT", "Sản phẩm", "Bộ phận", "Ghi chú", "Cập nhật"]

# Bí danh không dấu -> tên chuẩn
ALIAS = {
    "SALES": "SALES", "KINH DOANH": "SALES",
    "SAN XUAT": "SẢN XUẤT", "SẢN XUẤT": "SẢN XUẤT", "SX": "SẢN XUẤT",
    "GIAO": "GIAO", "GIAO HANG": "GIAO", "GIAO HÀNG": "GIAO",
}


def tg(method: str, **params):
    """Gọi Bot API bằng urllib (gửi vào chat id chỉ định)."""
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


def send_to(chat_id: str, text: str) -> None:
    res = tg("sendMessage", chat_id=chat_id, text=text,
             parse_mode="HTML", disable_web_page_preview="true")
    if not res.get("ok"):
        raise SystemExit(f"Telegram lỗi: {res}")


def data_file() -> Path:
    real = HERE / fl.cfg("ORDERS_FILE", "orders.csv")
    if real.exists():
        return real
    return HERE / "orders_example.csv"


def load_orders(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save_orders(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def norm_stage(s: str) -> str:
    key = (s or "").strip().upper()
    return ALIAS.get(key, STAGES[0])


def next_stage(cur: str):
    cur = norm_stage(cur)
    i = STAGES.index(cur)
    if i >= len(STAGES) - 1:
        return None
    return STAGES[i + 1]


def group_by_stage(rows: list[dict]) -> dict:
    out = {st: [] for st in STAGES}
    for r in rows:
        out[norm_stage(r.get("Bộ phận", ""))].append(r)
    return out


def _plain(html: str) -> str:
    for a, b in (("<b>", ""), ("</b>", ""), ("<i>", ""), ("</i>", "")):
        html = html.replace(a, b)
    return html


def cmd_list(rows: list[dict]) -> None:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    grouped = group_by_stage(rows)
    done = len(grouped["GIAO"])
    lines = [f"<b>🔀 ĐIỀU PHỐI BỘ PHẬN — {company}</b>",
             f"<i>{datetime.now():%d/%m/%Y %H:%M} · {len(rows)} đơn · {done} ở khâu giao</i>", ""]
    for st in STAGES:
        items = grouped[st]
        lines.append(f"{ICON[st]} <b>{st}</b> ({len(items)})")
        if not items:
            lines.append("  <i>— trống —</i>")
        for r in items:
            lines.append(f"  • <b>{r.get('Mã đơn','')}</b> · {r.get('Khách','')} · {r.get('Sản phẩm','')}")
        lines.append("")
    print(_plain("\n".join(lines)))


def compose_message(order: dict, frm: str, to: str) -> str:
    """AI soạn thông báo bàn giao cho bộ phận nhận."""
    prompt = (
        f"Bạn là điều phối viên của {fl.cfg('COMPANY_NAME','một công ty')}. "
        f"Một đơn hàng vừa được bộ phận {LABEL[frm]} bàn giao sang bộ phận {LABEL[to]}.\n"
        f"Thông tin đơn:\n"
        f"- Mã đơn: {order.get('Mã đơn','')}\n"
        f"- Khách: {order.get('Khách','')} ({order.get('SĐT','')})\n"
        f"- Sản phẩm: {order.get('Sản phẩm','')}\n"
        f"- Ghi chú: {order.get('Ghi chú','') or '(không có)'}\n\n"
        f"Viết một thông báo ngắn (tối đa 3 câu, tiếng Việt, giọng đồng nghiệp) gửi cho bộ phận "
        f"{LABEL[to]}: nói rõ họ cần làm gì tiếp theo với đơn này và điểm cần lưu ý. "
        f"Không chào hỏi dài dòng, không lặp lại toàn bộ thông tin đã có. Chỉ trả về đoạn thông báo.")
    return fl.ask_ai(prompt).strip()


def cmd_handoff(rows: list[dict], path: Path, code: str, dry: bool) -> None:
    code_l = code.strip().lower()
    target = None
    for r in rows:
        if r.get("Mã đơn", "").strip().lower() == code_l:
            target = r
            break
    if target is None:
        print(f"Không tìm thấy đơn có mã '{code}'. Xem danh sách bằng lệnh: list")
        sys.exit(1)

    cur = norm_stage(target.get("Bộ phận", ""))
    nxt = next_stage(cur)
    if nxt is None:
        print(f"Đơn {code} đã ở bộ phận cuối ({cur}) — không thể bàn giao tiếp.")
        return

    stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    ai_note = compose_message(target, cur, nxt)

    header = (f"<b>{ICON.get(nxt,'')} ĐƠN MỚI CHUYỂN TỚI — {nxt}</b>\n"
              f"Mã: <b>{target.get('Mã đơn','')}</b> · {target.get('Khách','')} ({target.get('SĐT','')})\n"
              f"Sản phẩm: {target.get('Sản phẩm','')}\n"
              f"Từ bộ phận: {ICON.get(cur,'')} {cur}\n")
    ghi_chu = target.get("Ghi chú", "")
    if ghi_chu:
        header += f"Ghi chú: {ghi_chu}\n"
    msg = header + f"\n{ai_note}\n<i>Bàn giao lúc {stamp}</i>"

    chat_var = CHAT_ENV[nxt]
    chat_id = fl.cfg(chat_var)

    if dry:
        print(f"[--dry-run] Sẽ gửi vào chat của bộ phận {nxt} (biến {chat_var}"
              + (f" = {chat_id}" if chat_id else " CHƯA điền") + "):\n")
        print(_plain(msg))
        print("\n(--dry-run: KHÔNG ghi file, KHÔNG gửi Telegram)")
        return

    if not chat_id:
        print(f"Chưa điền {chat_var} trong .env — không biết gửi vào đâu cho bộ phận {nxt}.")
        sys.exit(1)

    # Ghi lại trạng thái đơn
    target["Bộ phận"] = nxt
    target["Cập nhật"] = stamp
    save_orders(path, rows)

    send_to(chat_id, msg)
    print(f"Đơn {code}: {cur} -> {nxt}. Đã báo bộ phận {nxt} qua Telegram và ghi {path.name}.")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry = "--dry-run" in sys.argv
    cmd = args[0].lower() if args else "list"

    path = data_file()
    rows = load_orders(path)

    if cmd == "list":
        cmd_list(rows)
    elif cmd == "handoff":
        if len(args) < 2:
            print("Thiếu mã đơn. Dùng: handoff <mã>")
            sys.exit(1)
        cmd_handoff(rows, path, args[1], dry)
    else:
        print(f"Lệnh không hợp lệ: '{cmd}'. Dùng: list | handoff <mã>")
        sys.exit(1)


if __name__ == "__main__":
    main()
