#!/usr/bin/env python3
"""
Trợ lý tổng (router) — hỏi gì chỉ đúng agent đó.

Đọc danh mục agent đã cài (agents.csv: Tên agent,Lệnh,Mô tả), rồi nhờ AI
đọc câu hỏi của bạn và chỉ ra NÊN dùng agent/lệnh nào + hướng dẫn ngắn.

  ./run.sh "sáng nay có lead nào mới không?"
  ./run.sh "làm báo cáo doanh thu tháng"
  ./run.sh --dry-run "gửi tin nhắn Zalo cho khách"   # giống nhau: in ra màn hình
  ./run.sh --list                                     # xem danh mục agent đã cài

Không gửi Telegram — đây là công cụ hỏi/đáp, kết quả in thẳng ra màn hình.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_catalog() -> list[dict]:
    """Đọc danh mục agent đã cài. Ưu tiên agents.csv thật, chưa có thì dùng
    agents_example.csv để chạy thử ngay."""
    real = HERE / "agents.csv"
    path = real if real.exists() else HERE / "agents_example.csv"
    if not path.exists():
        raise SystemExit(
            "Không tìm thấy agents.csv (hoặc agents_example.csv) trong thư mục này."
        )
    if path.name.endswith("_example.csv"):
        print("[i] Chưa có agents.csv — đang dùng agents_example.csv để chạy thử.")

    c_name = fl.cfg("COL_NAME", "Tên agent")
    c_cmd = fl.cfg("COL_CMD", "Lệnh")
    c_desc = fl.cfg("COL_DESC", "Mô tả")

    rows: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            clean = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            name = clean.get(c_name, "")
            if not name:
                continue
            rows.append({
                "name": name,
                "cmd": clean.get(c_cmd, ""),
                "desc": clean.get(c_desc, ""),
            })
    if not rows:
        raise SystemExit(f"Danh mục {path.name} trống hoặc sai tên cột "
                         f"(cần: {c_name}, {c_cmd}, {c_desc}).")
    return rows


def catalog_text(catalog: list[dict]) -> str:
    lines = []
    for i, a in enumerate(catalog, 1):
        cmd = f" (lệnh {a['cmd']})" if a["cmd"] else ""
        lines.append(f"{i}. {a['name']}{cmd}\n   {a['desc']}")
    return "\n".join(lines)


def build_prompt(question: str, catalog: list[dict]) -> str:
    company = fl.cfg("COMPANY_NAME", "doanh nghiệp")
    return (
        f"Bạn là trợ lý điều phối của {company}. Công ty đã cài sẵn các 'AI Agent' "
        f"dưới đây, mỗi agent lo một việc:\n\n"
        f"{catalog_text(catalog)}\n\n"
        f"Người dùng hỏi: \"{question}\"\n\n"
        "Nhiệm vụ: chọn 1 (tối đa 2) agent PHÙ HỢP NHẤT để xử lý yêu cầu này. "
        "Trả lời bằng tiếng Việt, thật ngắn gọn theo mẫu:\n"
        "• Nên dùng: <tên agent> — <lệnh>\n"
        "• Vì hợp: <một câu>\n"
        "• Làm ngay: <1-2 bước cụ thể để mở/chạy agent đó>\n"
        "Nếu KHÔNG agent nào trong danh mục hợp, nói thẳng 'Chưa có agent phù hợp' "
        "và gợi ý ngắn cần thêm agent kiểu gì. Chỉ trả về nội dung, không markdown thừa, "
        "không bịa ra agent ngoài danh mục."
    )


def print_list(catalog: list[dict]) -> None:
    print(f"Danh mục agent đã cài ({len(catalog)}):\n")
    print(catalog_text(catalog))


def get_question(argv: list[str]) -> str:
    parts = [a for a in argv if not a.startswith("-")]
    return " ".join(parts).strip()


def main() -> None:
    argv = sys.argv[1:]
    catalog = read_catalog()

    if "--list" in argv:
        print_list(catalog)
        return

    question = get_question(argv)
    if not question:
        print("Cách dùng: ./run.sh \"câu hỏi của bạn\"")
        print("           ./run.sh --list   (xem danh mục agent)\n")
        print_list(catalog)
        return

    answer = fl.ask_ai(build_prompt(question, catalog))
    print(f"❓ Hỏi: {question}\n")
    print(answer)


if __name__ == "__main__":
    main()
