$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python daily_kpi.py $args
