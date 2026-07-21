$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python payment_confirm.py $args
