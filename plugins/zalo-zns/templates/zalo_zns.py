#!/usr/bin/env python3
"""
Zalo ZNS — soạn & gửi tin ZNS: xác nhận đơn, nhắc lịch hẹn, nhắc thanh toán.

Đọc queue.csv (cột: Loại | Khách | SĐT | Thời điểm | Ghi chú).
  Loại: 'xác nhận đơn' | 'nhắc hẹn' | 'nhắc thanh toán'
Soạn nội dung theo mẫu (có thể nhờ AI làm mượt), rồi gửi qua connector Zalo (seam).

  ./run.sh --dry-run   |   ./run.sh
Dùng GÓI Claude Code cho phần soạn tin, không cần API key.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

TEMPLATES = {
    "xác nhận đơn": "Chào {kh}, {ct} xác nhận đơn của bạn: {gc}. Cảm ơn bạn đã tin tưởng!",
    "nhắc hẹn": "Chào {kh}, {ct} nhắc lịch hẹn của bạn vào {tp}: {gc}. Hẹn gặp bạn nhé!",
    "nhắc thanh toán": "Chào {kh}, {ct} nhắc khoản thanh toán {gc} đến hạn {tp}. Bạn hỗ trợ giúp nhé!",
}


def read_queue() -> list[dict]:
    p = HERE / "queue.csv"
    if not p.exists():
        p = HERE / "queue_example.csv"
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def build_messages(rows: list[dict]) -> list[tuple[str, str, str]]:
    ct = fl.cfg("COMPANY_NAME", "công ty")
    polish = fl.cfg("AI_POLISH", "0") == "1"
    out = []
    for r in rows:
        loai = (r.get("Loại", "") or "").strip().lower()
        tpl = TEMPLATES.get(loai, "Chào {kh}, {ct} có thông báo: {gc}")
        msg = tpl.format(kh=r.get("Khách", "quý khách"), ct=ct,
                         tp=r.get("Thời điểm", ""), gc=r.get("Ghi chú", ""))
        if polish:
            msg = fl.ask_ai(f"Viết lại tin nhắn ZNS sau cho tự nhiên, lịch sự, giữ đủ thông tin, "
                            f"1-2 câu, không thêm emoji quá đà: {msg}") or msg
        out.append((loai, r.get("SĐT", ""), msg))
    return out


def main() -> None:
    msgs = build_messages(read_queue())
    if not msgs:
        print("[!] queue.csv trống."); return
    if "--dry-run" in sys.argv:
        for loai, phone, m in msgs:
            print(f"[{loai}] → {phone or '(chưa có SĐT)'}: {m}\n")
        print(f"[i] Tổng {len(msgs)} tin ZNS (dry-run, chưa gửi thật).")
        return
    try:
        import connector as conn
    except ImportError:
        raise SystemExit("Chưa có connector.py gửi ZNS. Nhờ Claude Code viết (xem connector_example.py).")
    for _, phone, m in msgs:
        conn.send_zns(phone, m)
    print(f"Đã gửi {len(msgs)} tin ZNS.")


if __name__ == "__main__":
    main()
