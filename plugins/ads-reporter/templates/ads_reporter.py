"""
Báo cáo Meta/TikTok Ads về Telegram mỗi sáng.

Đọc ads.csv (Ngày, Kênh, Chiến dịch, Chi phí, Hiển thị, Click, Lead).
Tính tổng chi và CPM, CPC, CPL cho từng kênh và từng chiến dịch;
AI nhận định chiến dịch nào hiệu quả nên tăng ngân sách, cái nào nên tắt.
Gửi Telegram hoặc in ra màn hình.
Chưa có ads.csv thật thì tự dùng ads_example.csv để chạy thử.

  python3 ads_reporter.py --dry-run   in ra màn hình
  python3 ads_reporter.py             gửi Telegram
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")


def read_rows() -> list[dict]:
    """Đọc ads.csv; chưa có thì fallback ads_example.csv."""
    real = HERE / fl.cfg("ADS_FILE", "ads.csv")
    path = real if real.exists() else (HERE / "ads_example.csv")
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _metrics(cost: float, impr: float, click: float, lead: float) -> dict:
    return {
        "cost": cost,
        "impr": impr,
        "click": click,
        "lead": lead,
        "cpm": (cost / impr * 1000) if impr else 0.0,
        "cpc": (cost / click) if click else 0.0,
        "cpl": (cost / lead) if lead else 0.0,
        "ctr": (click / impr * 100) if impr else 0.0,
    }


def aggregate(rows: list[dict], key_cols: list[str]) -> list[dict]:
    """Gộp các dòng theo (các) cột khóa rồi tính chỉ số."""
    col_cost = fl.cfg("COL_COST", "Chi phí")
    col_impr = fl.cfg("COL_IMPR", "Hiển thị")
    col_click = fl.cfg("COL_CLICK", "Click")
    col_lead = fl.cfg("COL_LEAD", "Lead")
    buckets: dict = {}
    for r in rows:
        label = " · ".join((r.get(c) or "").strip() for c in key_cols).strip(" ·")
        if not label:
            continue
        b = buckets.setdefault(label, {"cost": 0.0, "impr": 0.0, "click": 0.0, "lead": 0.0})
        b["cost"] += fl.parse_amount(r.get(col_cost, ""))
        b["impr"] += fl.parse_amount(r.get(col_impr, ""))
        b["click"] += fl.parse_amount(r.get(col_click, ""))
        b["lead"] += fl.parse_amount(r.get(col_lead, ""))
    out = []
    for label, b in buckets.items():
        m = _metrics(b["cost"], b["impr"], b["click"], b["lead"])
        m["label"] = label
        out.append(m)
    out.sort(key=lambda x: x["cost"], reverse=True)
    return out


def _fmt_cpl(cpl: float, lead: float) -> str:
    if lead <= 0:
        return "— (0 lead)"
    return fl.fmt_vnd(cpl)


def build_report(channels: list[dict], camps: list[dict], commentary: str) -> str:
    brand = fl.cfg("BRAND_NAME", "Tony Wedding")
    tot_cost = sum(c["cost"] for c in channels)
    tot_lead = sum(c["lead"] for c in channels)
    tot_click = sum(c["click"] for c in channels)
    avg_cpl = (tot_cost / tot_lead) if tot_lead else 0.0
    lines = [
        f"<b>📣 BÁO CÁO ADS — {brand}</b>",
        f"<i>{date.today().strftime('%d/%m/%Y')}</i>",
        "",
        f"Tổng chi: <b>{fl.fmt_vnd(tot_cost)}</b> · "
        f"Lead: <b>{tot_lead:.0f}</b> · CPL TB: <b>{_fmt_cpl(avg_cpl, tot_lead)}</b>",
        "",
        "<b>Theo kênh:</b>",
    ]
    for c in channels:
        lines.append(
            f"• <b>{c['label']}</b>: chi {fl.fmt_vnd(c['cost'])} · "
            f"CPM {fl.fmt_vnd(c['cpm'])} · CPC {fl.fmt_vnd(c['cpc'])} · "
            f"CPL {_fmt_cpl(c['cpl'], c['lead'])} · {c['lead']:.0f} lead"
        )
    lines += ["", "<b>Theo chiến dịch:</b>"]
    for c in camps:
        lines.append(
            f"• <b>{c['label']}</b>: chi {fl.fmt_vnd(c['cost'])} · "
            f"CPC {fl.fmt_vnd(c['cpc'])} · CPL {_fmt_cpl(c['cpl'], c['lead'])} · "
            f"CTR {c['ctr']:.1f}% · {c['lead']:.0f} lead"
        )
    lines += ["", "<b>🧠 Nhận định AI:</b>", commentary]
    return "\n".join(lines)


def strip_html(text: str) -> str:
    for tag in ("<b>", "</b>", "<i>", "</i>"):
        text = text.replace(tag, "")
    return text


def main() -> None:
    col_channel = fl.cfg("COL_CHANNEL", "Kênh")
    col_camp = fl.cfg("COL_CAMPAIGN", "Chiến dịch")
    rows = read_rows()
    channels = aggregate(rows, [col_channel])
    camps = aggregate(rows, [col_channel, col_camp])
    if not channels:
        print("Không có dữ liệu Ads để xử lý.")
        return

    camp_txt = "; ".join(
        f"{c['label']}: chi {fl.fmt_vnd(c['cost'])}, "
        f"{c['lead']:.0f} lead, CPL {_fmt_cpl(c['cpl'], c['lead'])}, "
        f"CPC {fl.fmt_vnd(c['cpc'])}, CTR {c['ctr']:.1f}%"
        for c in camps
    )
    prompt = (
        f"Bạn là chuyên viên chạy quảng cáo (Meta/TikTok Ads) cho {fl.cfg('BRAND_NAME', 'thương hiệu')}. "
        f"Số liệu hôm nay theo từng chiến dịch: {camp_txt}. "
        "CPL = chi phí trên mỗi lead (càng thấp càng tốt). "
        "Viết nhận định ngắn (tối đa 5 câu, tiếng Việt): nêu tên chiến dịch nào đang hiệu quả "
        "(CPL thấp, nhiều lead) nên tăng ngân sách; chiến dịch nào kém (CPL quá cao hoặc tốn chi mà 0 lead) "
        "nên tắt hoặc sửa; và 1 hành động cụ thể cho hôm nay. "
        "Không liệt kê lại toàn bộ số. Chỉ trả về đoạn nhận định."
    )
    report = build_report(channels, camps, fl.ask_ai(prompt))
    if "--dry-run" in sys.argv:
        print(strip_html(report))
        return
    fl.send_telegram(report)
    print("Đã gửi báo cáo Ads qua Telegram.")


if __name__ == "__main__":
    main()
