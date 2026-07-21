$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python reply_approval.py $args
