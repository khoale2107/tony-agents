"""
finlib — thư viện dùng chung cho các agent tài chính/vận hành của Tony Academy.
Không cần thư viện ngoài. Gọi AI ưu tiên GÓI Claude Code (claude -p), fallback API key.
"""

import csv
import io
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


# ---- cấu hình ----
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


def cfg(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


# ---- tiện ích số/ngày ----
def parse_amount(text) -> float:
    if text is None or text == "":
        return 0.0
    if isinstance(text, (int, float)):
        return float(text)
    cleaned = "".join(ch for ch in str(text) if ch.isdigit() or ch in ".,-")
    cleaned = cleaned.replace(".", "").replace(",", "")
    try:
        return float(cleaned) if cleaned not in ("", "-") else 0.0
    except ValueError:
        return 0.0


def parse_date(text):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(text).strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def fmt_vnd(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".") + " đ"


# ---- nguồn dữ liệu (SOURCE=gsheet|csv|custom) ----
def fetch_rows(base_dir: Path) -> list[dict]:
    source = cfg("SOURCE", "gsheet").lower()
    if source in ("", "gsheet", "csv"):
        return _fetch_csv(cfg("GOOGLE_SHEET_CSV_URL"), base_dir)
    if source == "custom":
        return _fetch_custom(base_dir)
    raise SystemExit(f"SOURCE='{source}' chưa hỗ trợ. Dùng gsheet | csv | custom, "
                     "hoặc nhờ Claude Code viết adapter.")


def _fetch_csv(csv_url: str, base_dir: Path) -> list[dict]:
    if not csv_url:
        local = base_dir / "sample_data.csv"
        if local.exists():
            print("[i] Chưa cấu hình GOOGLE_SHEET_CSV_URL — đang dùng sample_data.csv để chạy thử.")
            raw = local.read_text(encoding="utf-8-sig")
        else:
            raise SystemExit("Thiếu GOOGLE_SHEET_CSV_URL trong .env")
    elif csv_url.startswith(("http://", "https://")):
        req = urllib.request.Request(csv_url, headers={"User-Agent": "tony-agents/0.1"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8-sig")
    else:
        raw = Path(csv_url).expanduser().read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def _fetch_custom(base_dir: Path) -> list[dict]:
    path = base_dir / "adapter_custom.py"
    if not path.exists():
        raise SystemExit(
            "SOURCE=custom nhưng chưa có adapter_custom.py.\n"
            "Mở Claude Code và nói 'dữ liệu tôi ở <ERP>...' để nó viết adapter."
        )
    import importlib.util
    spec = importlib.util.spec_from_file_location("adapter_custom", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "fetch_rows"):
        raise SystemExit("adapter_custom.py phải có hàm fetch_rows() -> list[dict].")
    return list(mod.fetch_rows())


# ---- gọi AI: ưu tiên GÓI Claude Code, fallback API ----
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


def ask_ai(prompt: str, timeout: int = 180) -> str:
    claude_bin = find_claude()
    if claude_bin:
        try:
            r = subprocess.run([claude_bin, "-p", prompt],
                               capture_output=True, text=True, timeout=timeout)
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
                max_tokens=1024, messages=[{"role": "user", "content": prompt}])
            txt = "\n".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
            if txt:
                return txt
        except ImportError:
            print("[!] Chế độ API cần: pip install anthropic")
        except Exception as e:
            print(f"[!] Lỗi gọi API: {e}")
    return ("(Chưa dùng được AI. Cần cài Claude Code + đăng nhập gói — khuyến nghị, "
            "hoặc điền ANTHROPIC_API_KEY vào .env.)")


# ---- gửi Telegram (tùy chọn) ----
def send_telegram(text: str) -> None:
    token = cfg("TELEGRAM_BOT_TOKEN")
    chat_id = cfg("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong .env")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id, "text": text,
        "parse_mode": "HTML", "disable_web_page_preview": "true",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as resp:
        import json
        payload = json.loads(resp.read().decode())
    if not payload.get("ok"):
        raise SystemExit(f"Telegram lỗi: {payload}")
