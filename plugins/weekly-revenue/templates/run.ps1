$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python weekly_revenue.py $args
