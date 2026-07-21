$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python customer_tracking.py $args
