$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python budget_controller.py $args
