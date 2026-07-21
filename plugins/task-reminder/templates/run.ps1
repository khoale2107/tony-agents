$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python task_reminder.py $args
