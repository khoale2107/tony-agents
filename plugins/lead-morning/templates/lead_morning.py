#!/usr/bin/env python3
"""
Báo cáo lead sáng — điểm danh khách hàng tiềm năng mỗi sáng.

- Lead mới hôm nay.
- Khách 3+ ngày chưa xử lý (tồn đọng).
- Hẹn đã qua mà chưa tới (nghi no-show).
Kèm gợi ý ưu tiên từ AI. Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   |   ./run.sh
"""
import sys
from datetime import date, timedelta
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

DONE = ("đến", "xong", "hoàn thành", "ký", "chốt", "huỷ", "hủy")     # coi như đã xử lý
PENDING = ("mới", "chưa", "đang")                                     # coi là chưa xử lý


def classify(rows: list[dict]):
    c_name = fl.cfg("COL_NAME", "Tên")
    c_created = fl.cfg("COL_CREATED", "Ngày tạo")
    c_status = fl.cfg("COL_STATUS", "Trạng thái")
    c_appt = fl.cfg("COL_APPT", "Ngày hẹn")
    c_staff = fl.cfg("COL_STAFF", "Nhân viên")
    stale_days = int(fl.cfg("STALE_DAYS", "3"))
    today = date.today()

    new, stale, noshow = [], [], []
    for r in rows:
        name = r.get(c_name, "?")
        staff = r.get(c_staff, "")
        status = r.get(c_status, "").lower()
        created = fl.parse_date(r.get(c_created, ""))
        appt = fl.parse_date(r.get(c_appt, ""))
        tag = f"{name}" + (f" (NV: {staff})" if staff else "")

        if created == today:
            new.append(tag)
        if created and created <= today - timedelta(days=stale_days) and any(p in status for p in PENDING):
            stale.append(f"{tag} — tạo {created.strftime('%d/%m')}, '{r.get(c_status,'')}'")
        if appt and appt < today and not any(dd in status for dd in DONE):
            noshow.append(f"{tag} — hẹn {appt.strftime('%d/%m')} chưa tới")
    return new, stale, noshow


def build_report(new, stale, noshow, tip) -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    def block(title, items):
        if not items:
            return [f"<b>{title}:</b> (không có)"]
        return [f"<b>{title}:</b>"] + [f"• {x}" for x in items]
    lines = [f"<b>☀️ BÁO CÁO LEAD SÁNG — {company}</b>",
             f"<i>{date.today().strftime('%d/%m/%Y')}</i>", ""]
    lines += block(f"🆕 Lead mới ({len(new)})", new) + [""]
    lines += block(f"⏳ Tồn đọng 3+ ngày ({len(stale)})", stale) + [""]
    lines += block(f"📵 Nghi no-show ({len(noshow)})", noshow) + [""]
    lines += ["<b>🧠 Ưu tiên hôm nay:</b>", tip]
    return "\n".join(lines)


def main() -> None:
    new, stale, noshow = classify(fl.fetch_rows(HERE))
    prompt = (f"Bạn là trưởng nhóm sale của {fl.cfg('COMPANY_NAME','công ty')}. Sáng nay có: "
              f"{len(new)} lead mới; {len(stale)} khách tồn đọng 3+ ngày ({'; '.join(stale) or 'không'}); "
              f"{len(noshow)} khách nghi no-show ({'; '.join(noshow) or 'không'}). "
              "Viết 2-3 câu tiếng Việt: nên xử lý ai TRƯỚC và vì sao, giọng đốc thúc nhẹ nhàng. Chỉ trả về nội dung.")
    report = build_report(new, stale, noshow, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo lead sáng qua Telegram.")


if __name__ == "__main__":
    main()
