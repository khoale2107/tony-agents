#!/usr/bin/env python3
"""
Content Hunter — quét TikTok/YouTube trong ngách, tìm FORMAT đang viral.
Đọc videos.csv (bản export: Nền tảng | Tiêu đề | View | Like | Link),
AI rút ra format/hook đang lên + cách áp dụng cho ngành của bạn.

Quét thật để mở rộng nguồn là 1 seam (collector_example.py): copy -> collector.py,
nhờ Claude Code viết bộ thu theo API/công cụ của bạn -> ghi ra videos.csv.

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
    real = HERE / "videos.csv"
    path = real if real.exists() else HERE / "videos_example.csv"
    if not path.exists():
        raise SystemExit("Không thấy videos.csv (hay videos_example.csv). Cần bản export video.")
    if path.name.endswith("_example.csv"):
        print("[i] Chưa có videos.csv — đang dùng videos_example.csv để chạy thử.")
    import csv
    raw = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(raw.splitlines())
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def rank_videos(rows: list[dict]) -> list[dict]:
    """Xếp theo mức tương tác (view + trọng số like) để AI ưu tiên bài mạnh."""
    out = []
    for r in rows:
        view = fl.parse_amount(r.get("View", "0"))
        like = fl.parse_amount(r.get("Like", "0"))
        out.append({
            "nen_tang": r.get("Nền tảng", "?"),
            "tieu_de": r.get("Tiêu đề", ""),
            "view": view,
            "like": like,
            "link": r.get("Link", ""),
            "diem": view + like * 5,  # like hiếm hơn view nên trọng số cao
        })
    return sorted(out, key=lambda x: -x["diem"])


def analyze(videos: list[dict]) -> str:
    nganh = fl.cfg("NGANH_HANG", "chụp ảnh - quay phim cưới")
    topn = int(fl.cfg("TOP_N_PHAN_TICH", "15"))
    sample = videos[:topn]
    payload = json.dumps(
        [{"nen_tang": v["nen_tang"], "tieu_de": v["tieu_de"],
          "view": int(v["view"]), "like": int(v["like"])} for v in sample],
        ensure_ascii=False,
    )
    prompt = (
        f"Bạn là chuyên gia content viral. Dưới đây là {len(sample)} video đang hút "
        f"tương tác trong ngách, dạng JSON [{{nen_tang, tieu_de, view, like}}]:\n{payload}\n\n"
        f"Ngành của tôi: {nganh}.\n"
        "Hãy phân tích và trả lời NGẮN GỌN, có cấu trúc bằng tiếng Việt:\n"
        "1) 3-5 FORMAT/HOOK đang viral (đặt tên format + mô tả 1 dòng vì sao nó ăn).\n"
        "2) Với mỗi format, gợi ý 1 ý tưởng áp dụng CỤ THỂ cho ngành của tôi (1 câu).\n"
        "3) 3 tiêu đề/hook mẫu tôi có thể quay ngay.\n"
        "Không lan man, không mở bài. Dùng gạch đầu dòng."
    )
    return fl.ask_ai(prompt).strip()


def build_report(videos: list[dict], insight: str) -> str:
    company = fl.cfg("COMPANY_NAME", "Kênh của tôi")
    show = int(fl.cfg("TOP_N_HIEN", "5"))
    lines = [f"<b>🔥 CONTENT HUNTER — {company}</b>",
             f"<i>Quét {len(videos)} video · top {min(show, len(videos))} bài mạnh nhất</i>", ""]
    for v in videos[:show]:
        v_txt = f"{int(v['view']):,}".replace(",", ".")
        l_txt = f"{int(v['like']):,}".replace(",", ".")
        link = f"\n  {v['link']}" if v["link"] else ""
        lines.append(f"• [{v['nen_tang']}] {v['tieu_de']}\n  👁 {v_txt} · ❤️ {l_txt}{link}")
    lines += ["", "<b>💡 FORMAT VIRAL & CÁCH ÁP DỤNG</b>", insight]
    return "\n".join(lines)


def main() -> None:
    videos = rank_videos(read_rows())
    if not videos:
        print("Không có video nào trong file.")
        return
    insight = analyze(videos)
    report = build_report(videos, insight)
    if "--dry-run" in sys.argv:
        for tag in ("<b>", "</b>", "<i>", "</i>"):
            report = report.replace(tag, "")
        print(report)
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo format viral qua Telegram.")


if __name__ == "__main__":
    main()
