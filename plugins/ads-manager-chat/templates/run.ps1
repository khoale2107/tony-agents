$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python ads_manager.py $args
