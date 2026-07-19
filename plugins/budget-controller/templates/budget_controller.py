#!/usr/bin/env python3
"""
Budget Controller — cảnh báo ngân sách theo phòng ban.

So chi phí thực tế trong tháng (theo phòng ban) với ngân sách đặt ra, cảnh báo
phòng nào vượt / sắp vượt, kèm nhận định AI. Gửi Telegram hoặc in ra màn hình.

  ./run.sh --dry-run   in ra màn hình (không gửi)
  ./run.sh             gửi báo cáo Telegram
"""
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def parse_budgets() -> dict:
    out = {}
    for part in fl.cfg("NGAN_SACH", "").split(","):
        if ":" in part:
            name, _, amt = part.partition(":")
            out[name.strip()] = fl.parse_amount(amt)
    return out


def actual_by_dept(rows: list[dict]) -> dict:
    col_date = fl.cfg("COL_DATE", "Ngày")
    col_dept = fl.cfg("COL_DEPT", "Phòng ban")
    col_type = fl.cfg("COL_TYPE", "Loại")
    col_amount = fl.cfg("COL_AMOUNT", "Số tiền")
    today = date.today()
    out = {}
    for r in rows:
        d = fl.parse_date(r.get(col_date, ""))
        if not d or (d.year, d.month) != (today.year, today.month):
            continue
        if "chi" in r.get(col_type, "").lower():
            dept = r.get(col_dept, "Khác") or "Khác"
            out[dept] = out.get(dept, 0.0) + fl.parse_amount(r.get(col_amount, ""))
    return out


def evaluate(budgets: dict, actuals: dict) -> list[dict]:
    warn_at = float(fl.cfg("WARN_PERCENT", "80")) / 100
    rows = []
    for dept, budget in budgets.items():
        act = actuals.get(dept, 0.0)
        pct = (act / budget) if budget else 0.0
        status = "OVER" if pct > 1 else ("WARN" if pct >= warn_at else "OK")
        rows.append({"dept": dept, "budget": budget, "actual": act, "pct": pct, "status": status})
    # phòng có chi nhưng không đặt ngân sách
    for dept, act in actuals.items():
        if dept not in budgets:
            rows.append({"dept": dept, "budget": 0, "actual": act, "pct": 0, "status": "NO_BUDGET"})
    return sorted(rows, key=lambda x: -x["pct"])


ICON = {"OVER": "🔴", "WARN": "🟡", "OK": "🟢", "NO_BUDGET": "⚪"}


def build_report(rows: list[dict], commentary: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    lines = [f"<b>📊 KIỂM SOÁT NGÂN SÁCH — {company}</b>",
             f"<i>Tháng {date.today().strftime('%m/%Y')}</i>", ""]
    for r in rows:
        pct = f"{r['pct']*100:.0f}%" if r["budget"] else "—"
        b = fl.fmt_vnd(r["budget"]) if r["budget"] else "chưa đặt"
        lines.append(f"{ICON[r['status']]} <b>{r['dept']}</b>: {fl.fmt_vnd(r['actual'])} / {b} ({pct})")
    lines += ["", "<b>🧠 Nhận định:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    budgets = parse_budgets()
    rows = fl.fetch_rows(HERE)
    actuals = actual_by_dept(rows)
    evald = evaluate(budgets, actuals)

    over = [r for r in evald if r["status"] in ("OVER", "WARN")]
    detail = "\n".join(
        f"- {r['dept']}: đã chi {fl.fmt_vnd(r['actual'])}"
        + (f" / ngân sách {fl.fmt_vnd(r['budget'])} ({r['pct']*100:.0f}%)" if r["budget"] else " (chưa đặt ngân sách)")
        for r in evald) or "- (không có dữ liệu)"
    prompt = (f"Bạn là kiểm soát viên ngân sách của {fl.cfg('COMPANY_NAME','công ty')}. "
              f"Tình hình chi theo phòng ban tháng này:\n{detail}\n\n"
              "Viết nhận định ngắn (tối đa 4 câu, tiếng Việt): phòng nào đáng lo nhất, "
              "vì sao, và 1 khuyến nghị hành động. Không lặp lại số đã liệt kê. Chỉ trả về đoạn nhận định.")
    commentary = fl.ask_ai(prompt)
    report = build_report(evald, commentary)

    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi cảnh báo ngân sách qua Telegram.")


if __name__ == "__main__":
    main()
