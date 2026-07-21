$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python cskh_monitor.py $args
