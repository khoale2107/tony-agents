$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python competitor_intel.py $args
