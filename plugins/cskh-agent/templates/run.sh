#!/usr/bin/env bash
# Trợ lý CSKH (macOS/Linux).
#   ./run.sh "câu hỏi của khách"   trả lời 1 câu
#   ./run.sh                       chế độ hỏi-đáp liên tục
# Dùng gói Claude Code, KHÔNG cần cài thư viện gì.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 cskh.py "$@"
