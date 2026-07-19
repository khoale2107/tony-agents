"""
ADAPTER TUỲ BIẾN — lấy số liệu từ ERP / phần mềm kế toán riêng của bạn.

CÁCH DÙNG:
  1. Đặt SOURCE=custom trong file .env
  2. Đổi tên file này thành  adapter_custom.py
  3. Viết phần thân hàm fetch_rows() cho đúng nguồn của bạn.
     (Cách nhanh: mở Claude Code trong thư mục này và nói:
      "Dữ liệu của tôi ở <tên ERP>, đây là API/tài khoản: ..." — Claude sẽ viết giúp.)

HỢP ĐỒNG (bắt buộc):
  fetch_rows() trả về list[dict]. Mỗi dict là một dòng thu/chi, có các khoá:
     "Ngày"     : chuỗi ngày, ví dụ "12/07/2026" hoặc "2026-07-12"
     "Loại"     : chứa chữ "Doanh thu"/"thu"  hoặc  "Chi phí"/"chi"
     "Hạng mục" : tên khoản, ví dụ "Lương nhân sự"
     "Số tiền"  : số tiền (số hoặc chuỗi "1.500.000")
  (Tên khoá phải khớp COL_DATE/COL_TYPE/COL_ITEM/COL_AMOUNT trong .env — mặc định như trên.)
"""

import os


def cfg(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def fetch_rows() -> list[dict]:
    # ============ VÍ DỤ A — gọi REST API bất kỳ (KiotViet/Sapo/Misa/ERP nhà) ============
    # import json, urllib.request
    # token = cfg("ERP_API_TOKEN")
    # req = urllib.request.Request(
    #     "https://erp-cua-ban/api/transactions?month=current",
    #     headers={"Authorization": f"Bearer {token}"},
    # )
    # data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    # rows = []
    # for t in data["items"]:
    #     rows.append({
    #         "Ngày": t["date"],
    #         "Loại": "Doanh thu" if t["kind"] == "income" else "Chi phí",
    #         "Hạng mục": t.get("category", "Khác"),
    #         "Số tiền": t["amount"],
    #     })
    # return rows

    # ============ VÍ DỤ B — Odoo (XML-RPC, CHỈ ĐỌC, dùng thư viện chuẩn) ============
    # import xmlrpc.client
    # url, db = cfg("ODOO_URL"), cfg("ODOO_DB")
    # uid = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common").authenticate(
    #     db, cfg("ODOO_USER"), cfg("ODOO_API_KEY"), {})
    # models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    # # Đọc account.move.line đã posted trong kỳ; map income->Doanh thu, expense->Chi phí.
    # # (Chỉ dùng search_read/read — KHÔNG create/write/unlink.)
    # ...
    # return rows

    raise NotImplementedError(
        "Chưa viết fetch_rows(). Nhờ Claude Code viết cho ERP của bạn, "
        "hoặc điền theo một trong hai ví dụ ở trên."
    )
