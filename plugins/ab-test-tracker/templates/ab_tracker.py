#!/usr/bin/env python3
"""
A/B Test Tracker — theo dõi hiệu quả creative theo biến thể.

Đọc ab.csv (Nhóm,Biến thể,Hiển thị,Click,Chuyển đổi). Với mỗi biến thể tính
CTR (Click/Hiển thị) và CVR (Chuyển đổi/Click). Mỗi Nhóm chọn 1 biến thể WINNER
theo chỉ số ưu tiên (mặc định CVR). AI nhận định nên nhân bản cái nào, cắt cái
nào. Gửi Telegram hoặc in màn hình.

  ./run.sh --dry-run   in ra màn hình (không gửi)
  ./run.sh             gửi báo cáo Telegram
Dùng GÓI Claude Code, không cần API key.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_rows() -> list[dict]:
    p = HERE / "ab.csv"
    if not p.exists():
        p = HERE / "ab_example.csv"
        print("[i] Chưa có ab.csv — đang dùng ab_example.csv để chạy thử.")
    return list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))


def _num(x) -> float:
    return fl.parse_amount(x)


def compute(rows: list[dict]) -> list[dict]:
    col_group = fl.cfg("COL_GROUP", "Nhóm")
    col_var = fl.cfg("COL_VARIANT", "Biến thể")
    col_imp = fl.cfg("COL_IMPRESSION", "Hiển thị")
    col_click = fl.cfg("COL_CLICK", "Click")
    col_conv = fl.cfg("COL_CONVERSION", "Chuyển đổi")

    out = []
    for r in rows:
        imp = _num(r.get(col_imp, ""))
        clk = _num(r.get(col_click, ""))
        cvn = _num(r.get(col_conv, ""))
        ctr = (clk / imp) if imp else 0.0
        cvr = (cvn / clk) if clk else 0.0
        # tỉ lệ chuyển đổi trên tổng hiển thị (dùng để tie-break / tham khảo)
        conv_rate = (cvn / imp) if imp else 0.0
        out.append({
            "group": (r.get(col_group, "") or "Khác").strip() or "Khác",
            "variant": (r.get(col_var, "") or "?").strip() or "?",
            "imp": imp, "click": clk, "conv": cvn,
            "ctr": ctr, "cvr": cvr, "conv_rate": conv_rate,
        })
    return out


def pick_winners(items: list[dict]) -> dict:
    """Trả về dict: group -> {'items': [...], 'winner': variant_name}."""
    metric = fl.cfg("WINNER_METRIC", "cvr").lower()  # cvr | ctr | conv_rate
    min_imp = int(_num(fl.cfg("MIN_IMPRESSION", "0")))
    groups: dict = {}
    for it in items:
        groups.setdefault(it["group"], []).append(it)

    result = {}
    for g, its in groups.items():
        eligible = [x for x in its if x["imp"] >= min_imp] or its
        key = metric if metric in ("cvr", "ctr", "conv_rate") else "cvr"
        best = max(eligible, key=lambda x: (x[key], x["conv_rate"], x["ctr"]))
        ordered = sorted(its, key=lambda x: -x[key])
        result[g] = {"items": ordered, "winner": best["variant"], "metric": key}
    return result


def _pct(x: float) -> str:
    return f"{x*100:.2f}%"


def build_report(result: dict) -> str:
    campaign = fl.cfg("CAMPAIGN_NAME", "Chiến dịch")
    metric_label = {"cvr": "CVR", "ctr": "CTR", "conv_rate": "CR/hiển thị"}
    lines = [f"<b>🧪 A/B TEST — {campaign}</b>", ""]
    for g in sorted(result.keys()):
        blk = result[g]
        ml = metric_label.get(blk["metric"], blk["metric"].upper())
        lines.append(f"<b>▸ Nhóm {g}</b> <i>(winner theo {ml})</i>")
        for it in blk["items"]:
            crown = " 🏆" if it["variant"] == blk["winner"] else ""
            lines.append(
                f"  • <b>{it['variant']}</b>{crown} — "
                f"CTR {_pct(it['ctr'])}, CVR {_pct(it['cvr'])} "
                f"({it['conv']:.0f} CĐ / {it['click']:.0f} click / {it['imp']:.0f} hiển thị)"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def build_ai_prompt(result: dict) -> str:
    detail_lines = []
    for g in sorted(result.keys()):
        blk = result[g]
        detail_lines.append(f"Nhóm {g} (winner: {blk['winner']}):")
        for it in blk["items"]:
            detail_lines.append(
                f"  - {it['variant']}: CTR {_pct(it['ctr'])}, CVR {_pct(it['cvr'])}, "
                f"{it['conv']:.0f} chuyển đổi / {it['click']:.0f} click / {it['imp']:.0f} hiển thị"
            )
    detail = "\n".join(detail_lines)
    return (
        f"Bạn là chuyên viên tối ưu quảng cáo của {fl.cfg('CAMPAIGN_NAME','chiến dịch')}. "
        f"Kết quả A/B test các creative:\n{detail}\n\n"
        "Viết nhận định ngắn (tối đa 5 câu, tiếng Việt): mỗi nhóm nên NHÂN BẢN biến thể nào, "
        "CẮT biến thể nào, và lưu ý nếu mẫu còn quá nhỏ chưa nên kết luận. "
        "Không lặp lại nguyên số đã liệt kê. Chỉ trả về đoạn nhận định."
    )


def main() -> None:
    rows = read_rows()
    items = compute(rows)
    if not items:
        print("Không có dữ liệu trong ab.csv / ab_example.csv.")
        return
    result = pick_winners(items)
    report = build_report(result)
    commentary = fl.ask_ai(build_ai_prompt(result))
    full = report + "\n\n<b>🧠 Nhận định:</b>\n" + commentary

    if "--dry-run" in sys.argv:
        plain = (full.replace("<b>", "").replace("</b>", "")
                     .replace("<i>", "").replace("</i>", ""))
        print(plain)
        return
    fl.send_telegram(full)
    print("Đã gửi báo cáo A/B test qua Telegram.")


if __name__ == "__main__":
    main()
