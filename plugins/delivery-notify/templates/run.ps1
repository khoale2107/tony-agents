$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python delivery_notify.py $args
