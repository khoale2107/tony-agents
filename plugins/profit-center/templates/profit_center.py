#!/usr/bin/env python3
"""
Profit Center — lãi/lỗ theo chi nhánh / cửa hàng.

Tính doanh thu, chi phí, lợi nhuận cho TỪNG chi nhánh trong tháng, xếp hạng,
kèm nhận định AI (nơi nào khỏe nhất, nơi nào lỗ). Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   in ra màn hình
  ./run.sh             gửi Telegram
"""
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def by_branch(rows: list[dict]) -> dict:
    col_date = fl.cfg("COL_DATE", "Ngày")
    col_branch = fl.cfg("COL_BRANCH", "Chi nhánh")
    col_type = fl.cfg("COL_TYPE", "Loại")
    col_amount = fl.cfg("COL_AMOUNT", "Số tiền")
    today = date.today()
    out = {}
    for r in rows:
        d = fl.parse_date(r.get(col_date, ""))
        if not d or (d.year, d.month) != (today.year, today.month):
            continue
        br = r.get(col_branch, "Khác") or "Khác"
        amt = fl.parse_amount(r.get(col_amount, ""))
        rec = out.setdefault(br, {"revenue": 0.0, "cost": 0.0})
        if "thu" in r.get(col_type, "").lower():
            rec["revenue"] += amt
        elif "chi" in r.get(col_type, "").lower():
            rec["cost"] += amt
    for rec in out.values():
        rec["profit"] = rec["revenue"] - rec["cost"]
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["profit"]))


def build_report(data: dict, commentary: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    lines = [f"<b>🏬 LÃI/LỖ THEO CHI NHÁNH — {company}</b>",
             f"<i>Tháng {date.today().strftime('%m/%Y')}</i>", ""]
    for br, rec in data.items():
        icon = "🟢" if rec["profit"] >= 0 else "🔴"
        lines.append(f"{icon} <b>{br}</b>: lợi nhuận {fl.fmt_vnd(rec['profit'])} "
                     f"(DT {fl.fmt_vnd(rec['revenue'])} · CP {fl.fmt_vnd(rec['cost'])})")
    lines += ["", "<b>🧠 Nhận định:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    data = by_branch(fl.fetch_rows(HERE))
    detail = "\n".join(
        f"- {br}: DT {fl.fmt_vnd(r['revenue'])}, CP {fl.fmt_vnd(r['cost'])}, LN {fl.fmt_vnd(r['profit'])}"
        for br, r in data.items()) or "- (không có dữ liệu)"
    prompt = (f"Bạn là CFO của {fl.cfg('COMPANY_NAME','công ty')} có nhiều chi nhánh. "
              f"Kết quả tháng này:\n{detail}\n\n"
              "Viết nhận định ngắn (tối đa 4 câu, tiếng Việt): chi nhánh nào hiệu quả nhất, "
              "chi nhánh nào cần can thiệp và vì sao, 1 khuyến nghị. Không lặp lại số. Chỉ trả về đoạn nhận định.")
    report = build_report(data, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo lãi/lỗ chi nhánh qua Telegram.")


if __name__ == "__main__":
    main()
