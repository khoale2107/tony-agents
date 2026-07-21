#!/usr/bin/env python3
"""
Reply/DM automation cho TikTok/Facebook — phân loại comment/DM và soạn
câu trả lời theo tông từng nền tảng.

Đọc inbox.csv (cột: Nền tảng | Người dùng | Nội dung).
Phân loại (hỏi giá / khen / chê / hỏi thông tin / spam) và soạn trả lời.
Gửi qua connector (seam). Dùng GÓI Claude Code cho phần soạn.

  ./run.sh --dry-run   |   ./run.sh
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_inbox() -> list[dict]:
    p = HERE / "inbox.csv"
    if not p.exists():
        p = HERE / "inbox_example.csv"
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def load_knowledge() -> str:
    for name in ("knowledge.md", "knowledge_example.md"):
        p = HERE / name
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    return ""


def process(rows: list[dict]) -> list[dict]:
    ct = fl.cfg("COMPANY_NAME", "công ty")
    kb = load_knowledge()
    payload = json.dumps([{"i": i, "nen_tang": r.get("Nền tảng", ""),
                           "noi_dung": r.get("Nội dung", "")} for i, r in enumerate(rows)],
                         ensure_ascii=False)
    prompt = (
        f"Bạn quản lý kênh social của {ct}. Dưới đây là các comment/DM dạng JSON [{{i,nen_tang,noi_dung}}].\n"
        + (f"KIẾN THỨC để trả lời (chỉ dùng cái này, không bịa giá):\n{kb}\n\n" if kb else "")
        + "Với MỖI mục: phân loại vào 1 trong [hỏi giá, khen, chê, hỏi thông tin, spam] và soạn 1 câu trả lời "
        "hợp tông nền tảng (TikTok trẻ trung, Facebook lịch sự). Nếu spam thì reply để trống. "
        "Nếu cần báo giá mà kiến thức không có thì mời khách inbox/để lại SĐT.\n"
        'CHỈ trả về JSON [{"i":số,"loai":"...","reply":"..."}], không thêm gì khác.\n\n'
        f"{payload}"
    )
    raw = fl.ask_ai(prompt)
    parsed = {}
    try:
        s, e = raw.find("["), raw.rfind("]")
        for o in json.loads(raw[s:e + 1]):
            parsed[int(o["i"])] = (o.get("loai", "?"), o.get("reply", ""))
    except Exception:
        print("[!] AI trả về không đúng JSON.")
    out = []
    for i, r in enumerate(rows):
        loai, reply = parsed.get(i, ("?", ""))
        out.append({**r, "loai": loai, "reply": reply})
    return out


def main() -> None:
    results = process(read_inbox())
    dry = "--dry-run" in sys.argv
    conn = None
    if not dry:
        try:
            import connector as conn  # noqa
        except ImportError:
            raise SystemExit("Chưa có connector.py. Nhờ Claude Code viết (xem connector_example.py).")
    sent = 0
    for r in results:
        head = f"[{r.get('Nền tảng','')}·{r['loai']}] {r.get('Người dùng','')}: {r.get('Nội dung','')}"
        if not r["reply"]:
            print(f"{head}\n  → (bỏ qua)\n"); continue
        if dry:
            print(f"{head}\n  → {r['reply']}\n")
        else:
            conn.reply(r.get("Nền tảng", ""), r.get("Người dùng", ""), r["reply"])
        sent += 1
    print(f"[i] {sent} câu trả lời " + ("(dry-run, chưa gửi)." if dry else "đã gửi."))


if __name__ == "__main__":
    main()
