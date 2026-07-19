# Chạy CFO Agent trên Windows (PowerShell).
# Cách dùng:  .\run.ps1            (gửi báo cáo Telegram)
#             .\run.ps1 --dry-run  (chỉ in ra màn hình để thử)
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv")) {
    Write-Host "[setup] Tạo môi trường Python (.venv) và cài thư viện..."
    python -m venv .venv
    & ".\.venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
    & ".\.venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
}

& ".\.venv\Scripts\python.exe" cfo_agent.py $args
