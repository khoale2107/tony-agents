"""
Theo dõi động thái đối thủ (ads & bài đăng) và cảnh báo về Telegram.

Đọc competitor.csv (Đối thủ, Loại, Nội dung, Ngày) với Loại = ad | post.
Gộp theo từng đối thủ, đếm số ad/post, rồi AI tóm tắt động thái từng
đối thủ + nêu mối ĐE DỌA cần đề phòng và CƠ HỘI có thể tận dụng.
Gửi Telegram hoặc in ra màn hình.
Chưa có competitor.csv thật thì tự dùng competitor_example.csv để chạy thử.

  python3 competitor_intel.py --dry-run   in ra màn hình
  python3 competitor_intel.py             gửi Telegram
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_rows() -> list[dict]:
    """Đọc competitor.csv; chưa có thì fallback competitor_example.csv."""
    real = HERE / fl.cfg("COMPETITOR_FILE", "competitor.csv")
    path = real if real.exists() else (HERE / "competitor_example.csv")
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def group_by_competitor(rows: list[dict]) -> list[dict]:
    """Gộp theo tên đối thủ, đếm số ad/post và giữ danh sách nội dung."""
    col_name = fl.cfg("COL_NAME", "Đối thủ")
    col_type = fl.cfg("COL_TYPE", "Loại")
    col_content = fl.cfg("COL_CONTENT", "Nội dung")
    col_date = fl.cfg("COL_DATE", "Ngày")
    buckets: dict = {}
    for r in rows:
        name = (r.get(col_name) or "").strip()
        if not name:
            continue
        loai = (r.get(col_type) or "").strip().lower()
        content = (r.get(col_content) or "").strip()
        ngay = (r.get(col_date) or "").strip()
        b = buckets.setdefault(name, {"name": name, "ads": 0, "posts": 0, "items": []})
        if loai == "ad":
            b["ads"] += 1
            kind = "AD"
        else:
            b["posts"] += 1
            kind = "POST"
        b["items"].append({"kind": kind, "content": content, "date": ngay})
    out = list(buckets.values())
    out.sort(key=lambda x: (x["ads"] + x["posts"]), reverse=True)
    return out


def build_ai_prompt(comps: list[dict]) -> str:
    brand = fl.cfg("BRAND_NAME", "thương hiệu của chúng tôi")
    lines = []
    for c in comps:
        lines.append(f"### {c['name']} — {c['ads']} quảng cáo, {c['posts']} bài đăng")
        for it in c["items"]:
            d = f" ({it['date']})" if it["date"] else ""
            lines.append(f"- [{it['kind']}]{d} {it['content']}")
    data = "\n".join(lines)
    return (
        f"Bạn là chuyên viên nghiên cứu thị trường cho {brand} (ngành cưới/sự kiện). "
        "Dưới đây là các động thái gần đây của đối thủ (AD = họ đang bỏ tiền chạy quảng cáo, "
        "POST = bài đăng thường):\n\n"
        f"{data}\n\n"
        "Viết bản tóm tắt tình báo tiếng Việt, ngắn gọn, theo cấu trúc sau:\n"
        "1) TÓM TẮT ĐỘNG THÁI: mỗi đối thủ 1 dòng — họ đang đẩy mạnh cái gì (khuyến mãi, "
        "sản phẩm, thông điệp, tần suất chạy ad).\n"
        "2) ĐE DỌA: 1-3 gạch đầu dòng về mối nguy cần đề phòng (đối thủ chiếm thị phần, "
        "phá giá, chiến dịch mạnh...).\n"
        "3) CƠ HỘI: 1-3 gạch đầu dòng về khoảng trống ta có thể tận dụng.\n"
        "4) NÊN LÀM NGAY: 1 hành động cụ thể cho tuần này.\n"
        "Không lặp lại nguyên văn dữ liệu. Trả về đúng 4 mục trên."
    )


def build_report(comps: list[dict], commentary: str) -> str:
    brand = fl.cfg("BRAND_NAME", "Tony Wedding")
    tot_ads = sum(c["ads"] for c in comps)
    tot_posts = sum(c["posts"] for c in comps)
    lines = [
        f"<b>🕵️ TÌNH BÁO ĐỐI THỦ — {brand}</b>",
        f"<i>{date.today().strftime('%d/%m/%Y')}</i>",
        "",
        f"Theo dõi <b>{len(comps)}</b> đối thủ · "
        f"<b>{tot_ads}</b> quảng cáo · <b>{tot_posts}</b> bài đăng",
        "",
        "<b>Động thái ghi nhận:</b>",
    ]
    for c in comps:
        lines.append(
            f"• <b>{c['name']}</b>: {c['ads']} ad · {c['posts']} post"
        )
    lines += ["", "<b>🧠 Phân tích AI:</b>", commentary]
    return "\n".join(lines)


def strip_html(text: str) -> str:
    for tag in ("<b>", "</b>", "<i>", "</i>"):
        text = text.replace(tag, "")
    return text


def main() -> None:
    rows = read_rows()
    comps = group_by_competitor(rows)
    if not comps:
        print("Không có dữ liệu đối thủ để xử lý.")
        return
    commentary = fl.ask_ai(build_ai_prompt(comps))
    report = build_report(comps, commentary)
    if "--dry-run" in sys.argv:
        print(strip_html(report))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo tình báo đối thủ qua Telegram.")


if __name__ == "__main__":
    main()
