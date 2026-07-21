#!/usr/bin/env python3
"""
Bot thu báo cáo cuối ngày — tổng hợp gửi sếp ~21h.

Đọc reports.csv (Nhân viên,Phòng,Nội dung báo cáo). AI gom lại thành bản
gọn cho sếp: điểm chính từng phòng + việc tồn / rủi ro cần lưu ý.
Gửi Telegram cho sếp, hoặc in màn hình với --dry-run.

  python3 eod_collector.py --dry-run   in ra màn hình
  python3 eod_collector.py             gửi Telegram sếp
"""
from __future__ import annotations

import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_reports() -> list[dict]:
    """Đọc báo cáo: file thật REPORTS_FILE, chưa có thì dùng reports_example.csv."""
    import csv

    name = fl.cfg("REPORTS_FILE", "reports.csv")
    path = HERE / name
    if not path.exists():
        path = HERE / "reports_example.csv"
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def group_by_dept(rows: list[dict]) -> "OrderedDict[str, list[dict]]":
    col_staff = fl.cfg("COL_STAFF", "Nhân viên")
    col_dept = fl.cfg("COL_DEPT", "Phòng")
    col_content = fl.cfg("COL_CONTENT", "Nội dung báo cáo")
    depts: "OrderedDict[str, list[dict]]" = OrderedDict()
    for r in rows:
        dept = (r.get(col_dept, "") or "Khác").strip()
        depts.setdefault(dept, []).append({
            "staff": (r.get(col_staff, "") or "").strip(),
            "content": (r.get(col_content, "") or "").strip(),
        })
    return depts


def build_prompt(depts: "OrderedDict[str, list[dict]]") -> str:
    blocks = []
    for dept, items in depts.items():
        lines = [f"# Phòng {dept}"]
        for it in items:
            who = it["staff"] or "(khuyết danh)"
            lines.append(f"- {who}: {it['content']}")
        blocks.append("\n".join(lines))
    raw = "\n\n".join(blocks)
    company = fl.cfg("COMPANY_NAME", "công ty")
    return (
        f"Bạn là trợ lý tổng hợp báo cáo cuối ngày cho sếp {company}. "
        "Dưới đây là báo cáo thô của từng nhân viên, nhóm theo phòng:\n\n"
        f"{raw}\n\n"
        "Hãy tổng hợp thành bản báo cáo GỌN cho sếp đọc trong 1 phút. Yêu cầu:\n"
        "- Với MỖI phòng: 1-3 gạch đầu dòng nêu điểm chính đã làm được hôm nay.\n"
        "- Sau đó 1 mục 'VIỆC TỒN / RỦI RO': liệt kê việc chưa xong, vướng mắc, "
        "rủi ro cần sếp lưu ý (nếu không có thì ghi 'Không có').\n"
        "- Viết tiếng Việt, súc tích, không lặp lại nguyên văn, không thêm lời chào.\n"
        "- KHÔNG dùng dấu sao markdown (*, **). Mỗi phòng bắt đầu bằng dòng 'PHÒNG <tên>:'."
    )


def build_report(summary: str, depts: "OrderedDict[str, list[dict]]") -> str:
    company = fl.cfg("COMPANY_NAME", "Công ty")
    n_staff = sum(len(v) for v in depts.values())
    today = date.today().strftime("%d/%m/%Y")
    head = [
        f"<b>🌙 BÁO CÁO CUỐI NGÀY — {company}</b>",
        f"<i>{today} · {len(depts)} phòng · {n_staff} báo cáo</i>",
        "",
    ]
    return "\n".join(head) + summary.strip()


def to_plain(html: str) -> str:
    for tag in ("<b>", "</b>", "<i>", "</i>"):
        html = html.replace(tag, "")
    return html


def main() -> None:
    rows = read_reports()
    depts = group_by_dept(rows)
    if not depts:
        print("Chưa có báo cáo nào để tổng hợp.")
        return
    summary = fl.ask_ai(build_prompt(depts))
    report = build_report(summary, depts)
    if "--dry-run" in sys.argv:
        print(to_plain(report))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo cuối ngày cho sếp qua Telegram.")


if __name__ == "__main__":
    main()
