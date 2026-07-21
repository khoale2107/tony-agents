$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python order_sla.py $args
