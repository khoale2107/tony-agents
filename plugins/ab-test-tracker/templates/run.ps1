$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python ab_tracker.py $args
