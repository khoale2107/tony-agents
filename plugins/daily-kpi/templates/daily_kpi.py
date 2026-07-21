"""
KPI hàng ngày từng nhân viên.

Đọc kpi.csv (Nhân viên, Chỉ tiêu, Thực đạt). Tính % đạt mỗi người, xếp hạng,
AI nhận định ai vượt / ai hụt cần hỗ trợ. Gửi Telegram hoặc in màn hình.
Chưa có kpi.csv thật thì tự dùng kpi_example.csv để chạy thử.

  python3 daily_kpi.py --dry-run   in ra màn hình
  python3 daily_kpi.py             gửi Telegram
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_rows() -> list[dict]:
    """Đọc kpi.csv; chưa có thì fallback kpi_example.csv."""
    real = HERE / fl.cfg("KPI_FILE", "kpi.csv")
    path = real if real.exists() else (HERE / "kpi_example.csv")
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def compute(rows: list[dict]) -> list[dict]:
    col_name = fl.cfg("COL_NAME", "Nhân viên")
    col_target = fl.cfg("COL_TARGET", "Chỉ tiêu")
    col_actual = fl.cfg("COL_ACTUAL", "Thực đạt")
    out = []
    for r in rows:
        name = (r.get(col_name) or "").strip()
        if not name:
            continue
        target = fl.parse_amount(r.get(col_target, ""))
        actual = fl.parse_amount(r.get(col_actual, ""))
        pct = (actual / target * 100) if target else 0.0
        out.append({"name": name, "target": target, "actual": actual, "pct": pct})
    out.sort(key=lambda x: x["pct"], reverse=True)
    return out


def badge(pct: float) -> str:
    if pct >= 100:
        return "✅"
    if pct >= 80:
        return "🟡"
    return "🔴"


def build_report(people: list[dict], commentary: str) -> str:
    team = fl.cfg("TEAM_NAME", "Đội")
    tot_target = sum(p["target"] for p in people)
    tot_actual = sum(p["actual"] for p in people)
    tot_pct = (tot_actual / tot_target * 100) if tot_target else 0.0
    lines = [
        f"<b>📊 KPI NGÀY — {team}</b>",
        f"<i>{date.today().strftime('%d/%m/%Y')}</i>",
        "",
        f"Toàn đội: <b>{tot_pct:.0f}%</b> "
        f"({fl.fmt_vnd(tot_actual)} / {fl.fmt_vnd(tot_target)})",
        "",
        "<b>Bảng xếp hạng:</b>",
    ]
    for i, p in enumerate(people, 1):
        lines.append(
            f"{i}. {badge(p['pct'])} <b>{p['name']}</b> — {p['pct']:.0f}% "
            f"({fl.fmt_vnd(p['actual'])}/{fl.fmt_vnd(p['target'])})"
        )
    lines += ["", "<b>🧠 Nhận định:</b>", commentary]
    return "\n".join(lines)


def strip_html(text: str) -> str:
    for tag in ("<b>", "</b>", "<i>", "</i>"):
        text = text.replace(tag, "")
    return text


def main() -> None:
    people = compute(read_rows())
    if not people:
        print("Không có dữ liệu KPI để xử lý.")
        return
    rows_txt = "; ".join(
        f"{p['name']}={p['pct']:.0f}% ({fl.fmt_vnd(p['actual'])}/{fl.fmt_vnd(p['target'])})"
        for p in people
    )
    prompt = (
        f"Bạn là trưởng nhóm sales của {fl.cfg('TEAM_NAME', 'đội')}. "
        f"KPI ngày hôm nay từng nhân viên (% đạt = thực đạt/chỉ tiêu): {rows_txt}. "
        "Viết nhận định ngắn (tối đa 4 câu, tiếng Việt): nêu tên ai vượt chỉ tiêu để khen, "
        "ai đang hụt cần hỗ trợ ngay, và 1 hành động cụ thể cho hôm nay. "
        "Không liệt kê lại toàn bộ số. Chỉ trả về đoạn nhận định."
    )
    report = build_report(people, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(strip_html(report))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo KPI ngày qua Telegram.")


if __name__ == "__main__":
    main()
