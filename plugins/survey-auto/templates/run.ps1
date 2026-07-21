$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python survey_auto.py $args
