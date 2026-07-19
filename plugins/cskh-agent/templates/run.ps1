# Trợ lý CSKH (Windows PowerShell).
#   .\run.ps1 "câu hỏi của khách"   trả lời 1 câu
#   .\run.ps1                       chế độ hỏi-đáp liên tục
# Dùng gói Claude Code, KHÔNG cần cài thư viện gì.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python cskh.py $args
