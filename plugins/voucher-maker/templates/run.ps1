$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python voucher_maker.py $args
