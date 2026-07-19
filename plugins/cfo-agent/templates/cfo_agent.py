#!/usr/bin/env python3
"""
CFO Agent — Báo cáo tài chính tự động.

Luồng:
  1. Đọc dữ liệu doanh thu / chi phí từ Google Sheet (link CSV export).
  2. Tính doanh thu, chi phí, lợi nhuận cho kỳ báo cáo (ngày hoặc tháng).
  3. Nhờ Claude viết nhận định ngắn gọn kiểu CFO.
  4. Gửi báo cáo qua Telegram.

Chạy tay:   python cfo_agent.py
Chạy thử (không gửi Telegram, in ra màn hình):  python cfo_agent.py --dry-run

Mọi cấu hình đọc từ file .env cùng thư mục. KHÔNG có key/token nào nằm trong code này.
"""

import csv
import io
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Đọc cấu hình từ .env (không cần thư viện ngoài)
# ---------------------------------------------------------------------------

def load_env(path: Path) -> None:
    """Nạp các biến trong file .env vào os.environ (bỏ qua dòng trống / comment)."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


BASE_DIR = Path(__file__).resolve().parent
load_env(BASE_DIR / ".env")


def cfg(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


# ---------------------------------------------------------------------------
# 2. Đọc dữ liệu từ Google Sheet
# ---------------------------------------------------------------------------

def fetch_sheet_rows(csv_url: str) -> list[dict]:
    """Đọc dữ liệu CSV và trả về danh sách dòng (dict theo tên cột).

    Ưu tiên GOOGLE_SHEET_CSV_URL. Nếu bỏ trống, tự dùng file sample_data.csv
    cùng thư mục để bạn chạy thử ngay khi chưa nối Google Sheet.
    Cũng chấp nhận một đường dẫn file CSV local.
    """
    if not csv_url:
        local = BASE_DIR / "sample_data.csv"
        if local.exists():
            print("[i] Chưa cấu hình GOOGLE_SHEET_CSV_URL — đang dùng sample_data.csv để chạy thử.")
            raw = local.read_text(encoding="utf-8-sig")
        else:
            raise SystemExit("Thiếu GOOGLE_SHEET_CSV_URL trong .env")
    elif csv_url.startswith(("http://", "https://")):
        req = urllib.request.Request(csv_url, headers={"User-Agent": "cfo-agent/0.1"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8-sig")
    else:
        raw = Path(csv_url).expanduser().read_text(encoding="utf-8-sig")

    reader = csv.DictReader(io.StringIO(raw))
    return [ {(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader ]


def parse_amount(text: str) -> float:
    """Chuyển '1.500.000' / '1,500,000' / '1500000 đ' -> 1500000.0."""
    if not text:
        return 0.0
    cleaned = "".join(ch for ch in text if ch.isdigit() or ch in ".,-")
    # Bỏ dấu phân cách hàng nghìn, giữ dấu trừ.
    cleaned = cleaned.replace(".", "").replace(",", "")
    try:
        return float(cleaned) if cleaned not in ("", "-") else 0.0
    except ValueError:
        return 0.0


def parse_row_date(text: str):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# 3. Tính toán
# ---------------------------------------------------------------------------

def summarize(rows: list[dict]) -> dict:
    col_date = cfg("COL_DATE", "Ngày")
    col_type = cfg("COL_TYPE", "Loại")
    col_amount = cfg("COL_AMOUNT", "Số tiền")
    col_item = cfg("COL_ITEM", "Hạng mục")
    period = cfg("REPORT_PERIOD", "month").lower()  # day | month

    today = date.today()
    revenue = 0.0
    cost = 0.0
    cost_by_item: dict[str, float] = {}
    counted = 0

    for row in rows:
        d = parse_row_date(row.get(col_date, ""))
        if d is None:
            continue
        if period == "day" and d != today:
            continue
        if period == "month" and (d.year, d.month) != (today.year, today.month):
            continue

        amount = parse_amount(row.get(col_amount, ""))
        loai = row.get(col_type, "").lower()
        counted += 1
        if "thu" in loai:            # "Doanh thu", "thu"
            revenue += amount
        elif "chi" in loai:          # "Chi phí", "chi"
            cost += amount
            item = row.get(col_item, "Khác") or "Khác"
            cost_by_item[item] = cost_by_item.get(item, 0.0) + amount

    return {
        "period": period,
        "as_of": today.isoformat(),
        "rows_counted": counted,
        "revenue": revenue,
        "cost": cost,
        "profit": revenue - cost,
        "cost_by_item": dict(sorted(cost_by_item.items(), key=lambda x: -x[1])),
    }


def fmt_vnd(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".") + " đ"


# ---------------------------------------------------------------------------
# 4. Nhờ Claude viết nhận định
# ---------------------------------------------------------------------------

def ai_commentary(summary: dict) -> str:
    api_key = cfg("ANTHROPIC_API_KEY")
    if not api_key:
        return "(Chưa cấu hình ANTHROPIC_API_KEY nên bỏ qua phần nhận định AI.)"
    try:
        import anthropic
    except ImportError:
        return "(Chưa cài thư viện 'anthropic'. Chạy: pip install anthropic)"

    model = cfg("ANTHROPIC_MODEL", "claude-opus-4-8")
    company = cfg("COMPANY_NAME", "công ty")

    top_costs = "\n".join(
        f"- {item}: {fmt_vnd(v)}" for item, v in list(summary["cost_by_item"].items())[:5]
    ) or "- (không có)"

    prompt = f"""Bạn là CFO của {company}. Dưới đây là số liệu tài chính kỳ báo cáo ({summary['period']}, tính đến {summary['as_of']}):

- Doanh thu: {fmt_vnd(summary['revenue'])}
- Chi phí: {fmt_vnd(summary['cost'])}
- Lợi nhuận: {fmt_vnd(summary['profit'])}
- Số bản ghi trong kỳ: {summary['rows_counted']}

Các khoản chi lớn nhất:
{top_costs}

Viết một đoạn NHẬN ĐỊNH ngắn gọn (tối đa 5 câu), bằng tiếng Việt, giọng điệu như một giám đốc tài chính báo cáo cho sếp: nêu tình hình, 1-2 điểm đáng chú ý (biên lợi nhuận, khoản chi bất thường), và 1 khuyến nghị hành động. Không lặp lại số liệu đã liệt kê, tập trung vào ý nghĩa."""

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
    return "\n".join(parts).strip() or "(AI không trả về nội dung.)"


# ---------------------------------------------------------------------------
# 5. Gửi Telegram
# ---------------------------------------------------------------------------

def send_telegram(text: str) -> None:
    token = cfg("TELEGRAM_BOT_TOKEN")
    chat_id = cfg("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong .env")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    if not payload.get("ok"):
        raise SystemExit(f"Telegram trả lỗi: {payload}")


# ---------------------------------------------------------------------------
# 6. Ghép báo cáo & chạy
# ---------------------------------------------------------------------------

def build_report(summary: dict, commentary: str) -> str:
    company = cfg("COMPANY_NAME", "Công ty")
    period_label = "hôm nay" if summary["period"] == "day" else "tháng này"
    lines = [
        f"<b>📊 BÁO CÁO TÀI CHÍNH — {company}</b>",
        f"<i>Kỳ: {period_label} · tính đến {summary['as_of']}</i>",
        "",
        f"💰 Doanh thu: <b>{fmt_vnd(summary['revenue'])}</b>",
        f"💸 Chi phí: <b>{fmt_vnd(summary['cost'])}</b>",
        f"📈 Lợi nhuận: <b>{fmt_vnd(summary['profit'])}</b>",
    ]
    if summary["cost_by_item"]:
        lines.append("")
        lines.append("<b>Chi lớn nhất:</b>")
        for item, v in list(summary["cost_by_item"].items())[:5]:
            lines.append(f"• {item}: {fmt_vnd(v)}")
    lines += ["", "<b>🧠 Nhận định:</b>", commentary]
    return "\n".join(lines)


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    rows = fetch_sheet_rows(cfg("GOOGLE_SHEET_CSV_URL"))
    summary = summarize(rows)
    commentary = ai_commentary(summary)
    report = build_report(summary, commentary)

    if dry_run:
        print(report.replace("<b>", "").replace("</b>", "")
                    .replace("<i>", "").replace("</i>", ""))
        return
    send_telegram(report)
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Đã gửi báo cáo Telegram.")


if __name__ == "__main__":
    main()
