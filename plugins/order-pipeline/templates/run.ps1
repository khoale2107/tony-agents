$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python order_pipeline.py $args
