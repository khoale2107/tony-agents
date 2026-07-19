# Chạy CFO Agent trên Windows (PowerShell).
#   .\run.ps1            gửi báo cáo Telegram
#   .\run.ps1 --dry-run  chỉ in ra màn hình để thử
#
# Bản dùng gói Claude Code KHÔNG cần cài thư viện gì (chỉ dùng Python có sẵn +
# lệnh 'claude'). Nếu bạn chọn chế độ API key thì tự cài: pip install anthropic
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python cfo_agent.py $args
