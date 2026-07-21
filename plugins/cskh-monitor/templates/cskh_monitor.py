#!/usr/bin/env python3
"""
Giám sát nhân viên tư vấn — chấm điểm phản hồi CHẬM và khách bị BỎ SÓT.

Đọc log chat (cột: Thời điểm khách nhắn | Thời điểm NV trả lời | Nhân viên | Khách | Trạng thái).
- Phản hồi chậm: trả lời sau > SLA_MINUTES phút.
- Bỏ sót: chưa có thời điểm trả lời (Trạng thái chưa 'đã trả lời').
Kèm nhận định AI. Gửi Telegram hoặc in màn hình (--dry-run).

  ./run.sh --dry-run   |   ./run.sh
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def parse_dt(text):
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%H:%M %d/%m/%Y"):
        try:
            return datetime.strptime(str(text).strip(), fmt)
        except (ValueError, TypeError):
            continue
    return None


def analyze(rows: list[dict]):
    c_in = fl.cfg("COL_IN", "Thời điểm khách nhắn")
    c_out = fl.cfg("COL_OUT", "Thời điểm NV trả lời")
    c_staff = fl.cfg("COL_STAFF", "Nhân viên")
    c_cust = fl.cfg("COL_CUST", "Khách")
    sla = int(fl.cfg("SLA_MINUTES", "15"))

    slow, missed = [], []
    per_staff: dict[str, list[float]] = {}
    for r in rows:
        staff = r.get(c_staff, "?") or "?"
        cust = r.get(c_cust, "?")
        t_in = parse_dt(r.get(c_in, ""))
        t_out = parse_dt(r.get(c_out, ""))
        if not t_out:
            missed.append(f"{cust} — NV {staff} chưa trả lời")
            continue
        if t_in:
            mins = (t_out - t_in).total_seconds() / 60.0
            per_staff.setdefault(staff, []).append(mins)
            if mins > sla:
                slow.append(f"{cust} — NV {staff} trả lời sau {mins:.0f} phút")
    return slow, missed, per_staff, sla


def build_report(slow, missed, per_staff, sla, note) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    lines = [f"<b>🕵️ GIÁM SÁT TƯ VẤN — {company}</b>",
             f"<i>{datetime.now().strftime('%d/%m/%Y %H:%M')} · SLA {sla} phút</i>", ""]
    lines.append(f"<b>🐌 Trả lời chậm ({len(slow)}):</b>")
    lines += [f"• {x}" for x in slow] or ["• (không)"]
    lines.append("")
    lines.append(f"<b>📭 Bỏ sót ({len(missed)}):</b>")
    lines += [f"• {x}" for x in missed] or ["• (không)"]
    lines.append("")
    lines.append("<b>⏱ Thời gian phản hồi TB theo NV:</b>")
    if per_staff:
        for s, arr in sorted(per_staff.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
            lines.append(f"• {s}: {sum(arr)/len(arr):.0f} phút ({len(arr)} lượt)")
    else:
        lines.append("• (không có dữ liệu)")
    lines += ["", "<b>🧠 Nhận định:</b>", note]
    return "\n".join(lines)


def main() -> None:
    slow, missed, per_staff, sla = analyze(fl.fetch_rows(HERE))
    avg_txt = "; ".join(f"{s} {sum(a)/len(a):.0f}p" for s, a in per_staff.items()) or "không có"
    prompt = (f"Bạn là quản lý CSKH của {fl.cfg('COMPANY_NAME','công ty')}. Hôm nay có "
              f"{len(slow)} lượt trả lời chậm (>{sla} phút), {len(missed)} khách bị bỏ sót. "
              f"Thời gian phản hồi TB mỗi NV: {avg_txt}. "
              "Viết 2-3 câu tiếng Việt: khen/nhắc nhở nhân viên nào, hành động cần làm ngay. Chỉ trả về nội dung.")
    report = build_report(slow, missed, per_staff, sla, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo giám sát tư vấn qua Telegram.")


if __name__ == "__main__":
    main()
