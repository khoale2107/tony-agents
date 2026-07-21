#!/usr/bin/env python3
"""
Ops Daily Report — báo cáo vận hành cuối ngày.

Đọc orders.csv, đếm số đơn ở mỗi khâu, phát hiện khâu đang "tắc"
(tồn nhiều hoặc có đơn quá hạn / ứ đọng lâu), rồi để AI nhận định đơn
đang nghẽn ở đâu và đề xuất xử lý. Gửi Telegram hoặc in ra màn hình.

  python3 ops_daily.py --dry-run   in ra màn hình (không gửi)
  python3 ops_daily.py             gửi báo cáo cuối ngày qua Telegram

Không cấu hình gì vẫn chạy được: tự đọc orders_example.csv.
"""
from __future__ import annotations

import csv
import sys
from datetime import date, datetime
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

# Trình tự các khâu (đổi trong .env qua biến STAGES nếu xưởng bạn khác)
DEFAULT_STAGES = ["NHẬN", "THIẾT KẾ", "SẢN XUẤT", "QC", "GIAO", "XONG"]
ICON = {"NHẬN": "📥", "THIẾT KẾ": "✏️", "SẢN XUẤT": "🛠️",
        "QC": "🔍", "GIAO": "🚚", "XONG": "✅"}


def stages() -> list[dict]:
    raw = fl.cfg("STAGES", "")
    if raw.strip():
        return [s.strip() for s in raw.split(",") if s.strip()]
    return list(DEFAULT_STAGES)


def data_file() -> Path:
    """File dữ liệu thật (orders.csv) nếu có, ngược lại dùng file mẫu."""
    real = HERE / fl.cfg("ORDERS_FILE", "orders.csv")
    if real.exists():
        return real
    return HERE / "orders_example.csv"


def load_orders(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()}
                for row in csv.DictReader(f)]


def norm_stage(s: str, order: list[dict]) -> str:
    s = (s or "").strip().upper()
    for st in order:
        if st.upper() == s:
            return st
    return order[0]


def days_since(text) -> int:
    """Số ngày kể từ mốc cập nhật gần nhất (âm/0 nếu không đọc được)."""
    d = fl.parse_date(text)
    if not d:
        return 0
    return (date.today() - d).days


def analyze(rows: list[dict], order: list[dict]) -> dict:
    col_stage = fl.cfg("COL_STAGE", "Khâu")
    col_deadline = fl.cfg("COL_DEADLINE", "Hạn giao")
    col_update = fl.cfg("COL_UPDATE", "Cập nhật")
    done = order[-1]
    stale_days = int(fl.cfg("STALE_DAYS", "2") or "2")
    pileup = int(fl.cfg("PILEUP_THRESHOLD", "3") or "3")
    today = date.today()

    counts = {st: 0 for st in order}
    overdue = {st: 0 for st in order}
    stale = {st: 0 for st in order}
    overdue_list: list[dict] = []
    active = 0

    for r in rows:
        st = norm_stage(r.get(col_stage, ""), order)
        counts[st] += 1
        if st == done:
            continue
        active += 1
        dl = fl.parse_date(r.get(col_deadline, ""))
        if dl and dl < today:
            overdue[st] += 1
            overdue_list.append({"row": r, "stage": st,
                                 "late": (today - dl).days})
        if days_since(r.get(col_update, "")) >= stale_days:
            stale[st] += 1

    # Điểm "tắc" mỗi khâu = quá hạn*3 + ứ đọng*2 + (tồn nhiều)*1
    stuck = []
    for st in order:
        if st == done:
            continue
        score = overdue[st] * 3 + stale[st] * 2
        if counts[st] >= pileup:
            score += 1
        if score > 0:
            stuck.append({"stage": st, "count": counts[st],
                          "overdue": overdue[st], "stale": stale[st],
                          "score": score})
    stuck.sort(key=lambda x: -x["score"])
    overdue_list.sort(key=lambda x: -x["late"])

    return {"counts": counts, "overdue": overdue, "stale": stale,
            "active": active, "total": len(rows),
            "stuck": stuck, "overdue_list": overdue_list,
            "stale_days": stale_days, "pileup": pileup}


def build_prompt(a: dict, order: list[dict]) -> str:
    done = order[-1]
    lines = []
    for st in order:
        if st == done:
            continue
        lines.append(f"- {st}: {a['counts'][st]} đơn tồn, "
                     f"{a['overdue'][st]} quá hạn, {a['stale'][st]} ứ đọng "
                     f"(>{a['stale_days']} ngày chưa cập nhật)")
    detail = "\n".join(lines) or "- (không có đơn nào đang chạy)"
    late = "\n".join(
        f"- {o['row'].get('Mã đơn','?')} ({o['stage']}): trễ {o['late']} ngày"
        for o in a["overdue_list"][:6]) or "- (không có đơn quá hạn)"
    return (
        f"Bạn là quản lý vận hành của {fl.cfg('COMPANY_NAME','một xưởng')}. "
        "Cuối ngày, tình hình đơn theo từng khâu:\n"
        f"{detail}\n\nĐơn quá hạn đáng chú ý:\n{late}\n\n"
        "Viết nhận định ngắn (tối đa 5 câu, tiếng Việt): đơn đang TẮC ở khâu nào, "
        "vì sao (tồn nhiều / quá hạn / ứ đọng), và 1-2 đề xuất xử lý cụ thể cho "
        "sáng mai. Không lặp lại toàn bộ con số. Chỉ trả về đoạn nhận định.")


def build_report(a: dict, order: list[dict], commentary: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Xưởng")
    done = order[-1]
    lines = [f"<b>🌙 BÁO CÁO VẬN HÀNH CUỐI NGÀY — {company}</b>",
             f"<i>{datetime.now():%d/%m/%Y %H:%M} · "
             f"{a['active']} đơn đang chạy / {a['total']} tổng</i>", ""]
    for st in order:
        c = a["counts"][st]
        flag = ""
        if st != done:
            marks = []
            if a["overdue"][st]:
                marks.append(f"⏰{a['overdue'][st]} quá hạn")
            if a["stale"][st]:
                marks.append(f"🐌{a['stale'][st]} ứ đọng")
            if marks:
                flag = " — " + ", ".join(marks)
        lines.append(f"{ICON.get(st,'•')} <b>{st}</b>: {c} đơn{flag}")
    lines.append("")

    if a["stuck"]:
        top = a["stuck"][0]
        lines.append(f"<b>🚨 Khâu tắc nhất: {top['stage']}</b> "
                     f"({top['count']} tồn, {top['overdue']} quá hạn)")
    else:
        lines.append("<b>🟢 Không phát hiện khâu tắc.</b>")
    lines += ["", "<b>🧠 Nhận định &amp; đề xuất:</b>", commentary]
    return "\n".join(lines)


def _plain(html: str) -> str:
    for a, b in (("<b>", ""), ("</b>", ""), ("<i>", ""),
                 ("</i>", ""), ("&amp;", "&")):
        html = html.replace(a, b)
    return html


def main() -> None:
    dry = "--dry-run" in sys.argv
    order = stages()
    path = data_file()
    rows = load_orders(path)
    if path.name.endswith("_example.csv"):
        print(f"[i] Chưa có {fl.cfg('ORDERS_FILE','orders.csv')} — "
              "đang dùng orders_example.csv để chạy thử.")

    a = analyze(rows, order)
    commentary = fl.ask_ai(build_prompt(a, order))
    report = build_report(a, order, commentary)

    if dry:
        print(_plain(report))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo vận hành cuối ngày qua Telegram.")


if __name__ == "__main__":
    main()
