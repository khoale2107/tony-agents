$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python ops_daily.py $args
