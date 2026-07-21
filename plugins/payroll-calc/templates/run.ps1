$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python payroll_calc.py $args
