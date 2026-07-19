#!/usr/bin/env python3
"""
OCR hoá đơn — chụp/đưa ảnh hoá đơn, AI đọc và TỰ GHI SỔ (thêm 1 dòng vào so_ke.csv).

  ./run.sh duong-dan-anh-hoa-don.jpg
  ./run.sh anh1.jpg anh2.png ...        (nhiều ảnh một lượt)

Dùng GÓI Claude Code để đọc ảnh (Claude Code có thể xem ảnh). Không cần API key.
Kết quả ghi vào so_ke.csv cùng thư mục.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")
SOKE = HERE / "so_ke.csv"
HEADERS = ["Ngày", "Nhà cung cấp", "Hạng mục", "Số tiền", "Ảnh nguồn"]


def read_invoice(image_path: str) -> dict | None:
    p = Path(image_path).expanduser().resolve()
    if not p.exists():
        print(f"[!] Không thấy file: {image_path}")
        return None
    claude = fl.find_claude()
    if not claude:
        print("[!] Chưa có Claude Code. Cài + đăng nhập gói (claude login).")
        return None
    prompt = (f"Đọc hoá đơn trong file: {p}\n"
              "Trích thông tin và CHỈ trả về ĐÚNG MỘT DÒNG, các trường ngăn bởi dấu | theo thứ tự:\n"
              "ngày(dd/mm/yyyy)|nhà cung cấp|hạng mục ngắn gọn|tổng tiền(chỉ chữ số)\n"
              "Không thêm giải thích, không markdown. Trường nào không rõ để trống nhưng giữ đủ dấu |.")
    try:
        r = subprocess.run([claude, "-p", prompt, "--allowedTools", "Read"],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        print(f"[!] Lỗi gọi Claude Code: {e}")
        return None
    line = ""
    for ln in (r.stdout or "").splitlines():
        if "|" in ln:
            line = ln.strip()
    if not line:
        print(f"[!] AI không trích được từ {p.name}. Trả về:\n{(r.stdout or r.stderr)[:200]}")
        return None
    parts = [x.strip() for x in line.split("|")]
    parts += [""] * (4 - len(parts))
    return {"Ngày": parts[0], "Nhà cung cấp": parts[1], "Hạng mục": parts[2],
            "Số tiền": str(int(fl.parse_amount(parts[3]))), "Ảnh nguồn": p.name}


def append_row(rec: dict) -> None:
    new = not SOKE.exists()
    with SOKE.open("a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        if new:
            w.writeheader()
        w.writerow(rec)


def main() -> None:
    images = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not images:
        print("Cách dùng: ./run.sh <đường-dẫn-ảnh-hoá-đơn> [ảnh khác...]")
        return
    for img in images:
        print(f"\n📷 Đang đọc: {img} ...")
        rec = read_invoice(img)
        if not rec:
            continue
        append_row(rec)
        print(f"✅ Đã ghi sổ: {rec['Ngày']} | {rec['Nhà cung cấp']} | "
              f"{rec['Hạng mục']} | {fl.fmt_vnd(fl.parse_amount(rec['Số tiền']))}")
    if SOKE.exists():
        print(f"\n📒 Sổ kế toán: {SOKE}")


if __name__ == "__main__":
    main()
