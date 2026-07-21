#!/usr/bin/env python3
"""
Ads Manager qua chat — bật/tắt campaign & đổi ngân sách bằng lệnh Telegram.

  ./run.sh --dry-run tat "Mùa Cưới 2026"          mô phỏng tắt 1 campaign (không gửi, không áp thật)
  ./run.sh --dry-run bat "Combo Chụp Ảnh"          mô phỏng bật
  ./run.sh --dry-run nsach "Mùa Cưới 2026" 800000  mô phỏng đổi ngân sách/ngày
  ./run.sh poll                                     đọc lệnh mới trong chat, áp qua connector, ghi actions.csv, trả lời

Cú pháp lệnh trong Telegram:
  tat <campaign>            tắt campaign
  bat <campaign>            bật campaign
  nsach <campaign> <số>     đổi ngân sách/ngày (VND)

Danh sách campaign đọc từ campaigns.csv (chưa có thì dùng campaigns_example.csv).
Áp lên nền tảng thật qua connector.py (copy từ connector_example.py — hàm apply_action).
Câu nói tự nhiên ("tắt chiến dịch mùa cưới giúp") được Claude Code (GÓI, không API key) diễn giải.
"""
from __future__ import annotations

import csv
import json
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import finlib as fl

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")
OFFSET_FILE = HERE / ".tg_offset"
ACTIONS_FILE = HERE / "actions.csv"
ACTION_HEADER = ["ThoiGian", "Lenh", "Campaign", "GiaTri", "KetQua"]

# Tên hành động chuẩn hoá
VERBS = {
    "tat": "tat", "tắt": "tat", "off": "tat", "stop": "tat", "pause": "tat",
    "bat": "bat", "bật": "bat", "on": "bat", "start": "bat", "run": "bat",
    "nsach": "nsach", "ngansach": "nsach", "ngân_sách": "nsach",
    "budget": "nsach", "ns": "nsach",
}
VERB_LABEL = {"tat": "TẮT", "bat": "BẬT", "nsach": "ĐỔI NGÂN SÁCH"}


# ---------- Telegram helper ----------
def tg(method: str, **params):
    token = fl.cfg("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong .env")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
        return json.loads(r.read().decode())


# ---------- dữ liệu campaign ----------
def _no_accent(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()


def read_campaigns() -> list[dict]:
    p = HERE / "campaigns.csv"
    if not p.exists():
        alt = HERE / "campaigns_example.csv"
        if alt.exists():
            print(f"[i] Chưa có campaigns.csv — dùng {alt.name} để chạy thử.")
            p = alt
        else:
            return []
    with p.open(encoding="utf-8-sig") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()}
                for row in csv.DictReader(f)]


def find_campaign(name: str, rows: list[dict]) -> dict:
    """Khớp campaign theo tên (bỏ dấu, kiểu 'chứa'). Trả về row hoặc {}."""
    want = _no_accent(name)
    if not want:
        return {}
    # exact trước
    for r in rows:
        if _no_accent(r.get("Campaign", "")) == want:
            return r
    # rồi tới 'chứa'
    for r in rows:
        cn = _no_accent(r.get("Campaign", ""))
        if want in cn or cn in want:
            return r
    return {}


def write_campaigns(rows: list[dict]) -> None:
    p = HERE / "campaigns.csv"
    if not p.exists():
        return  # chỉ cập nhật file thật, không đụng file _example
    fields = list(rows[0].keys()) if rows else ["Campaign", "TrangThai", "NganSach"]
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# ---------- phân tích lệnh ----------
def parse_command(text: str) -> dict:
    """Trả về {'verb','campaign','value'} hoặc {} nếu không phải lệnh ads."""
    toks = text.strip().split()
    if not toks:
        return {}
    verb = VERBS.get(toks[0].lower())
    if not verb:
        return {}
    rest = toks[1:]
    if verb == "nsach":
        if len(rest) < 2:
            return {"verb": verb, "campaign": "", "value": None, "error": "Thiếu tên campaign hoặc số tiền."}
        value = fl.parse_amount(rest[-1])
        campaign = " ".join(rest[:-1]).strip().strip('"').strip("'")
        return {"verb": verb, "campaign": campaign, "value": value}
    campaign = " ".join(rest).strip().strip('"').strip("'")
    if not campaign:
        return {"verb": verb, "campaign": "", "value": None, "error": "Thiếu tên campaign."}
    return {"verb": verb, "campaign": campaign, "value": None}


def ai_parse(text: str) -> dict:
    """Diễn giải câu nói tự nhiên tiếng Việt -> lệnh ads (dùng GÓI Claude Code)."""
    prompt = (
        "Người dùng nhắn một câu điều khiển quảng cáo. Hãy trích thành JSON đúng 1 dòng, "
        'khoá: verb (một trong "tat","bat","nsach"), campaign (chuỗi tên chiến dịch), '
        'value (số nguyên VND nếu là đổi ngân sách, ngược lại null). '
        'Nếu không phải lệnh quảng cáo, trả {"verb":null}. '
        "Chỉ trả JSON, không giải thích.\nCâu: " + text
    )
    raw = fl.ask_ai(prompt).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < 0:
        return {}
    try:
        data = json.loads(raw[start:end + 1])
    except Exception:
        return {}
    verb = VERBS.get(str(data.get("verb", "")).lower()) if data.get("verb") else None
    if not verb:
        return {}
    val = data.get("value")
    return {"verb": verb, "campaign": (data.get("campaign") or "").strip(),
            "value": fl.parse_amount(val) if val not in (None, "") else None}


# ---------- áp hành động ----------
def load_connector():
    """connector.py thật nếu có; ngược lại connector_example (seam raise)."""
    for name in ("connector", "connector_example"):
        p = HERE / f"{name}.py"
        if p.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location(name, p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "apply_action"):
                return mod
    return None


def log_action(verb: str, campaign: str, value, result: str) -> None:
    new = not ACTIONS_FILE.exists()
    with ACTIONS_FILE.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(ACTION_HEADER)
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    verb, campaign, "" if value is None else int(value), result])


def describe(cmd: dict, camp: dict) -> str:
    verb, value = cmd["verb"], cmd.get("value")
    name = camp.get("Campaign") if camp else cmd["campaign"]
    if verb == "nsach":
        old = camp.get("NganSach", "?") if camp else "?"
        old_s = fl.fmt_vnd(fl.parse_amount(old)) if old not in ("?", "") else "?"
        return f"{VERB_LABEL[verb]} “{name}”: {old_s} → {fl.fmt_vnd(value)}/ngày"
    cur = camp.get("TrangThai", "?") if camp else "?"
    return f"{VERB_LABEL[verb]} “{name}” (đang: {cur or '?'})"


def apply_command(cmd: dict, dry: bool) -> str:
    """Trả về text phản hồi (HTML). dry=True: không gọi connector, không ghi log."""
    if cmd.get("error"):
        return f"⚠️ {cmd['error']}\nCú pháp: <code>tat|bat &lt;campaign&gt;</code> hoặc <code>nsach &lt;campaign&gt; &lt;số&gt;</code>"
    rows = read_campaigns()
    camp = find_campaign(cmd["campaign"], rows)
    verb, value = cmd["verb"], cmd.get("value")
    canonical = camp.get("Campaign") if camp else cmd["campaign"]
    head = describe(cmd, camp)

    if dry:
        note = "" if camp else "\n<i>(không thấy campaign này trong campaigns.csv — vẫn sẽ gửi lệnh)</i>"
        return f"<b>[dry-run] {head}</b>{note}\n<i>Chưa áp thật, chưa ghi actions.csv.</i>"

    conn = load_connector()
    result = "OK"
    try:
        if conn is None:
            raise NotImplementedError("Chưa có connector.apply_action.")
        conn.apply_action(verb, canonical, value)
    except NotImplementedError as e:
        result = "CHUA_CAU_HINH"
        log_action(verb, canonical, value, result)
        return (f"<b>{head}</b>\n⚠️ Connector chưa cấu hình: {e}\n"
                f"Copy <code>connector_example.py</code> → <code>connector.py</code> rồi nhờ "
                f"Claude Code điền <code>apply_action</code> cho nền tảng của bạn. Đã ghi log lệnh.")
    except Exception as e:
        result = f"LOI: {str(e)[:120]}"
        log_action(verb, canonical, value, result)
        return f"<b>{head}</b>\n❌ Lỗi khi áp lệnh: {e}"

    # áp thành công -> cập nhật trạng thái file thật
    if camp:
        if verb == "nsach":
            camp["NganSach"] = str(int(value))
        else:
            camp["TrangThai"] = "bat" if verb == "bat" else "tat"
        write_campaigns(rows)
    log_action(verb, canonical, value, result)
    return f"<b>✅ {head}</b>\nĐã áp lên nền tảng và ghi actions.csv."


# ---------- chế độ ----------
def dry_run(argv_rest: list[str]):
    text = " ".join(argv_rest).strip() or 'tat "Mùa Cưới 2026"'
    cmd = parse_command(text)
    if not cmd:
        print(f"[i] '{text}' không khớp cú pháp — thử nhờ AI diễn giải...")
        cmd = ai_parse(text)
    if not cmd:
        print("Không nhận ra lệnh ads. Dùng: tat|bat <campaign> | nsach <campaign> <số>")
        return
    print(f"[dry-run] lệnh: {text}\n" + "-" * 44)
    # in dạng thô cho terminal (bỏ vài thẻ HTML cho dễ đọc)
    out = apply_command(cmd, dry=True)
    for tag in ("<b>", "</b>", "<i>", "</i>", "<code>", "</code>"):
        out = out.replace(tag, "")
    print(out.replace("&lt;", "<").replace("&gt;", ">"))


def poll():
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    resp = tg("getUpdates", offset=offset, timeout=25)
    updates = resp.get("result", [])
    if not updates:
        print("Chưa có lệnh mới.")
        return
    done = 0
    for u in updates:
        offset = u["update_id"] + 1
        msg = u.get("message") or u.get("channel_post")
        if not msg:
            continue
        text = (msg.get("text") or "").strip()
        if not text:
            continue
        chat_id = msg.get("chat", {}).get("id")
        mid = msg.get("message_id")
        cmd = parse_command(text)
        if not cmd:
            cmd = ai_parse(text)   # câu nói tự nhiên -> lệnh
        if not cmd:
            continue  # không phải lệnh ads -> im lặng
        reply = apply_command(cmd, dry=False)
        tg("sendMessage", chat_id=chat_id, text=reply, parse_mode="HTML",
           reply_to_message_id=mid, disable_web_page_preview="true")
        done += 1
        print(f"→ {cmd['verb']} '{cmd['campaign']}' (chat {chat_id})")
    OFFSET_FILE.write_text(str(offset))
    print(f"Xong. Xử lý {len(updates)} update, thực thi {done} lệnh.")


def main():
    args = sys.argv[1:]
    if "--dry-run" in args:
        dry_run([a for a in args if a != "--dry-run"])
        return
    cmd = args[0] if args else "poll"
    if cmd == "poll":
        poll()
    else:
        print("Dùng: ./run.sh poll  |  ./run.sh --dry-run tat \"Mùa Cưới 2026\"")


if __name__ == "__main__":
    main()
