#!/usr/bin/env python3
"""
Trợ lý CSKH — soạn câu trả lời khách hàng dựa trên kiến thức doanh nghiệp.

Cách dùng:
  ./run.sh "Thuê váy cưới bao nhiêu tiền một ngày?"     # trả lời 1 câu
  ./run.sh                                              # chế độ hỏi-đáp liên tục

Trợ lý CHỈ trả lời dựa trên file knowledge.md (kiến thức bạn cung cấp). Nếu câu
hỏi nằm ngoài kiến thức, nó lịch sự đề nghị chuyển tư vấn viên — không bịa.

Mặc định dùng GÓI Claude Code (không cần API key). Cấu hình ở .env (tùy chọn).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


load_env(BASE_DIR / ".env")


def cfg(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def find_claude() -> str:
    override = cfg("CLAUDE_BIN")
    cands = [override] if override else []
    if shutil.which("claude"):
        cands.append(shutil.which("claude"))
    cands += [str(Path.home() / ".local/bin/claude"),
              "/usr/local/bin/claude", "/opt/homebrew/bin/claude"]
    for c in cands:
        if c and Path(c).exists():
            return c
    return ""


def load_knowledge() -> str:
    for name in ("knowledge.md", "knowledge.example.md"):
        p = BASE_DIR / name
        if p.exists():
            if name == "knowledge.example.md":
                print("[i] Chưa có knowledge.md — đang dùng knowledge.example.md (kiến thức mẫu).")
            return p.read_text(encoding="utf-8")
    return "(Chưa có kiến thức nào.)"


def build_prompt(question: str, knowledge: str) -> str:
    company = cfg("COMPANY_NAME", "doanh nghiệp")
    tone = cfg("TONE", "thân thiện, lịch sự, xưng em - gọi anh/chị")
    return f"""Bạn là nhân viên chăm sóc khách hàng của {company}. Giọng điệu: {tone}.

Dưới đây là KIẾN THỨC được phép dùng để trả lời (giá, dịch vụ, chính sách...):
<kien_thuc>
{knowledge}
</kien_thuc>

Khách hỏi: "{question}"

Hãy soạn câu trả lời cho khách. Quy tắc:
- CHỈ dựa trên phần kiến thức ở trên. Tuyệt đối không bịa giá, chính sách hay thông tin không có trong đó.
- Nếu kiến thức không đủ để trả lời, lịch sự nói sẽ chuyển cho tư vấn viên hỗ trợ, và xin thông tin liên hệ.
- Ngắn gọn, đúng trọng tâm, đúng giọng điệu đã nêu. Chỉ trả về nội dung tin nhắn gửi khách, không giải thích thêm."""


def ask_ai(prompt: str) -> str:
    claude_bin = find_claude()
    if claude_bin:
        try:
            r = subprocess.run([claude_bin, "-p", prompt],
                               capture_output=True, text=True, timeout=180)
            out = (r.stdout or "").strip()
            if r.returncode == 0 and out:
                return out
            print(f"[!] Claude Code không ra kết quả (exit {r.returncode}). {(r.stderr or '').strip()[:200]}")
        except Exception as e:
            print(f"[!] Lỗi gọi Claude Code: {e}")

    api_key = cfg("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model=cfg("ANTHROPIC_MODEL", "claude-opus-4-8"),
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            txt = "\n".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
            if txt:
                return txt
        except ImportError:
            print("[!] Chế độ API cần: pip install anthropic")
        except Exception as e:
            print(f"[!] Lỗi gọi API: {e}")

    return ("(Chưa dùng được AI. Cần cài Claude Code + đăng nhập gói — khuyến nghị, "
            "hoặc điền ANTHROPIC_API_KEY vào .env.)")


def answer(question: str, knowledge: str) -> str:
    return ask_ai(build_prompt(question, knowledge))


def main() -> None:
    knowledge = load_knowledge()
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if args:  # chế độ 1 câu
        q = " ".join(args)
        print(f"\n👤 Khách: {q}\n")
        print(f"💬 Trả lời:\n{answer(q, knowledge)}\n")
        return

    # chế độ hỏi-đáp liên tục
    print("=== Trợ lý CSKH — gõ câu hỏi của khách, Enter để trả lời. Gõ 'thoat' để dừng. ===")
    while True:
        try:
            q = input("\n👤 Khách: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt!")
            break
        if not q:
            continue
        if q.lower() in ("thoat", "thoát", "exit", "quit"):
            print("Tạm biệt!")
            break
        print(f"\n💬 Trả lời:\n{answer(q, knowledge)}")


if __name__ == "__main__":
    main()
