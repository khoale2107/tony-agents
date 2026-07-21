$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python attendance.py $args
