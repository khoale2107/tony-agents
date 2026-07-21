$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python order_status.py $args
