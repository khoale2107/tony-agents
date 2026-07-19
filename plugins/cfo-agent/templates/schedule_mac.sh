#!/usr/bin/env bash
# Đặt lịch chạy CFO Agent 7h sáng mỗi ngày trên macOS (dùng launchd).
# Cách dùng:  ./schedule_mac.sh          (bật lịch 7:00)
#             ./schedule_mac.sh 8 30      (bật lịch 8:30)
#             ./schedule_mac.sh --off     (tắt lịch)
set -euo pipefail
cd "$(dirname "$0")"

LABEL="com.tonyacademy.cfo-agent"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

if [ "${1:-}" = "--off" ]; then
  launchctl unload "$PLIST" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Đã tắt lịch CFO Agent."
  exit 0
fi

HOUR="${1:-7}"
MINUTE="${2:-0}"
WORKDIR="$(pwd)"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${WORKDIR}/run.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>${HOUR}</integer>
    <key>Minute</key><integer>${MINUTE}</integer>
  </dict>
  <key>StandardOutPath</key><string>${WORKDIR}/cfo-agent.log</string>
  <key>StandardErrorPath</key><string>${WORKDIR}/cfo-agent.log</string>
  <key>WorkingDirectory</key><string>${WORKDIR}</string>
</dict>
</plist>
PLISTEOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Đã đặt lịch: CFO Agent chạy lúc ${HOUR}:$(printf '%02d' "$MINUTE") mỗi ngày."
echo "Log ghi tại: ${WORKDIR}/cfo-agent.log"
