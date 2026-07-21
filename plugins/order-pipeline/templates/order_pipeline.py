#!/usr/bin/env python3
"""
Order Pipeline — quản lý đơn hàng đa bước.

Theo dõi đơn qua các khâu: NHẬN -> XỬ LÝ -> QC -> TẠO ĐƠN -> XONG.
Đọc orders.csv (Mã đơn,Khách,SĐT,Sản phẩm,Khâu,Người phụ trách,Cập nhật).

  ./run.sh list                  in bảng đơn theo khâu + AI tóm tắt (gửi Telegram)
  ./run.sh list --dry-run        chỉ in ra màn hình, không gửi
  ./run.sh advance DH001         chuyển đơn DH001 sang khâu kế, ghi lại orders.csv + báo Telegram
  ./run.sh advance DH001 --dry-run   xem thử, không ghi file, không gửi

Không cấu hình gì vẫn chạy được: tự đọc orders_example.csv.
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

# Trình tự các khâu
STAGES = ["NHẬN", "XỬ LÝ", "QC", "TẠO ĐƠN", "XONG"]
ICON = {"NHẬN": "📥", "XỬ LÝ": "⚙️", "QC": "🔍", "TẠO ĐƠN": "🧾", "XONG": "✅"}
FIELDS = ["Mã đơn", "Khách", "SĐT", "Sản phẩm", "Khâu", "Người phụ trách", "Cập nhật"]


def data_file() -> Path:
    """File dữ liệu thật (orders.csv) nếu có, ngược lại dùng file mẫu."""
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
    s = (s or "").strip().upper()
    for st in STAGES:
        if st.upper() == s:
            return st
    return STAGES[0]


def next_stage(cur: str):
    cur = norm_stage(cur)
    i = STAGES.index(cur)
    if i >= len(STAGES) - 1:
        return None
    return STAGES[i + 1]


def group_by_stage(rows: list[dict]) -> dict:
    out = {st: [] for st in STAGES}
    for r in rows:
        out[norm_stage(r.get("Khâu", ""))].append(r)
    return out


def build_list_report(rows: list[dict], commentary: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Cửa hàng")
    grouped = group_by_stage(rows)
    active = sum(len(grouped[st]) for st in STAGES if st != "XONG")
    lines = [f"<b>📦 PIPELINE ĐƠN HÀNG — {company}</b>",
             f"<i>{datetime.now():%d/%m/%Y %H:%M} · {active} đơn đang chạy / {len(rows)} tổng</i>", ""]
    for st in STAGES:
        items = grouped[st]
        lines.append(f"{ICON[st]} <b>{st}</b> ({len(items)})")
        if not items:
            lines.append("  <i>— trống —</i>")
        for r in items:
            lines.append(
                f"  • <b>{r.get('Mã đơn','')}</b> · {r.get('Khách','')} · {r.get('Sản phẩm','')}"
                f" — {r.get('Người phụ trách','')}")
        lines.append("")
    lines += ["<b>🧠 Tình hình:</b>", commentary]
    return "\n".join(lines)


def cmd_list(rows: list[dict], dry: bool) -> None:
    grouped = group_by_stage(rows)
    detail_lines = []
    for st in STAGES:
        codes = ", ".join(r.get("Mã đơn", "") for r in grouped[st]) or "(không có)"
        detail_lines.append(f"- {st}: {len(grouped[st])} đơn [{codes}]")
    detail = "\n".join(detail_lines)
    prompt = (
        f"Bạn là điều phối sản xuất của {fl.cfg('COMPANY_NAME','một xưởng')}. "
        f"Số đơn hiện đang nằm ở từng khâu (NHẬN -> XỬ LÝ -> QC -> TẠO ĐƠN -> XONG):\n{detail}\n\n"
        "Viết nhận định ngắn (tối đa 4 câu, tiếng Việt): khâu nào đang nghẽn/ứ đọng, "
        "đơn nào cần đẩy nhanh, và 1 khuyến nghị hành động cho hôm nay. "
        "Không lặp lại toàn bộ danh sách. Chỉ trả về đoạn nhận định.")
    commentary = fl.ask_ai(prompt)
    report = build_list_report(rows, commentary)

    if dry:
        print(_plain(report))
        return
    fl.send_telegram(report)
    print("Đã gửi bảng pipeline qua Telegram.")


def cmd_advance(rows: list[dict], path: Path, code: str, who: str, dry: bool) -> None:
    code_l = code.strip().lower()
    target = None
    for r in rows:
        if r.get("Mã đơn", "").strip().lower() == code_l:
            target = r
            break
    if target is None:
        print(f"Không tìm thấy đơn có mã '{code}'. Kiểm tra lại (xem bằng lệnh list).")
        sys.exit(1)

    cur = norm_stage(target.get("Khâu", ""))
    nxt = next_stage(cur)
    if nxt is None:
        print(f"Đơn {code} đã ở khâu cuối ({cur}) — không thể chuyển tiếp.")
        return

    stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    old_who = target.get("Người phụ trách", "")
    target["Khâu"] = nxt
    target["Cập nhật"] = stamp
    if who:
        target["Người phụ trách"] = who

    msg = (f"<b>➡️ CHUYỂN KHÂU ĐƠN {code}</b>\n"
           f"Khách: {target.get('Khách','')} · {target.get('Sản phẩm','')}\n"
           f"{ICON.get(cur,'')} <b>{cur}</b> → {ICON.get(nxt,'')} <b>{nxt}</b>\n"
           f"Phụ trách: {target.get('Người phụ trách', old_who)}\n"
           f"<i>Lúc {stamp}</i>")

    if dry:
        print(_plain(msg))
        print("\n(--dry-run: KHÔNG ghi file, KHÔNG gửi Telegram)")
        return

    save_orders(path, rows)
    fl.send_telegram(msg)
    print(f"Đơn {code}: {cur} -> {nxt}. Đã ghi {path.name} và báo Telegram.")


def _plain(html: str) -> str:
    for a, b in (("<b>", ""), ("</b>", ""), ("<i>", ""), ("</i>", "")):
        html = html.replace(a, b)
    return html


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry = "--dry-run" in sys.argv
    cmd = args[0].lower() if args else "list"

    path = data_file()
    rows = load_orders(path)

    if cmd == "list":
        cmd_list(rows, dry)
    elif cmd == "advance":
        if len(args) < 2:
            print("Thiếu mã đơn. Dùng: advance <mã> [người phụ trách mới]")
            sys.exit(1)
        code = args[1]
        who = args[2] if len(args) > 2 else ""
        cmd_advance(rows, path, code, who, dry)
    else:
        print(f"Lệnh không hợp lệ: '{cmd}'. Dùng: list | advance <mã>")
        sys.exit(1)


if __name__ == "__main__":
    main()
