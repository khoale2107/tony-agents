param([string]$At = "07:00", [switch]$Off)
$ErrorActionPreference = "Stop"; Set-Location -Path $PSScriptRoot
$taskName = "TonyAcademy-ad-image-composer"
if ($Off) { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue; Write-Host "Đã tắt lịch."; exit 0 }
$runPs1 = Join-Path $PSScriptRoot "run.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runPs1`"" -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $At
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force | Out-Null
Write-Host "Đã đặt lịch $At."
