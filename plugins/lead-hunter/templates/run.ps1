$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python lead_hunter.py $args
