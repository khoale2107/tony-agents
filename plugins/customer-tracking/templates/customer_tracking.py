#!/usr/bin/env python3
"""
Khách tự tra trạng thái đơn theo SỐ ĐIỆN THOẠI — đọc orders.csv, AI trả lời tự nhiên.

  ./run.sh 0901234567            -> tìm đơn của SĐT đó, AI trả lời trạng thái từng đơn
  ./run.sh 0901234567 --dry-run  -> giống trên nhưng ghi rõ đây là bản chạy thử (không khác biệt, không gửi đi)
  ./run.sh                       -> hướng dẫn cách dùng

Không cần Telegram. Thiếu orders.csv thì tự dùng orders_example.csv để chạy thử ngay.
Không thấy SĐT nào thì báo lịch sự.
"""
from __future__ import annotations

import sys
import csv
import io
import re
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def _cols():
    return {
        "code": fl.cfg("COL_CODE", "Mã đơn"),
        "customer": fl.cfg("COL_CUSTOMER", "Khách hàng"),
        "phone": fl.cfg("COL_PHONE", "SĐT"),
        "product": fl.cfg("COL_PRODUCT", "Sản phẩm"),
        "stage": fl.cfg("COL_STAGE", "Trạng thái"),
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
    out = []
    for row in reader:
        clean = {}
        for k, v in row.items():
            if not isinstance(k, str):
                continue  # bỏ qua cột thừa (restkey) khi dòng có nhiều cột hơn tiêu đề
            if isinstance(v, list):
                v = " ".join(v)
            clean[k.strip()] = (v or "").strip()
        out.append(clean)
    return out


def norm_phone(x: str) -> str:
    """Chuẩn hoá SĐT về chuỗi chỉ chứa chữ số, bỏ +84/84 đầu -> 0."""
    digits = re.sub(r"\D", "", x or "")
    if digits.startswith("84") and len(digits) >= 10:
        digits = "0" + digits[2:]
    return digits


def find_by_phone(rows: list[dict], phone_query: str) -> list[dict]:
    c = _cols()
    q = norm_phone(phone_query)
    if not q:
        return []
    hits = []
    for r in rows:
        if norm_phone(r.get(c["phone"], "")) == q:
            hits.append(r)
    return hits


def _days_left(due_raw: str):
    d = fl.parse_date(due_raw)
    if not d:
        return None
    return (d - date.today()).days


def render_orders_text(orders: list[dict]) -> str:
    """Tóm tắt dạng text các đơn tìm được (đưa vào prompt AI + in ra tham khảo)."""
    c = _cols()
    lines = []
    for i, r in enumerate(orders, 1):
        due_raw = r.get(c["due_date"], "")
        dl = _days_left(due_raw)
        due_txt = due_raw or "(chưa có)"
        if dl is not None:
            due_txt += f" (còn {dl} ngày)" if dl >= 0 else f" (đã quá hạn {-dl} ngày)"
        lines.append(
            f"Đơn {i}:\n"
            f"  - Mã đơn: {r.get(c['code'], '') or '(không mã)'}\n"
            f"  - Khách hàng: {r.get(c['customer'], '')}\n"
            f"  - Sản phẩm: {r.get(c['product'], '')}\n"
            f"  - Trạng thái hiện tại: {r.get(c['stage'], '') or '(chưa rõ)'}\n"
            f"  - Ngày đặt: {r.get(c['order_date'], '') or '(chưa có)'}\n"
            f"  - Hạn giao: {due_txt}\n"
            f"  - Ghi chú: {r.get(c['note'], '') or '(trống)'}"
        )
    return "\n\n".join(lines)


def ai_reply(orders: list[dict], phone_query: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Tony Wedding")
    detail = render_orders_text(orders)
    name = orders[0].get(_cols()["customer"], "") if orders else ""
    prompt = (
        f"Bạn là nhân viên chăm sóc khách hàng của {company} (dịch vụ trang trí cưới/sự kiện). "
        f"Khách vừa nhắn số điện thoại {phone_query} để hỏi tình trạng đơn của họ. "
        "Dựa vào dữ liệu đơn dưới đây, hãy viết MỘT tin nhắn trả lời khách bằng tiếng Việt, "
        "giọng thân thiện, lịch sự, xưng hô lịch sự (anh/chị). "
        "Nêu rõ trạng thái hiện tại của TỪNG đơn, còn bao nhiêu ngày tới hạn giao, "
        "và một câu trấn an/hẹn tiếp theo phù hợp với trạng thái. "
        "Nếu có đơn quá hạn thì xin lỗi nhẹ nhàng. Ngắn gọn, không bịa thông tin ngoài dữ liệu, "
        "không dùng markdown, không liệt kê lại nguyên văn dữ liệu thô.\n\n"
        f"Tên khách (nếu biết): {name}\n\n"
        f"DỮ LIỆU ĐƠN:\n{detail}"
    )
    return fl.ask_ai(prompt)


def polite_not_found(phone_query: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Tony Wedding")
    return (
        f"Dạ {company} chưa tìm thấy đơn nào gắn với số điện thoại {phone_query} ạ.\n"
        "Anh/chị vui lòng kiểm tra lại số đã dùng khi đặt, hoặc nhắn thêm mã đơn / tên "
        "người đặt để bên em tra giúp nhé. Xin cảm ơn anh/chị!"
    )


def main() -> None:
    args = list(sys.argv[1:])
    dry_run = "--dry-run" in args
    positional = [a for a in args if not a.startswith("-")]

    if not positional:
        print("Cách dùng: ./run.sh <SĐT>   (ví dụ: ./run.sh 0901234567)")
        print("Thêm --dry-run để chạy thử.")
        return

    phone_query = positional[0]
    rows = load_orders()
    orders = find_by_phone(rows, phone_query)

    if dry_run:
        print(f"[dry-run] Tra SĐT: {phone_query}")

    if not orders:
        print(polite_not_found(phone_query))
        return

    print(f"Tìm thấy {len(orders)} đơn cho SĐT {phone_query}:\n")
    print(render_orders_text(orders))
    print("\n--- Trả lời cho khách (AI) ---")
    print(ai_reply(orders, phone_query))


if __name__ == "__main__":
    main()
