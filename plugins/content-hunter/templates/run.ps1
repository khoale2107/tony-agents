$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python content_hunter.py $args
