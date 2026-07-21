#!/usr/bin/env python3
"""
Lead Hunter — quét bài/bình luận từ group, fanpage (bản export) và
CHẤM ĐIỂM khách tiềm năng, xếp hạng. Gửi Telegram top khách.

Đọc export.csv (cột: Nguồn | Người | Nội dung | Link). Việc quét thật là 1 seam
(collector_example.py) — bạn/Claude Code nối tuỳ nền tảng; ở đây xử lý file export.

  ./run.sh --dry-run   |   ./run.sh
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_rows() -> list[dict]:
    p = HERE / "export.csv"
    if not p.exists():
        p = HERE / "export_example.csv"
    import csv
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def score_leads(rows: list[dict]) -> list[dict]:
    nganh = fl.cfg("NGANH_HANG", "chụp ảnh - quay phim cưới")
    items = [{"i": i, "nguoi": r.get("Người", "?"), "noi_dung": r.get("Nội dung", ""),
              "nguon": r.get("Nguồn", ""), "link": r.get("Link", "")}
             for i, r in enumerate(rows)]
    payload = json.dumps([{"i": it["i"], "noi_dung": it["noi_dung"]} for it in items],
                         ensure_ascii=False)
    prompt = (
        f"Bạn lọc khách tiềm năng cho ngành: {nganh}. Dưới đây là danh sách bình luận/bài đăng "
        "dạng JSON [{i, noi_dung}]. Với MỖI mục, chấm điểm tiềm năng 0-100 và lý do ngắn "
        "(đang có nhu cầu/hỏi giá/đúng thời điểm = điểm cao; rao bán/spam/không liên quan = điểm thấp). "
        'CHỈ trả về JSON mảng [{"i":số,"diem":số,"ly_do":"..."}], không thêm chữ nào khác.\n\n'
        f"{payload}"
    )
    raw = fl.ask_ai(prompt)
    scored = {}
    try:
        start, end = raw.find("["), raw.rfind("]")
        for o in json.loads(raw[start:end + 1]):
            scored[int(o["i"])] = (int(o.get("diem", 0)), str(o.get("ly_do", "")))
    except Exception:
        print("[!] AI trả về không đúng JSON, xếp hạng tạm bằng độ dài nội dung.")
    out = []
    for it in items:
        diem, ly_do = scored.get(it["i"], (len(it["noi_dung"]) % 50, "chưa chấm được"))
        out.append({**it, "diem": diem, "ly_do": ly_do})
    return sorted(out, key=lambda x: -x["diem"])


def build_report(leads: list[dict]) -> str:
    topn = int(fl.cfg("TOP_N", "10"))
    minscore = int(fl.cfg("MIN_SCORE", "50"))
    hot = [l for l in leads if l["diem"] >= minscore][:topn]
    lines = [f"<b>🎯 LEAD HUNTER — {fl.cfg('COMPANY_NAME','Công ty')}</b>",
             f"<i>Quét {len(leads)} mục · {len(hot)} khách đáng theo (≥{minscore}đ)</i>", ""]
    if not hot:
        lines.append("(Chưa có khách đủ điểm. Thử hạ MIN_SCORE hoặc thêm nguồn.)")
    for l in hot:
        link = f" — {l['link']}" if l["link"] else ""
        lines.append(f"<b>{l['diem']}đ</b> · {l['nguoi']} ({l['nguon']})\n"
                     f"  {l['ly_do']}{link}")
    return "\n".join(lines)


def main() -> None:
    leads = score_leads(read_rows())
    report = build_report(leads)
    if "--dry-run" in sys.argv:
        print(report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
        return
    fl.send_telegram(report)
    print("Đã gửi danh sách lead tiềm năng qua Telegram.")


if __name__ == "__main__":
    main()
