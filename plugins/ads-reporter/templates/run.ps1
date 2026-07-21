$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python ads_reporter.py $args
