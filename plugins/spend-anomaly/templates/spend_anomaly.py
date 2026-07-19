#!/usr/bin/env python3
"""
Cảnh báo chi tiêu bất thường — phát hiện khoản chi vượt trung bình & hoá đơn trùng.

- Vượt trung bình: khoản chi > (trung bình cùng hạng mục × hệ số).
- Trùng: cùng hạng mục + cùng số tiền xuất hiện >1 lần (nghi trùng hoá đơn).
Kèm nhận định AI. Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   |   ./run.sh
"""
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def analyze(rows: list[dict]):
    col_date = fl.cfg("COL_DATE", "Ngày")
    col_item = fl.cfg("COL_ITEM", "Hạng mục")
    col_type = fl.cfg("COL_TYPE", "Loại")
    col_amount = fl.cfg("COL_AMOUNT", "Số tiền")
    factor = float(fl.cfg("ANOMALY_FACTOR", "2"))
    today = date.today()

    chi = []
    for r in rows:
        d = fl.parse_date(r.get(col_date, ""))
        if not d or (d.year, d.month) != (today.year, today.month):
            continue
        if "chi" not in r.get(col_type, "").lower():
            continue
        chi.append({"date": d, "item": r.get(col_item, "Khác") or "Khác",
                    "amount": fl.parse_amount(r.get(col_amount, ""))})

    # trung bình theo hạng mục
    by_item = defaultdict(list)
    for c in chi:
        by_item[c["item"]].append(c["amount"])
    avg = {k: (sum(v) / len(v)) for k, v in by_item.items()}

    over = [c for c in chi if avg[c["item"]] > 0 and c["amount"] > avg[c["item"]] * factor]

    # trùng: cùng hạng mục + cùng số tiền, xuất hiện nhiều lần
    seen = defaultdict(int)
    for c in chi:
        seen[(c["item"], round(c["amount"]))] += 1
    dups = [{"item": k[0], "amount": k[1], "count": n} for k, n in seen.items() if n > 1]

    return over, dups, avg


def build_report(over, dups, commentary) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    lines = [f"<b>🚨 CẢNH BÁO CHI TIÊU BẤT THƯỜNG — {company}</b>",
             f"<i>Tháng {date.today().strftime('%m/%Y')}</i>", ""]
    if over:
        lines.append("<b>Vượt trung bình:</b>")
        for c in over:
            lines.append(f"• {c['date'].strftime('%d/%m')} — {c['item']}: {fl.fmt_vnd(c['amount'])}")
    else:
        lines.append("✅ Không có khoản vượt trung bình.")
    lines.append("")
    if dups:
        lines.append("<b>Nghi trùng hoá đơn:</b>")
        for d in dups:
            lines.append(f"• {d['item']}: {fl.fmt_vnd(d['amount'])} × {d['count']} lần")
    else:
        lines.append("✅ Không thấy hoá đơn trùng.")
    lines += ["", "<b>🧠 Nhận định:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    over, dups, _ = analyze(fl.fetch_rows(HERE))
    over_txt = "; ".join(f"{c['item']} {fl.fmt_vnd(c['amount'])}" for c in over) or "không có"
    dup_txt = "; ".join(f"{d['item']} {fl.fmt_vnd(d['amount'])}×{d['count']}" for d in dups) or "không có"
    prompt = (f"Bạn là kiểm soát nội bộ của {fl.cfg('COMPANY_NAME','công ty')}. "
              f"Khoản chi vượt trung bình: {over_txt}. Nghi trùng hoá đơn: {dup_txt}. "
              "Viết nhận định ngắn (tối đa 4 câu, tiếng Việt): mức độ rủi ro, khoản nào nên kiểm tra trước, "
              "1 hành động. Nếu không có gì bất thường thì nói ngắn gọn tình hình ổn. Chỉ trả về đoạn nhận định.")
    report = build_report(over, dups, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi cảnh báo chi tiêu bất thường qua Telegram.")


if __name__ == "__main__":
    main()
