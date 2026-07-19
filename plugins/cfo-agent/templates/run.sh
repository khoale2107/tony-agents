#!/usr/bin/env bash
# Chạy CFO Agent trên macOS / Linux.
#   ./run.sh            gửi báo cáo Telegram
#   ./run.sh --dry-run  chỉ in ra màn hình để thử
#
# Bản dùng gói Claude Code KHÔNG cần cài thư viện gì (chỉ dùng Python có sẵn +
# lệnh 'claude'). Nếu bạn chọn chế độ API key thì tự cài: pip install anthropic
set -euo pipefail
cd "$(dirname "$0")"
exec python3 cfo_agent.py "$@"
