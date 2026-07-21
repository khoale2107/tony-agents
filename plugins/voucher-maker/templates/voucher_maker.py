#!/usr/bin/env python3
"""
Voucher Maker — bot tạo nội dung voucher/ấn phẩm theo template.

Đưa 1 câu mô tả, AI soạn nội dung hoàn chỉnh (tiêu đề, mô tả, điều kiện,
thời hạn) theo template thương hiệu trong .env, tự sinh mã voucher, rồi
xuất ra voucher.html (đơn giản, tự chứa) và in text ra màn hình.

  ./run.sh "Giảm 20% chụp cưới tháng 8"     tạo 1 voucher
  ./run.sh --dry-run                          chạy thử với yêu cầu mẫu (CSV)
  ./run.sh --dry-run "Tặng album ảnh cưới"    chạy thử, không cần cấu hình

Không cần ảnh, không cần Telegram.
"""
from __future__ import annotations

import html
import json
import random
import re
import string
import sys
from datetime import date, timedelta
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def gen_code() -> str:
    """Sinh mã voucher: PREFIX + 5 ký tự chữ-số ngẫu nhiên."""
    prefix = fl.cfg("VOUCHER_PREFIX", "TW").upper()
    alphabet = string.ascii_uppercase + string.digits
    tail = "".join(random.choice(alphabet) for _ in range(5))
    return f"{prefix}{tail}"


def extract_json(text: str) -> dict:
    """Bóc khối JSON đầu tiên trong output của AI (bỏ qua ```json fences)."""
    if not text:
        return {}
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except (ValueError, TypeError):
        return {}


def compose(request: str) -> dict:
    """Nhờ AI soạn nội dung voucher theo template thương hiệu."""
    brand = fl.cfg("BRAND_NAME", "Tony Wedding")
    tone = fl.cfg("TEMPLATE_HINT", "sang trọng, ấm áp, ngắn gọn, dùng cho ngành ảnh cưới")
    valid_days = fl.cfg("VALID_DAYS", "30")

    prompt = (
        f"Bạn là copywriter của thương hiệu \"{brand}\". "
        f"Soạn nội dung 1 voucher/ấn phẩm khuyến mãi từ yêu cầu: \"{request}\".\n"
        f"Phong cách: {tone}.\n"
        "Trả về DUY NHẤT một object JSON (không giải thích, không markdown) với các khóa:\n"
        '  "tieu_de": tiêu đề ngắn gọn ấn tượng (in hoa được),\n'
        '  "phu_de": 1 dòng phụ đề/khẩu hiệu ngắn,\n'
        '  "uu_dai": mô tả ưu đãi cụ thể 1 câu,\n'
        '  "dieu_kien": mảng 2-4 điều kiện áp dụng ngắn gọn,\n'
        f'  "thoi_han_ngay": số ngày voucher còn hiệu lực (số nguyên, mặc định {valid_days}),\n'
        '  "ghi_chu": 1 dòng ghi chú/kêu gọi hành động.\n'
        "Tiếng Việt. Chỉ trả JSON."
    )
    data = extract_json(fl.ask_ai(prompt))

    # Fallback nếu AI không trả JSON hợp lệ
    if not data.get("tieu_de"):
        data = {
            "tieu_de": request.upper()[:60],
            "phu_de": brand,
            "uu_dai": request,
            "dieu_kien": ["Áp dụng theo thể lệ chương trình", "Không quy đổi thành tiền mặt"],
            "thoi_han_ngay": valid_days,
            "ghi_chu": "Liên hệ để đặt lịch ngay hôm nay.",
        }

    try:
        days = int(str(data.get("thoi_han_ngay", valid_days)).strip() or valid_days)
    except ValueError:
        days = int(valid_days)
    han = date.today() + timedelta(days=days)

    dk = data.get("dieu_kien") or []
    if isinstance(dk, str):
        dk = [dk]

    return {
        "tieu_de": str(data.get("tieu_de", request)).strip(),
        "phu_de": str(data.get("phu_de", brand)).strip(),
        "uu_dai": str(data.get("uu_dai", request)).strip(),
        "dieu_kien": [str(x).strip() for x in dk if str(x).strip()],
        "ghi_chu": str(data.get("ghi_chu", "")).strip(),
        "ma": gen_code(),
        "phat_hanh": date.today().strftime("%d/%m/%Y"),
        "han": han.strftime("%d/%m/%Y"),
    }


def as_text(v: dict) -> str:
    brand = fl.cfg("BRAND_NAME", "Tony Wedding")
    lines = [
        "=" * 44,
        f"  {brand}",
        f"  {v['tieu_de']}",
        "-" * 44,
        f"  {v['phu_de']}",
        f"  Ưu đãi: {v['uu_dai']}",
        "",
        "  Điều kiện áp dụng:",
    ]
    for d in v["dieu_kien"]:
        lines.append(f"    - {d}")
    lines += [
        "",
        f"  Mã voucher : {v['ma']}",
        f"  Phát hành  : {v['phat_hanh']}",
        f"  Hạn dùng   : {v['han']}",
    ]
    if v["ghi_chu"]:
        lines += ["", f"  {v['ghi_chu']}"]
    lines.append("=" * 44)
    return "\n".join(lines)


def card_html(v: dict) -> str:
    e = html.escape
    hotline = fl.cfg("HOTLINE", "")
    dk = "".join(f"<li>{e(d)}</li>" for d in v["dieu_kien"])
    hotline_html = f'<div class="hotline">Hotline: {e(hotline)}</div>' if hotline else ""
    return f"""    <div class="voucher">
      <div class="brand">{e(fl.cfg("BRAND_NAME", "Tony Wedding"))}</div>
      <div class="title">{e(v['tieu_de'])}</div>
      <div class="sub">{e(v['phu_de'])}</div>
      <div class="deal">{e(v['uu_dai'])}</div>
      <ul class="cond">{dk}</ul>
      <div class="code">{e(v['ma'])}</div>
      <div class="meta">Phát hành {e(v['phat_hanh'])} &nbsp;•&nbsp; Hạn dùng {e(v['han'])}</div>
      <div class="note">{e(v['ghi_chu'])}</div>
      {hotline_html}
    </div>"""


def build_html(vouchers: list[dict]) -> str:
    cards = "\n".join(card_html(v) for v in vouchers)
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voucher — {html.escape(fl.cfg("BRAND_NAME", "Tony Wedding"))}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background:#f4ede4;
         margin:0; padding:32px; display:flex; flex-wrap:wrap; gap:24px; justify-content:center; }}
  .voucher {{ width:360px; background:linear-gradient(150deg,#1c1c28,#3a2e4d);
              color:#f5efe6; border-radius:18px; padding:28px 26px; box-sizing:border-box;
              box-shadow:0 10px 30px rgba(0,0,0,.25); position:relative; overflow:hidden; }}
  .voucher::after {{ content:""; position:absolute; right:-40px; top:-40px; width:120px; height:120px;
                     background:rgba(212,175,110,.18); border-radius:50%; }}
  .brand {{ font-size:12px; letter-spacing:3px; text-transform:uppercase; color:#d4af6e; }}
  .title {{ font-size:26px; font-weight:800; margin:10px 0 4px; line-height:1.2; }}
  .sub {{ font-size:13px; color:#cbb8d6; margin-bottom:16px; }}
  .deal {{ font-size:15px; background:rgba(255,255,255,.08); padding:10px 12px; border-radius:10px; }}
  .cond {{ font-size:12.5px; color:#d8cfd9; padding-left:18px; margin:14px 0; line-height:1.6; }}
  .code {{ font-family: "SF Mono", Menlo, monospace; font-size:22px; font-weight:700;
           letter-spacing:2px; color:#1c1c28; background:#d4af6e; text-align:center;
           padding:10px; border-radius:10px; margin:8px 0; }}
  .meta {{ font-size:11.5px; color:#b9a9c4; text-align:center; }}
  .note {{ font-size:12.5px; margin-top:12px; text-align:center; font-style:italic; color:#efe7d6; }}
  .hotline {{ font-size:12px; margin-top:8px; text-align:center; color:#d4af6e; }}
</style>
</head>
<body>
{cards}
</body>
</html>
"""


def read_requests_file() -> list[str]:
    """Đọc yêu cầu hàng loạt từ CSV; fallback file _example khi chưa có file thật."""
    real = HERE / "voucher_maker.csv"
    example = HERE / "voucher_maker_example.csv"
    path = real if real.exists() else example
    if not path.exists():
        return []
    import csv
    reqs = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            def _clean(v):
                if isinstance(v, list):
                    v = ",".join(x for x in v if x)
                return (v or "").strip()
            row = {(k or "").strip(): _clean(v) for k, v in row.items()}
            yc = row.get("yeu_cau") or row.get("Yêu cầu") or ""
            if yc:
                reqs.append(yc)
    return reqs


def main() -> None:
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        requests = [" ".join(args)]
    else:
        requests = read_requests_file()
        if not requests:
            print('Dùng: ./run.sh "Giảm 20% chụp cưới tháng 8"')
            print("Hoặc tạo voucher_maker.csv (cột yeu_cau) để chạy hàng loạt.")
            return
        print(f"[i] Không có yêu cầu ở dòng lệnh — dùng {len(requests)} yêu cầu mẫu từ CSV.")

    vouchers = [compose(r) for r in requests]

    for v in vouchers:
        print(as_text(v))
        print()

    out = HERE / fl.cfg("OUTPUT_HTML", "voucher.html")
    out.write_text(build_html(vouchers), encoding="utf-8")
    print(f"Đã xuất {len(vouchers)} voucher ra: {out}")
    if dry:
        print("(--dry-run) Không gửi đi đâu cả — chỉ tạo file HTML và in nội dung.")


if __name__ == "__main__":
    main()
