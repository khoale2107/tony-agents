$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python social_dm.py $args
