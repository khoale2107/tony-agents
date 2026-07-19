#!/usr/bin/env python3
"""
Báo cáo doanh thu tuần — cho ban lãnh đạo.

So doanh thu 7 ngày gần nhất với 7 ngày trước đó, bóc theo ngày, kèm nhận định AI.
Gửi Telegram hoặc in màn hình. (Đặt lịch chạy đầu tuần bằng schedule_*.)

  ./run.sh --dry-run   in ra màn hình
  ./run.sh             gửi Telegram
"""
import sys
from datetime import date, timedelta
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def collect(rows: list[dict]):
    col_date = fl.cfg("COL_DATE", "Ngày")
    col_type = fl.cfg("COL_TYPE", "Loại")
    col_amount = fl.cfg("COL_AMOUNT", "Số tiền")
    today = date.today()
    this_start = today - timedelta(days=6)     # 7 ngày gần nhất
    prev_start = today - timedelta(days=13)
    this_week, prev_week = 0.0, 0.0
    by_day = {this_start + timedelta(days=i): 0.0 for i in range(7)}
    for r in rows:
        d = fl.parse_date(r.get(col_date, ""))
        if not d or "thu" not in r.get(col_type, "").lower():
            continue
        amt = fl.parse_amount(r.get(col_amount, ""))
        if this_start <= d <= today:
            this_week += amt
            by_day[d] = by_day.get(d, 0.0) + amt
        elif prev_start <= d < this_start:
            prev_week += amt
    return this_week, prev_week, by_day


def build_report(this_week, prev_week, by_day, commentary) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    if prev_week:
        change = (this_week - prev_week) / prev_week * 100
        trend = f"{'📈' if change >= 0 else '📉'} {change:+.0f}% so với tuần trước"
    else:
        trend = "(chưa có dữ liệu tuần trước để so)"
    lines = [f"<b>📅 DOANH THU TUẦN — {company}</b>",
             f"<i>7 ngày gần nhất, tính đến {date.today().strftime('%d/%m/%Y')}</i>", "",
             f"💰 Tuần này: <b>{fl.fmt_vnd(this_week)}</b>",
             f"↩️ Tuần trước: {fl.fmt_vnd(prev_week)}",
             f"{trend}", "", "<b>Theo ngày:</b>"]
    for d, v in by_day.items():
        lines.append(f"• {d.strftime('%a %d/%m')}: {fl.fmt_vnd(v)}")
    lines += ["", "<b>🧠 Nhận định:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    this_week, prev_week, by_day = collect(fl.fetch_rows(HERE))
    days_txt = ", ".join(f"{d.strftime('%d/%m')}={fl.fmt_vnd(v)}" for d, v in by_day.items())
    prompt = (f"Bạn là CFO báo cáo cho ban lãnh đạo {fl.cfg('COMPANY_NAME','công ty')}. "
              f"Doanh thu tuần này {fl.fmt_vnd(this_week)}, tuần trước {fl.fmt_vnd(prev_week)}. "
              f"Theo ngày: {days_txt}. "
              "Viết nhận định ngắn (tối đa 4 câu, tiếng Việt): xu hướng, ngày mạnh/yếu bất thường, "
              "1 khuyến nghị cho tuần tới. Không lặp lại số. Chỉ trả về đoạn nhận định.")
    report = build_report(this_week, prev_week, by_day, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo doanh thu tuần qua Telegram.")


if __name__ == "__main__":
    main()
