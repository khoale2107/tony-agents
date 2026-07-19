#!/usr/bin/env bash
# Chạy CFO Agent trên macOS / Linux.
# Cách dùng:  ./run.sh          (gửi báo cáo Telegram)
#             ./run.sh --dry-run (chỉ in ra màn hình để thử)
set -euo pipefail
cd "$(dirname "$0")"

# Tạo môi trường ảo lần đầu, cài thư viện.
if [ ! -d ".venv" ]; then
  echo "[setup] Tạo môi trường Python (.venv) và cài thư viện..."
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet --upgrade pip
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

exec ./.venv/bin/python cfo_agent.py "$@"
