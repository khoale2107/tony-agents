#!/usr/bin/env python3
"""
Comment Insight — biến comment khách thành insight content.
Đọc comments.csv (bản gom comment: Nguồn | Nội dung),
AI gom nhóm mối quan tâm/thắc mắc của khách -> 3-5 insight
+ gợi ý chủ đề content nên làm để trả lời đúng cái khách quan tâm.

  ./run.sh --dry-run   |   ./run.sh
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_rows() -> list[dict]:
    name = fl.cfg("COMMENTS_FILE", "comments.csv")
    real = HERE / name
    path = real if real.exists() else HERE / "comments_example.csv"
    if not path.exists():
        raise SystemExit("Không thấy comments.csv (hay comments_example.csv). Cần bản gom comment khách.")
    if path.name.endswith("_example.csv"):
        print("[i] Chưa có comments.csv — đang dùng comments_example.csv để chạy thử.")
    raw = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(raw.splitlines())
    rows = [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]
    col_src = fl.cfg("COL_SOURCE", "Nguồn")
    col_txt = fl.cfg("COL_CONTENT", "Nội dung")
    out = []
    for r in rows:
        noi_dung = r.get(col_txt, "").strip()
        if not noi_dung:
            continue
        out.append({"nguon": r.get(col_src, "?").strip() or "?", "noi_dung": noi_dung})
    return out


def analyze(comments: list[dict]) -> str:
    nganh = fl.cfg("NGANH_HANG", "chụp ảnh - quay phim cưới")
    payload = json.dumps(
        [{"nguon": c["nguon"], "noi_dung": c["noi_dung"]} for c in comments],
        ensure_ascii=False,
    )
    prompt = (
        f"Bạn là chuyên gia content marketing. Dưới đây là {len(comments)} comment/thắc mắc "
        f"của khách (dạng JSON [{{nguon, noi_dung}}]):\n{payload}\n\n"
        f"Ngành của tôi: {nganh}.\n"
        "Hãy đọc và trả lời NGẮN GỌN, có cấu trúc bằng tiếng Việt:\n"
        "1) 3-5 INSIGHT: gom nhóm những mối quan tâm/thắc mắc/nỗi lo lặp lại của khách "
        "(mỗi insight 1 dòng: tên nhóm + vì sao khách quan tâm).\n"
        "2) Với mỗi insight, gợi ý 1 CHỦ ĐỀ CONTENT nên làm để trả lời đúng cái khách cần (1 câu).\n"
        "3) 3 tiêu đề/hook mẫu có thể quay hoặc viết ngay.\n"
        "Không lan man, không mở bài. Dùng gạch đầu dòng."
    )
    return fl.ask_ai(prompt).strip()


def build_report(comments: list[dict], insight: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Kênh của tôi")
    # đếm comment theo nguồn để sếp thấy nguồn nào nhiều tiếng nói khách
    by_src: dict[str, int] = {}
    for c in comments:
        by_src[c["nguon"]] = by_src.get(c["nguon"], 0) + 1
    top_src = sorted(by_src.items(), key=lambda x: -x[1])
    lines = [f"<b>💬 COMMENT INSIGHT — {company}</b>",
             f"<i>Đã gom {len(comments)} comment khách</i>", ""]
    if top_src:
        src_txt = " · ".join(f"{s}: {n}" for s, n in top_src)
        lines.append(f"<i>Nguồn: {src_txt}</i>")
        lines.append("")
    lines += ["<b>🧭 INSIGHT & CHỦ ĐỀ CONTENT NÊN LÀM</b>", insight]
    return "\n".join(lines)


def main() -> None:
    comments = read_rows()
    if not comments:
        print("Không có comment nào trong file.")
        return
    insight = analyze(comments)
    report = build_report(comments, insight)
    if "--dry-run" in sys.argv:
        for tag in ("<b>", "</b>", "<i>", "</i>"):
            report = report.replace(tag, "")
        print(report)
        return
    fl.send_telegram(report)
    print("Đã gửi insight content qua Telegram.")


if __name__ == "__main__":
    main()
