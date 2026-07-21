#!/usr/bin/env python3
"""
Survey tự động sau dịch vụ — 2 việc:

  send       Soạn tin mời khảo sát cho khách VỪA XONG dịch vụ (đọc done.csv).
  summarize  Tổng hợp phản hồi khách bằng AI (đọc responses.csv), gửi Telegram.

  ./run.sh send --dry-run
  ./run.sh summarize --dry-run   |   ./run.sh summarize

Gửi tin thật qua connector (xem connector_example.py — seam để nối Zalo/SMS/email).
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_csv(*names) -> list[dict]:
    for name in names:
        p = HERE / name
        if p.exists():
            return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))
    return []


def do_send(dry: bool) -> None:
    rows = read_csv("done.csv", "done_example.csv")
    link = fl.cfg("SURVEY_LINK", "https://forms.gle/vi-du")
    company = fl.cfg("COMPANY_NAME", "công ty")
    if not rows:
        print("[!] Không có khách trong done.csv"); return
    msgs = []
    for r in rows:
        name = r.get("Khách", "quý khách")
        svc = r.get("Dịch vụ", "dịch vụ")
        msg = (f"Chào {name}, cảm ơn bạn đã tin tưởng {company} với {svc}. "
               f"Bạn dành 30 giây đánh giá giúp mình nhé: {link} 💛")
        msgs.append((r.get("SĐT", ""), msg))
    if dry:
        for phone, m in msgs:
            print(f"→ {phone or '(chưa có SĐT)'}: {m}\n")
        print(f"[i] Tổng {len(msgs)} tin (dry-run, chưa gửi thật).")
        return
    try:
        import connector as conn
    except ImportError:
        raise SystemExit("Chưa có connector.py để gửi thật. Nhờ Claude Code viết (xem connector_example.py).")
    for phone, m in msgs:
        conn.send_message(phone, m)
    print(f"Đã gửi {len(msgs)} tin mời khảo sát.")


def do_summarize(dry: bool) -> None:
    rows = read_csv("responses.csv", "responses_example.csv")
    if not rows:
        print("[!] Chưa có phản hồi trong responses.csv"); return
    scores = [fl.parse_amount(r.get("Điểm", "")) for r in rows if r.get("Điểm")]
    avg = sum(scores) / len(scores) if scores else 0
    comments = "\n".join(f"- {r.get('Khách','?')} ({r.get('Điểm','?')}đ): {r.get('Nhận xét','')}"
                         for r in rows)
    prompt = (f"Đây là {len(rows)} phản hồi khách sau dịch vụ (điểm 1-5), điểm TB {avg:.1f}. "
              f"Phản hồi:\n{comments}\n\n"
              "Tổng hợp bằng tiếng Việt: mức hài lòng chung, 2 điểm khách khen, "
              "2 vấn đề cần cải thiện, 1 việc nên làm ngay. Ngắn gọn, gạch đầu dòng.")
    note = fl.ask_ai(prompt)
    company = fl.cfg("COMPANY_NAME", "Công ty")
    report = (f"<b>📝 TỔNG HỢP KHẢO SÁT — {company}</b>\n"
              f"<i>{len(rows)} phản hồi · điểm TB {avg:.1f}/5</i>\n\n{note}")
    if dry:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi tổng hợp khảo sát qua Telegram.")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry = "--dry-run" in sys.argv
    cmd = args[0] if args else "summarize"
    if cmd == "send":
        do_send(dry)
    elif cmd == "summarize":
        do_summarize(dry)
    else:
        print("Dùng: ./run.sh send|summarize [--dry-run]")


if __name__ == "__main__":
    main()
