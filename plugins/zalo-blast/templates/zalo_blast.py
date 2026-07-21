#!/usr/bin/env python3
"""
Zalo blast khách cũ theo phân khúc — AI soạn tin RIÊNG từng nhóm:
  • Sinh nhật hôm nay
  • Lâu chưa quay lại (>= WINRATE_DAYS ngày, mặc định 180 = 6 tháng)

Đọc customers.csv (cột: Tên | SĐT | Ngày sinh | Lần cuối mua).
Gửi qua connector Zalo (seam). Dùng GÓI Claude Code cho phần soạn tin.

  ./run.sh --dry-run   |   ./run.sh
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_customers() -> list[dict]:
    p = HERE / "customers.csv"
    if not p.exists():
        p = HERE / "customers_example.csv"
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def segment(rows: list[dict]):
    lapsed_days = int(fl.cfg("LAPSED_DAYS", "180"))
    today = date.today()
    birthday, lapsed = [], []
    for r in rows:
        dob = fl.parse_date(r.get("Ngày sinh", ""))
        last = fl.parse_date(r.get("Lần cuối mua", ""))
        if dob and dob.month == today.month and dob.day == today.day:
            birthday.append(r)
        if last and (today - last).days >= lapsed_days:
            lapsed.append(r)
    return birthday, lapsed


def draft(segment_name: str, sample_names: list[str]) -> str:
    ct = fl.cfg("COMPANY_NAME", "công ty")
    offer = fl.cfg("OFFER", "ưu đãi đặc biệt cho khách thân thiết")
    prompt = (f"Viết 1 tin nhắn Zalo ngắn (2-3 câu, ấm áp, có 1 emoji) từ {ct} gửi nhóm khách '{segment_name}'. "
              f"Kèm {offer}. Dùng {{ten}} làm chỗ điền tên khách. Chỉ trả về nội dung tin.")
    return fl.ask_ai(prompt)


def main() -> None:
    rows = read_customers()
    birthday, lapsed = segment(rows)
    dry = "--dry-run" in sys.argv
    plan = [("Sinh nhật hôm nay", birthday), ("Lâu chưa quay lại", lapsed)]

    conn = None
    if not dry:
        try:
            import connector as conn  # noqa
        except ImportError:
            raise SystemExit("Chưa có connector.py để gửi thật. Nhờ Claude Code viết (xem connector_example.py).")

    total = 0
    for name, group in plan:
        if not group:
            print(f"\n=== {name}: (không có khách) ==="); continue
        tpl = draft(name, [r.get("Tên", "") for r in group[:3]])
        print(f"\n=== {name} ({len(group)} khách) ===\nMẫu tin: {tpl}\n")
        for r in group:
            msg = tpl.replace("{ten}", r.get("Tên", "bạn"))
            if dry:
                print(f"  → {r.get('SĐT','')}: {msg}")
            else:
                conn.send_message(r.get("SĐT", ""), msg)
            total += 1
    print(f"\n[i] Tổng {total} tin " + ("(dry-run, chưa gửi)." if dry else "đã gửi."))


if __name__ == "__main__":
    main()
