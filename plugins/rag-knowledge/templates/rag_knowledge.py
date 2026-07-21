#!/usr/bin/env python3
"""
RAG kiến thức công ty — bot trả lời dựa trên tài liệu riêng của bạn
(bảng giá, chính sách, quy trình...) và CÓ TRÍCH NGUỒN.

  ./run.sh "gói chụp phóng sự cưới bao nhiêu tiền?"
  ./run.sh                       # hỏi tương tác nhiều câu

Đặt tài liệu (.md/.txt) vào thư mục ./knowledge. Có sẵn ví dụ để test ngay.
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

MAX_CHARS = int(fl.cfg("MAX_CONTEXT_CHARS", "20000"))


def load_docs() -> list[tuple[str, str]]:
    folder = HERE / fl.cfg("KNOWLEDGE_DIR", "knowledge")
    if not folder.exists():
        folder = HERE / "knowledge_example"
    docs = []
    for p in sorted(folder.glob("**/*")):
        if p.suffix.lower() in (".md", ".txt") and p.is_file():
            docs.append((p.name, p.read_text(encoding="utf-8").strip()))
    return docs


def build_context(docs: list[tuple[str, str]]) -> str:
    parts, total = [], 0
    for name, body in docs:
        block = f"### NGUỒN: {name}\n{body}\n"
        if total + len(block) > MAX_CHARS:
            block = block[: MAX_CHARS - total]
        parts.append(block)
        total += len(block)
        if total >= MAX_CHARS:
            break
    return "\n".join(parts)


def answer(question: str, context: str) -> str:
    company = fl.cfg("COMPANY_NAME", "công ty")
    prompt = (
        f"Bạn là trợ lý kiến thức nội bộ của {company}. Chỉ được dùng THÔNG TIN "
        "trong phần TÀI LIỆU dưới đây để trả lời, tuyệt đối KHÔNG bịa. Nếu tài liệu "
        "không có thông tin, hãy nói thẳng là chưa có và đề nghị hỏi người phụ trách.\n"
        "Trả lời ngắn gọn bằng tiếng Việt, cuối câu ghi (Nguồn: <tên file>).\n\n"
        f"=== TÀI LIỆU ===\n{context}\n=== HẾT ===\n\n"
        f"Câu hỏi: {question}"
    )
    return fl.ask_ai(prompt)


def main() -> None:
    docs = load_docs()
    if not docs:
        print("[!] Chưa có tài liệu trong ./knowledge. Thêm file .md/.txt rồi chạy lại.")
        return
    context = build_context(docs)
    print(f"[i] Đã nạp {len(docs)} tài liệu: {', '.join(n for n, _ in docs)}\n")

    q = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip()
    if q:
        print(answer(q, context))
        return
    print("Gõ câu hỏi (Enter trống để thoát):")
    while True:
        try:
            q = input("\n❓ ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        print("\n💬 " + answer(q, context))


if __name__ == "__main__":
    main()
