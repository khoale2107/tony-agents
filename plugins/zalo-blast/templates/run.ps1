$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python zalo_blast.py $args
