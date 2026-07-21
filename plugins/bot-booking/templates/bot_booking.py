#!/usr/bin/env python3
"""
Bot booking — đọc tin nhắn khách, hiểu nhu cầu, xem lịch trống và soạn
BÁO GIÁ + XÁC NHẬN ĐẶT LỊCH nhanh.

  ./run.sh "cho mình hỏi chụp cưới thứ 7 tuần này còn trống không, giá sao?"

Bảng giá đọc từ ./pricing.md; lịch trống đọc từ ./slots.csv (Ngày,Giờ,Trạng thái).
Có sẵn ví dụ để test ngay. Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def load_pricing() -> str:
    for name in (fl.cfg("PRICING_FILE", "pricing.md"), "pricing_example.md"):
        p = HERE / name
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    return "(chưa có bảng giá)"


def load_slots() -> str:
    for name in ("slots.csv", "slots_example.csv"):
        p = HERE / name
        if not p.exists():
            continue
        rows = list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))
        free = [r for r in rows if "trống" in (r.get("Trạng thái", "").lower())]
        if not free:
            return "(hiện không còn lịch trống trong danh sách)"
        return "\n".join(f"- {r.get('Ngày','')} {r.get('Giờ','')}" for r in free)
    return "(chưa có dữ liệu lịch)"


def main() -> None:
    msg = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip()
    if not msg:
        print('Cách dùng: ./run.sh "tin nhắn của khách"')
        return
    company = fl.cfg("COMPANY_NAME", "công ty")
    prompt = (
        f"Bạn là lễ tân đặt lịch của {company}, nhắn tin thân thiện, chuyên nghiệp. "
        "Dựa CHỈ vào BẢNG GIÁ và LỊCH TRỐNG bên dưới để trả lời khách. "
        "Không bịa giá hay lịch không có. Nếu khách muốn ngày đã kín, gợi ý ngày trống gần nhất. "
        "Trả lời gồm: chào hỏi ngắn, báo giá phù hợp nhu cầu, xác nhận lịch còn trống, "
        "và hỏi 1 câu để chốt (tên + số điện thoại đặt cọc giữ ngày). Chỉ trả về nội dung tin nhắn.\n\n"
        f"=== BẢNG GIÁ ===\n{load_pricing()}\n\n"
        f"=== LỊCH TRỐNG ===\n{load_slots()}\n\n"
        f"=== TIN NHẮN KHÁCH ===\n{msg}"
    )
    print("\n💬 Trả lời đề xuất:\n")
    print(fl.ask_ai(prompt))


if __name__ == "__main__":
    main()
