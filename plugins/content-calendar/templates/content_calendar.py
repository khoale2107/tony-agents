#!/usr/bin/env python3
"""
Content Calendar — lịch content + nhắc đăng bài.

Đọc calendar.csv (Ngày,Kênh,Chủ đề,Trạng thái). Nhắc bài ĐĂNG HÔM NAY và 3 ngày
tới còn CHƯA ĐĂNG, cảnh báo NGÀY TRỐNG (không có bài nào lên lịch). AI gợi ý cần
làm gì hôm nay + ý tưởng lấp chỗ trống. Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   in ra màn hình (không gửi)
  ./run.sh             gửi nhắc lịch Telegram
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

# Trạng thái coi là ĐÃ XONG -> không cần nhắc đăng
DONE_WORDS = ("đã đăng", "da dang", "xong", "hoàn thành", "hoan thanh",
              "done", "published", "hủy", "huỷ", "huy")


def read_rows() -> list[dict]:
    p = HERE / "calendar.csv"
    if not p.exists():
        p = HERE / "calendar_example.csv"
        print("[i] Chưa có calendar.csv — đang dùng calendar_example.csv để chạy thử.")
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def is_done(status: str) -> bool:
    s = (status or "").strip().lower()
    return any(w in s for w in DONE_WORDS)


def evaluate(rows: list[dict]):
    col_date = fl.cfg("COL_DATE", "Ngày")
    col_channel = fl.cfg("COL_CHANNEL", "Kênh")
    col_topic = fl.cfg("COL_TOPIC", "Chủ đề")
    col_status = fl.cfg("COL_STATUS", "Trạng thái")
    horizon = int(fl.cfg("HORIZON_DAYS", "3"))  # số ngày tới cần soi (mặc định 3)
    today = date.today()
    window = [today + timedelta(days=i) for i in range(horizon + 1)]

    # Gom bài theo ngày (chỉ trong cửa sổ đang soi)
    by_day: dict = {d: [] for d in window}
    pending = []  # bài chưa đăng trong cửa sổ
    for r in rows:
        d = fl.parse_date(r.get(col_date, ""))
        if d is None or d not in by_day:
            continue
        item = {
            "date": d,
            "channel": (r.get(col_channel, "").strip() or "Chưa rõ kênh"),
            "topic": (r.get(col_topic, "").strip() or "(chưa có chủ đề)"),
            "status": (r.get(col_status, "").strip() or "—"),
            "done": is_done(r.get(col_status, "")),
        }
        by_day[d].append(item)
        if not item["done"]:
            pending.append(item)

    # Ngày trống = ngày không có bài nào lên lịch
    empty_days = [d for d in window if not by_day[d]]
    pending.sort(key=lambda x: (x["date"], x["channel"]))
    return window, by_day, pending, empty_days, today


def day_label(d: date, today: date) -> str:
    diff = (d - today).days
    if diff == 0:
        return f"HÔM NAY {d.strftime('%d/%m')}"
    if diff == 1:
        return f"NGÀY MAI {d.strftime('%d/%m')}"
    return f"{d.strftime('%d/%m')} (còn {diff} ngày)"


def build_report(window, by_day, pending, empty_days, today, suggestion: str) -> str:
    brand = fl.cfg("BRAND_NAME", "Kênh của tôi")
    lines = [f"<b>🗓️ LỊCH CONTENT — {brand}</b>",
             f"<i>{today.strftime('%d/%m/%Y')}</i>", ""]

    todays = [x for x in by_day[today] if not x["done"]]
    if todays:
        lines.append("<b>📌 ĐĂNG HÔM NAY:</b>")
        for x in todays:
            lines.append(f"• [{x['channel']}] {x['topic']} — <i>{x['status']}</i>")
    else:
        if by_day[today]:
            lines.append("✅ Hôm nay các bài đã đăng xong.")
        else:
            lines.append("⚠️ Hôm nay CHƯA có bài nào lên lịch!")
    lines.append("")

    upcoming = [x for x in pending if x["date"] != today]
    if upcoming:
        lines.append("<b>⏳ 3 NGÀY TỚI (chưa đăng):</b>")
        for x in upcoming:
            lines.append(f"• {day_label(x['date'], today)} · [{x['channel']}] {x['topic']}")
        lines.append("")

    if empty_days:
        days_txt = ", ".join(day_label(d, today) for d in empty_days)
        lines.append(f"<b>🕳️ NGÀY TRỐNG (cần lên bài):</b> {days_txt}")
        lines.append("")

    if suggestion:
        lines.append("<b>🧠 Gợi ý:</b>")
        lines.append(suggestion)
    return "\n".join(lines)


def main() -> None:
    window, by_day, pending, empty_days, today = evaluate(read_rows())

    detail = []
    for d in window:
        items = by_day[d]
        if items:
            for x in items:
                mark = "ĐÃ ĐĂNG" if x["done"] else "CHƯA ĐĂNG"
                detail.append(f"- {d.strftime('%d/%m')} [{x['channel']}] {x['topic']} ({mark})")
        else:
            detail.append(f"- {d.strftime('%d/%m')} (TRỐNG - chưa có bài)")
    detail_txt = "\n".join(detail)

    prompt = (
        f"Bạn là quản lý content của kênh '{fl.cfg('BRAND_NAME','một thương hiệu')}'. "
        f"Đây là lịch đăng bài hôm nay và 3 ngày tới:\n{detail_txt}\n\n"
        "Hãy viết gợi ý NGẮN GỌN bằng tiếng Việt (tối đa 5 dòng): (1) hôm nay cần "
        "ưu tiên làm/đăng gì, (2) với những NGÀY TRỐNG hãy đề xuất nhanh 1 ý tưởng "
        "chủ đề cụ thể để lấp chỗ. Dứt khoát, thực dụng. Chỉ trả về đoạn gợi ý, "
        "không lặp lại nguyên văn danh sách trên.")
    need_ai = bool(pending or empty_days)
    suggestion = fl.ask_ai(prompt) if need_ai else ""
    report = build_report(window, by_day, pending, empty_days, today, suggestion)

    if "--dry-run" in sys.argv:
        for tag in ("<b>", "</b>", "<i>", "</i>"):
            report = report.replace(tag, "")
        print(report)
        return
    fl.send_telegram(report)
    print(f"Đã gửi nhắc lịch content qua Telegram "
          f"({len(pending)} bài chưa đăng, {len(empty_days)} ngày trống).")


if __name__ == "__main__":
    main()
