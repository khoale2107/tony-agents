$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python ocr_invoice.py $args
