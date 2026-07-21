#!/usr/bin/env python3
"""
Task Reminder — nhắc việc theo checklist.

Đọc tasks.csv (Việc,Người,Hạn,Trạng thái,Loại). Lọc việc TỚI HẠN HÔM NAY, QUÁ
HẠN hoặc CHƯA XONG; AI sắp thứ tự ưu tiên và viết lời nhắc gọn cho cả nhóm.
Dùng cho onboarding, deadline dự án, lịch trực. Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   in ra màn hình (không gửi)
  ./run.sh             gửi lời nhắc Telegram
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

DONE_WORDS = ("xong", "hoàn thành", "done", "hoàn tất", "đã xong", "hủy", "huỷ")


def read_rows() -> list[dict]:
    p = HERE / "tasks.csv"
    if not p.exists():
        p = HERE / "tasks_example.csv"
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def is_done(status: str) -> bool:
    s = (status or "").strip().lower()
    return any(w in s for w in DONE_WORDS)


def evaluate(rows: list[dict]) -> list[dict]:
    col_task = fl.cfg("COL_TASK", "Việc")
    col_owner = fl.cfg("COL_OWNER", "Người")
    col_due = fl.cfg("COL_DUE", "Hạn")
    col_status = fl.cfg("COL_STATUS", "Trạng thái")
    col_type = fl.cfg("COL_TYPE", "Loại")
    soon_days = int(fl.cfg("SOON_DAYS", "0"))  # 0 = chỉ hôm nay; 1 = thêm ngày mai
    today = date.today()

    out = []
    for r in rows:
        if is_done(r.get(col_status, "")):
            continue
        due = fl.parse_date(r.get(col_due, ""))
        # Không có hạn -> coi là việc treo (chưa xong), vẫn nhắc
        if due is None:
            bucket = "OPEN"
            days = 9999
        else:
            days = (due - today).days  # <0 = quá hạn
            if days < 0:
                bucket = "LATE"
            elif days <= soon_days:
                bucket = "TODAY"
            else:
                continue  # còn xa hạn, chưa nhắc
        out.append({
            "task": r.get(col_task, "").strip(),
            "owner": (r.get(col_owner, "").strip() or "Chưa gán"),
            "due": due,
            "days": days,
            "type": (r.get(col_type, "").strip() or "Khác"),
            "status": (r.get(col_status, "").strip() or "—"),
            "bucket": bucket,
        })
    # Quá hạn nặng nhất trước, rồi tới hạn, rồi việc treo
    order = {"LATE": 0, "TODAY": 1, "OPEN": 2}
    return sorted(out, key=lambda x: (order[x["bucket"]], x["days"]))


ICON = {"LATE": "🔴", "TODAY": "🟠", "OPEN": "⚪"}
LABEL = {"LATE": "QUÁ HẠN", "TODAY": "ĐẾN HẠN", "OPEN": "CHƯA CÓ HẠN"}


def due_text(t: dict) -> str:
    if t["due"] is None:
        return "chưa đặt hạn"
    if t["bucket"] == "LATE":
        return f"trễ {abs(t['days'])} ngày (hạn {t['due'].strftime('%d/%m')})"
    if t["days"] == 0:
        return "hạn HÔM NAY"
    return f"còn {t['days']} ngày (hạn {t['due'].strftime('%d/%m')})"


def build_report(rows: list[dict], commentary: str) -> str:
    team = fl.cfg("TEAM_NAME", "Nhóm")
    lines = [f"<b>✅ NHẮC VIỆC — {team}</b>",
             f"<i>{date.today().strftime('%d/%m/%Y')}</i>", ""]
    if not rows:
        lines.append("🎉 Không có việc quá hạn / đến hạn. Cả nhóm ổn!")
        return "\n".join(lines)
    for t in rows:
        lines.append(
            f"{ICON[t['bucket']]} <b>{t['task']}</b> — {t['owner']} "
            f"[{t['type']}] · {due_text(t)}")
    lines += ["", "<b>🧠 Ưu tiên hôm nay:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    rows = evaluate(read_rows())

    detail = "\n".join(
        f"- [{LABEL[t['bucket']]}] {t['task']} | phụ trách: {t['owner']} | "
        f"loại: {t['type']} | {due_text(t)}"
        for t in rows) or "- (không có việc cần nhắc)"
    prompt = (
        f"Bạn là trưởng nhóm của {fl.cfg('TEAM_NAME','nhóm')}. Danh sách việc cần "
        f"xử lý hôm nay:\n{detail}\n\n"
        "Hãy sắp xếp THỨ TỰ ƯU TIÊN xử lý (việc nào làm trước) và viết lời nhắc "
        "ngắn gọn, dứt khoát bằng tiếng Việt (tối đa 5 dòng). Nêu rõ ai cần làm "
        "gì trước. Ưu tiên việc quá hạn và onboarding/lịch trực gấp. "
        "Chỉ trả về đoạn nhắc việc, không lặp lại nguyên văn danh sách trên.")
    commentary = fl.ask_ai(prompt) if rows else ""
    report = build_report(rows, commentary)

    if "--dry-run" in sys.argv:
        for tag in ("<b>", "</b>", "<i>", "</i>"):
            report = report.replace(tag, "")
        print(report)
        return
    fl.send_telegram(report)
    print(f"Đã gửi nhắc việc qua Telegram ({len(rows)} việc).")


if __name__ == "__main__":
    main()
