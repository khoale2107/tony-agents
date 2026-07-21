$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python ad_image_composer.py $args
