$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python rag_knowledge.py $args
