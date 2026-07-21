$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python dept_handoff.py $args
