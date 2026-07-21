$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python content_calendar.py $args
