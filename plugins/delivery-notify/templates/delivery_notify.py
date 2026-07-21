#!/usr/bin/env python3
"""
Đánh dấu giao hàng + báo khách:
  • Đọc deliveries.csv (cột: Mã đơn | Khách | SĐT | Địa chỉ | Trạng thái).
  • Với đơn có Trạng thái chứa "đã giao" mà CHƯA báo -> AI soạn tin báo khách.
  • Gửi qua connector (seam: send_message(phone, text)). --dry-run chỉ in tin.
  • Sau khi báo: ghi cột "Đã báo" = ngày, để lần sau không báo lại.

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

DATA = HERE / "deliveries.csv"
if not DATA.exists():
    DATA = HERE / "deliveries_example.csv"

DELIVERED_KW = "đã giao"
NOTIFIED_COL = "Đã báo"


def read_rows() -> list[dict]:
    return list(csv.DictReader(DATA.read_text(encoding="utf-8-sig").splitlines()))


def write_rows(rows: list[dict], fieldnames: list[str]) -> None:
    with DATA.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def is_delivered(row: dict) -> bool:
    return DELIVERED_KW in (row.get("Trạng thái", "") or "").lower()


def already_notified(row: dict) -> bool:
    return bool((row.get(NOTIFIED_COL, "") or "").strip())


def draft(row: dict) -> str:
    ct = fl.cfg("COMPANY_NAME", "cửa hàng")
    hotline = fl.cfg("HOTLINE", "")
    ten = row.get("Khách", "quý khách")
    ma = row.get("Mã đơn", "")
    dc = row.get("Địa chỉ", "")
    extra = f" Hotline hỗ trợ: {hotline}." if hotline else ""
    prompt = (
        f"Viết 1 tin nhắn ngắn (2-3 câu, lịch sự, ấm áp, 1 emoji) từ {ct} "
        f"báo cho khách '{ten}' rằng đơn hàng mã {ma} đã được giao thành công "
        f"tới địa chỉ '{dc}'. Cảm ơn khách đã mua hàng và mời phản hồi nếu cần hỗ trợ.{extra} "
        f"Chỉ trả về nội dung tin, không thêm ghi chú."
    )
    return fl.ask_ai(prompt).strip()


def main() -> None:
    dry = "--dry-run" in sys.argv
    rows = read_rows()
    fieldnames = list(rows[0].keys()) if rows else [
        "Mã đơn", "Khách", "SĐT", "Địa chỉ", "Trạng thái"
    ]
    if NOTIFIED_COL not in fieldnames:
        fieldnames.append(NOTIFIED_COL)

    todo = [r for r in rows if is_delivered(r) and not already_notified(r)]

    if not todo:
        print("[i] Không có đơn 'đã giao' nào cần báo (tất cả đã báo hoặc chưa giao).")
        return

    conn = None
    if not dry:
        try:
            import connector as conn  # noqa
        except ImportError:
            raise SystemExit(
                "Chưa có connector.py để gửi thật. Nhờ Claude Code viết send_message() "
                "(xem connector_example.py)."
            )

    today = date.today().strftime("%d/%m/%Y")
    sent = 0
    for r in todo:
        r.setdefault(NOTIFIED_COL, "")
        msg = draft(r)
        phone = r.get("SĐT", "")
        print(f"\n=== Đơn {r.get('Mã đơn','')} — {r.get('Khách','')} ({phone}) ===\n{msg}")
        if dry:
            print("  [dry-run] chưa gửi, chưa cập nhật trạng thái.")
            continue
        conn.send_message(phone, msg)
        r[NOTIFIED_COL] = today
        sent += 1

    if dry:
        print(f"\n[i] {len(todo)} đơn sẽ được báo (dry-run, chưa gửi, chưa ghi file).")
        return

    write_rows(rows, fieldnames)
    print(f"\n[i] Đã báo {sent} khách và cập nhật cột '{NOTIFIED_COL}' trong {DATA.name}.")

    if fl.cfg("TELEGRAM_BOT_TOKEN") and fl.cfg("TELEGRAM_CHAT_ID"):
        fl.send_telegram(
            f"<b>Báo giao hàng</b>: đã nhắn <b>{sent}</b> khách "
            f"(đơn đã giao) lúc {today}."
        )


if __name__ == "__main__":
    main()
