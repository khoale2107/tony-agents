$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python master_assistant.py $args
