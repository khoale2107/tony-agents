$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python spend_anomaly.py $args
