#!/usr/bin/env python3
"""
Order SLA — nhắc khâu/đơn trễ deadline.

Đọc orders.csv (mỗi dòng = 1 khâu của 1 đơn, có cột "Hạn xử lý"). So hạn với hôm
nay: khâu nào ĐÃ TRỄ hoặc SẮP TỚI HẠN mà chưa xong -> gom lại, nêu người phụ
trách. AI viết lời nhắc đốc thúc gọn. Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   in ra màn hình (không gửi)
  ./run.sh             gửi cảnh báo Telegram
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

DONE_WORDS = ("xong", "hoàn thành", "done", "hoàn tất", "đã giao", "đã xong")


def read_rows() -> list[dict]:
    p = HERE / "orders.csv"
    if not p.exists():
        p = HERE / "orders_example.csv"
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def is_done(status: str) -> bool:
    s = (status or "").strip().lower()
    return any(w in s for w in DONE_WORDS)


def evaluate(rows: list[dict]) -> list[dict]:
    col_order = fl.cfg("COL_ORDER", "Mã đơn")
    col_step = fl.cfg("COL_STEP", "Khâu")
    col_owner = fl.cfg("COL_OWNER", "Người phụ trách")
    col_status = fl.cfg("COL_STATUS", "Trạng thái")
    col_due = fl.cfg("COL_DUE", "Hạn xử lý")
    soon_days = int(fl.cfg("SOON_DAYS", "1"))
    today = date.today()

    out = []
    for r in rows:
        if is_done(r.get(col_status, "")):
            continue
        due = fl.parse_date(r.get(col_due, ""))
        if not due:
            continue
        days = (due - today).days  # <0 = đã trễ
        if days < 0:
            status = "LATE"
        elif days <= soon_days:
            status = "SOON"
        else:
            continue
        out.append({
            "order": r.get(col_order, "?") or "?",
            "step": r.get(col_step, "?") or "?",
            "owner": (r.get(col_owner, "") or "Chưa gán").strip() or "Chưa gán",
            "state": (r.get(col_status, "") or "").strip(),
            "due": due,
            "days": days,
            "status": status,
        })
    # trễ nặng nhất lên đầu
    return sorted(out, key=lambda x: x["days"])


ICON = {"LATE": "🔴", "SOON": "🟡"}


def humanize(days: int) -> str:
    if days < 0:
        return f"trễ {abs(days)} ngày"
    if days == 0:
        return "hết hạn hôm nay"
    return f"còn {days} ngày"


def build_report(items: list[dict], commentary: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Xưởng")
    late = [i for i in items if i["status"] == "LATE"]
    soon = [i for i in items if i["status"] == "SOON"]
    lines = [f"<b>⏰ NHẮC SLA — {company}</b>",
             f"<i>{date.today().strftime('%d/%m/%Y')} · trễ {len(late)} · sắp hạn {len(soon)}</i>", ""]
    if not items:
        lines.append("🟢 Không có khâu nào trễ hay sắp tới hạn. Ổn!")
    for it in items:
        lines.append(
            f"{ICON[it['status']]} <b>{it['order']}</b> · {it['step']} — "
            f"{humanize(it['days'])} (hạn {it['due'].strftime('%d/%m')})\n"
            f"   👤 {it['owner']}" + (f" · {it['state']}" if it["state"] else "")
        )
    if items:
        lines += ["", "<b>🧠 Lời nhắc:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    rows = read_rows()
    items = evaluate(rows)

    if items:
        detail = "\n".join(
            f"- Đơn {i['order']}, khâu \"{i['step']}\", phụ trách {i['owner']}: {humanize(i['days'])}"
            + (f" (đang: {i['state']})" if i["state"] else "")
            for i in items)
        prompt = (
            f"Bạn là quản lý sản xuất của {fl.cfg('COMPANY_NAME','xưởng')}. "
            f"Dưới đây là các khâu ĐANG TRỄ hoặc SẮP TỚI HẠN:\n{detail}\n\n"
            "Viết 1 lời nhắc đốc thúc ngắn gọn (tối đa 4 câu, tiếng Việt), giọng khẩn "
            "nhưng lịch sự: nêu khâu/đơn cần ưu tiên xử lý trước, nhắc đúng người phụ "
            "trách, và 1 đề nghị hành động cụ thể. Không lặp lại y nguyên danh sách. "
            "Chỉ trả về đoạn nhắc.")
        commentary = fl.ask_ai(prompt)
    else:
        commentary = ""

    report = build_report(items, commentary)

    if "--dry-run" in sys.argv:
        for tag in ("<b>", "</b>", "<i>", "</i>"):
            report = report.replace(tag, "")
        print(report)
        return
    fl.send_telegram(report)
    print(f"Đã gửi nhắc SLA qua Telegram ({len(items)} khâu cần chú ý).")


if __name__ == "__main__":
    main()
