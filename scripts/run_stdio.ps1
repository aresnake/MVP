[CmdletBinding()]
param()

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "=== MVP server (stdio) ===" -ForegroundColor Cyan
Write-Host "CWD: $repoRoot"
Write-Host "Transport: stdio"
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow

python -m mvp.server
