#!/usr/bin/env bash
# Đặt lịch chạy tự động trên macOS (launchd).
#   ./schedule_mac.sh          bật lịch mặc định
#   ./schedule_mac.sh 8 30     đổi giờ 8:30
#   ./schedule_mac.sh --off    tắt lịch
set -euo pipefail
cd "$(dirname "$0")"
LABEL="com.tonyacademy.reply-approval"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
if [ "${1:-}" = "--off" ]; then
  launchctl unload "$PLIST" 2>/dev/null || true; rm -f "$PLIST"
  echo "Đã tắt lịch."; exit 0
fi
HOUR="${1:-7}"; MINUTE="${2:-0}"; WORKDIR="$(pwd)"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key><array><string>${WORKDIR}/run.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>${HOUR}</integer><key>Minute</key><integer>${MINUTE}</integer></dict>
  <key>StandardOutPath</key><string>${WORKDIR}/agent.log</string>
  <key>StandardErrorPath</key><string>${WORKDIR}/agent.log</string>
  <key>WorkingDirectory</key><string>${WORKDIR}</string>
</dict></plist>
PLISTEOF
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Đã đặt lịch ${HOUR}:$(printf '%02d' "$MINUTE") mỗi ngày. Log: ${WORKDIR}/agent.log"
