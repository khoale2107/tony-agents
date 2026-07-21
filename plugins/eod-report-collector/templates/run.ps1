$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python eod_collector.py $args
