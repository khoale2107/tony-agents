#!/usr/bin/env python3
"""
Payroll Calc — tính lương theo sản phẩm / ca / show.

Đọc work.csv (Nhân viên, Loại, Số lượng, Đơn giá). Loại = sản phẩm | ca | show.
Lương mỗi người = tổng (Số lượng × Đơn giá). Cộng tổng quỹ lương. AI tóm tắt.

  ./run.sh --dry-run   in bảng lương ra màn hình (không gửi)
  ./run.sh             gửi bảng lương qua Telegram
"""
from __future__ import annotations

import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def load_work() -> list[dict]:
    """Đọc file chấm công. Fallback về work_example.csv khi chưa có file thật."""
    import csv

    real = HERE / fl.cfg("WORK_FILE", "work.csv")
    path = real if real.exists() else (HERE / "work_example.csv")
    if not path.exists():
        raise SystemExit("Không tìm thấy work.csv hay work_example.csv.")
    if path.name.endswith("_example.csv"):
        print("[i] Chưa có work.csv — đang dùng work_example.csv để chạy thử.")
    raw = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(raw.splitlines())
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def compute(rows: list[dict]) -> list[dict]:
    col_name = fl.cfg("COL_NAME", "Nhân viên")
    col_type = fl.cfg("COL_TYPE", "Loại")
    col_qty = fl.cfg("COL_QTY", "Số lượng")
    col_price = fl.cfg("COL_PRICE", "Đơn giá")

    people: dict = {}
    for r in rows:
        name = (r.get(col_name, "") or "").strip()
        if not name:
            continue
        qty = fl.parse_amount(r.get(col_qty, ""))
        price = fl.parse_amount(r.get(col_price, ""))
        line = qty * price
        loai = (r.get(col_type, "") or "khác").strip().lower()
        p = people.setdefault(name, {"name": name, "total": 0.0, "by_type": {}, "items": []})
        p["total"] += line
        p["by_type"][loai] = p["by_type"].get(loai, 0.0) + line
        p["items"].append({"loai": loai, "qty": qty, "price": price, "line": line})
    return sorted(people.values(), key=lambda x: -x["total"])


def build_report(people: list[dict], summary: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    period = fl.cfg("PERIOD", "")
    total_fund = sum(p["total"] for p in people)

    head = f"<b>💰 BẢNG LƯƠNG — {company}</b>"
    if period:
        head += f"\n<i>Kỳ: {period}</i>"
    lines = [head, ""]
    for i, p in enumerate(people, 1):
        parts = ", ".join(f"{k} {fl.fmt_vnd(v)}" for k, v in p["by_type"].items())
        lines.append(f"{i}. <b>{p['name']}</b>: {fl.fmt_vnd(p['total'])}")
        lines.append(f"   <i>({parts})</i>")
    lines += ["", f"<b>Tổng quỹ lương:</b> {fl.fmt_vnd(total_fund)} — {len(people)} người"]
    lines += ["", "<b>🧠 Tóm tắt:</b>", summary]
    return "\n".join(lines)


def strip_html(text: str) -> str:
    return (text.replace("<b>", "").replace("</b>", "")
                .replace("<i>", "").replace("</i>", ""))


def main() -> None:
    rows = load_work()
    people = compute(rows)
    if not people:
        raise SystemExit("Không có dữ liệu lương để tính.")

    total_fund = sum(p["total"] for p in people)
    detail = "\n".join(
        f"- {p['name']}: {fl.fmt_vnd(p['total'])} "
        + "(" + ", ".join(f"{k}={fl.fmt_vnd(v)}" for k, v in p["by_type"].items()) + ")"
        for p in people)
    prompt = (
        f"Bạn là kế toán lương của {fl.cfg('COMPANY_NAME', 'công ty')}. "
        f"Bảng lương kỳ này (lương = số lượng × đơn giá theo sản phẩm/ca/show):\n{detail}\n"
        f"Tổng quỹ lương: {fl.fmt_vnd(total_fund)}.\n\n"
        "Viết tóm tắt ngắn (tối đa 4 câu, tiếng Việt): ai lương cao nhất/thấp nhất, "
        "cơ cấu lương nghiêng về loại nào (sản phẩm/ca/show), và 1 lưu ý cho chủ. "
        "Không lặp lại toàn bộ số đã liệt kê. Chỉ trả về đoạn tóm tắt.")
    summary = fl.ask_ai(prompt)
    report = build_report(people, summary)

    if "--dry-run" in sys.argv:
        print(strip_html(report))
        return
    fl.send_telegram(report)
    print("Đã gửi bảng lương qua Telegram.")


if __name__ == "__main__":
    main()
