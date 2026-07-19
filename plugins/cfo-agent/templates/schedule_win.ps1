# Đặt lịch chạy CFO Agent 7h sáng mỗi ngày trên Windows (Task Scheduler).
# Cách dùng:  .\schedule_win.ps1           (bật lịch 7:00)
#             .\schedule_win.ps1 -At 08:30 (bật lịch 8:30)
#             .\schedule_win.ps1 -Off       (tắt lịch)
param(
    [string]$At = "07:00",
    [switch]$Off
)
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$taskName = "TonyAcademy-CFO-Agent"

if ($Off) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Đã tắt lịch CFO Agent."
    exit 0
}

$runPs1 = Join-Path $PSScriptRoot "run.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runPs1`"" `
    -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "Báo cáo tài chính CFO Agent hằng ngày" -Force | Out-Null

Write-Host "Đã đặt lịch: CFO Agent chạy lúc $At mỗi ngày."
