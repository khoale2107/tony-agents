$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python comment_insight.py $args
