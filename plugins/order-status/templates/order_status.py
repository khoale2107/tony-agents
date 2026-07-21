#!/usr/bin/env python3
"""
Theo dõi trạng thái đơn theo khâu — đọc orders.csv, đếm đơn ở mỗi khâu.

  ./run.sh --dry-run     -> in bảng: mỗi khâu bao nhiêu đơn + liệt kê mã (không gửi)
  ./run.sh <mã đơn>      -> in chi tiết 1 đơn + khâu hiện tại
  ./run.sh               -> gửi Telegram tổng quan (chạy thật)

Thiếu orders.csv thì tự dùng orders_example.csv để chạy thử ngay.
"""
from __future__ import annotations

import sys
import csv
import io
from collections import defaultdict
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

# Thứ tự các khâu trong quy trình (đơn đi từ trái sang phải).
STAGES = [
    "Tiếp nhận",
    "Thiết kế",
    "Duyệt mẫu",
    "Sản xuất",
    "Kiểm tra QC",
    "Giao / Setup",
    "Hoàn tất",
]


def _cols():
    return {
        "code": fl.cfg("COL_CODE", "Mã đơn"),
        "customer": fl.cfg("COL_CUSTOMER", "Khách hàng"),
        "product": fl.cfg("COL_PRODUCT", "Sản phẩm"),
        "stage": fl.cfg("COL_STAGE", "Khâu"),
        "order_date": fl.cfg("COL_ORDER_DATE", "Ngày đặt"),
        "due_date": fl.cfg("COL_DUE_DATE", "Hạn giao"),
        "note": fl.cfg("COL_NOTE", "Ghi chú"),
    }


def load_orders() -> list[dict]:
    real = HERE / "orders.csv"
    path = real if real.exists() else HERE / "orders_example.csv"
    if not path.exists():
        raise SystemExit("Không thấy orders.csv (hoặc orders_example.csv).")
    if path.name.endswith("_example.csv"):
        print("[i] Chưa có orders.csv — đang dùng orders_example.csv để chạy thử.")
    raw = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))

    def _clean(v) -> str:
        if isinstance(v, list):  # cột thừa do dấu phẩy chưa bọc "..."
            v = " ".join(str(x) for x in v)
        return (v or "").strip() if v is not None else ""

    out = []
    for row in reader:
        out.append({(k or "").strip(): _clean(v) for k, v in row.items() if k is not None})
    return out


def _match_stage(value: str) -> str:
    """Ghép giá trị khâu trong dữ liệu vào danh sách STAGES (không phân biệt hoa/thường/dấu cách)."""
    v = (value or "").strip().lower()
    for s in STAGES:
        if s.lower() == v:
            return s
    for s in STAGES:
        if v and (v in s.lower() or s.lower() in v):
            return s
    return value.strip() or "(chưa rõ)"


def group_by_stage(rows: list[dict]):
    c = _cols()
    buckets = defaultdict(list)
    for r in rows:
        stage = _match_stage(r.get(c["stage"], ""))
        buckets[stage].append(r.get(c["code"], "").strip() or "(không mã)")
    return buckets


def _days_left(due_raw: str):
    d = fl.parse_date(due_raw)
    if not d:
        return None
    return (d - date.today()).days


def render_overview(rows: list[dict]) -> str:
    """Bảng text tổng quan theo khâu (dùng cho cả --dry-run và log)."""
    buckets = group_by_stage(rows)
    total = len(rows)
    lines = [f"BẢNG THEO DÕI ĐƠN THEO KHÂU — tổng {total} đơn", ""]
    # Các khâu đã biết theo đúng thứ tự trước, khâu lạ để sau.
    known = [s for s in STAGES if s in buckets]
    extra = [s for s in buckets if s not in STAGES]
    for stage in known + extra:
        codes = buckets[stage]
        lines.append(f"[{stage}] — {len(codes)} đơn")
        lines.append("    " + ", ".join(codes))
    return "\n".join(lines)


def render_overview_html(rows: list[dict]) -> str:
    buckets = group_by_stage(rows)
    total = len(rows)
    company = fl.cfg("COMPANY_NAME", "Xưởng")
    out = [f"<b>📦 {company} — Trạng thái đơn theo khâu</b>",
           f"Tổng: <b>{total}</b> đơn\n"]
    known = [s for s in STAGES if s in buckets]
    extra = [s for s in buckets if s not in STAGES]
    for stage in known + extra:
        codes = buckets[stage]
        out.append(f"<b>{stage}</b>: {len(codes)} đơn")
        out.append(f"   <i>{', '.join(codes)}</i>")
    # Đơn sắp tới hạn / trễ hạn
    c = _cols()
    urgent = []
    for r in rows:
        stage = _match_stage(r.get(c["stage"], ""))
        if stage == "Hoàn tất":
            continue
        dl = _days_left(r.get(c["due_date"], ""))
        if dl is not None and dl <= int(fl.cfg("DUE_SOON_DAYS", "2")):
            code = r.get(c["code"], "").strip()
            tag = "TRỄ" if dl < 0 else "sắp tới hạn"
            urgent.append(f"   ⚠️ {code} — {tag} ({dl} ngày) — đang ở [{stage}]")
    if urgent:
        out.append("\n<b>Cần chú ý:</b>")
        out.extend(urgent)
    return "\n".join(out)


def ai_note(rows: list[dict]) -> str:
    overview = render_overview(rows)
    prompt = (
        "Bạn là quản lý sản xuất của một xưởng cưới/sự kiện. Dưới đây là bảng đơn theo khâu. "
        "Nhận xét NGẮN GỌN (2-3 câu tiếng Việt): khâu nào đang ùn (nhiều đơn nhất/nghẽn cổ chai), "
        "đơn nào cần ưu tiên đẩy. Không lặp lại số liệu, chỉ đưa ý hành động.\n\n" + overview
    )
    return fl.ask_ai(prompt)


def show_one(rows: list[dict], code_query: str) -> None:
    c = _cols()
    q = code_query.strip().lower()
    found = [r for r in rows if r.get(c["code"], "").strip().lower() == q]
    if not found:
        # thử khớp gần đúng
        found = [r for r in rows if q in r.get(c["code"], "").strip().lower()]
    if not found:
        print(f"Không tìm thấy đơn có mã '{code_query}'.")
        codes = [r.get(c["code"], "").strip() for r in rows]
        print("Các mã hiện có: " + ", ".join(x for x in codes if x))
        return
    for r in found:
        stage = _match_stage(r.get(c["stage"], ""))
        idx = STAGES.index(stage) if stage in STAGES else -1
        pos = f"{idx + 1}/{len(STAGES)}" if idx >= 0 else "?"
        dl = _days_left(r.get(c["due_date"], ""))
        due_txt = r.get(c["due_date"], "") or "(chưa có)"
        if dl is not None:
            due_txt += f"  ({'trễ ' + str(-dl) + ' ngày' if dl < 0 else 'còn ' + str(dl) + ' ngày'})"
        print("=" * 44)
        print(f"Mã đơn     : {r.get(c['code'], '')}")
        print(f"Khách hàng : {r.get(c['customer'], '')}")
        print(f"Sản phẩm   : {r.get(c['product'], '')}")
        print(f"Ngày đặt   : {r.get(c['order_date'], '')}")
        print(f"Hạn giao   : {due_txt}")
        print(f"Ghi chú    : {r.get(c['note'], '') or '(trống)'}")
        print("-" * 44)
        print(f"KHÂU HIỆN TẠI: {stage}  (bước {pos})")
        # thanh tiến trình
        if idx >= 0:
            bar = " -> ".join(
                (f"[{s}]" if i == idx else s) for i, s in enumerate(STAGES)
            )
            print("Tiến trình : " + bar)
        print("=" * 44)


def main() -> None:
    args = [a for a in sys.argv[1:]]
    dry_run = "--dry-run" in args
    positional = [a for a in args if not a.startswith("-")]

    rows = load_orders()

    # Tra 1 đơn cụ thể
    if positional:
        show_one(rows, positional[0])
        return

    # Tổng quan
    if dry_run:
        print(render_overview(rows))
        print("\n--- Nhận định AI ---")
        print(ai_note(rows))
        print("\n[dry-run] Không gửi Telegram.")
        return

    # Chạy thật -> gửi Telegram
    html = render_overview_html(rows)
    note = ai_note(rows)
    if note:
        html += f"\n\n<b>🤖 Nhận định:</b>\n<i>{note}</i>"
    fl.send_telegram(html)
    print("Đã gửi Telegram tổng quan trạng thái đơn.")


if __name__ == "__main__":
    main()
