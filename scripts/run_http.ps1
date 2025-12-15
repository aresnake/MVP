[CmdletBinding()]
param(
    [int]$Port = 8765,
    [switch]$InMemory
)

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:MVP_TRANSPORT = "http"
$env:MVP_HTTP_PORT = $Port
if ($InMemory) { $env:MVP_RUNTIME = "inmemory" }

Write-Host "=== MVP server (http) ===" -ForegroundColor Cyan
Write-Host "CWD: $repoRoot"
Write-Host "Transport: http://127.0.0.1:$Port"
if ($InMemory) { Write-Host "Runtime: in-memory adapter" }
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow

python -m mvp.server
