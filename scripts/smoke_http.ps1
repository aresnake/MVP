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

Write-Host "=== MVP HTTP smoke test ===" -ForegroundColor Cyan
Write-Host "CWD: $repoRoot"
Write-Host "Transport: http://127.0.0.1:$Port"
if ($InMemory) { Write-Host "Runtime: in-memory adapter" }

$proc = Start-Process -FilePath "python" -ArgumentList "-m","mvp.server" -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden

function Stop-Server {
    param($p)
    if ($p -and -not $p.HasExited) {
        Stop-Process -Id $p.Id -Force
        $p.WaitForExit()
    }
}

try {
    $client = [System.Net.Http.HttpClient]::new()
    $client.BaseAddress = [Uri]"http://127.0.0.1:$Port"

    # wait for server to start
    $ready = $false
    foreach ($i in 1..40) {
        try {
            $resp = $client.GetAsync("/health").Result
            if ($resp.IsSuccessStatusCode) { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 200 }
    }
    if (-not $ready) { throw "Server did not start on http://127.0.0.1:$Port" }

    Write-Host "GET /health"
    $health = $client.GetStringAsync("/health").Result
    Write-Host $health

    Write-Host "GET /tools"
    $tools = $client.GetStringAsync("/tools").Result
    Write-Host $tools

    Write-Host "POST /call runtime.probe (no contract)"
    $payload = '{"name":"runtime.probe","params":{}}'
    $resp = $client.PostAsync("/call", (New-Object System.Net.Http.StringContent($payload, [System.Text.Encoding]::UTF8, "application/json"))).Result
    Write-Host $resp.Content.ReadAsStringAsync().Result

    Write-Host "POST /contract/create"
    $createBody = '{"host_profile":"codex_stdio","runtime_profile":"none","capabilities":["DATA_ONLY"],"tool_allowlist":["runtime.probe","scene.list_objects"]}'
    $resp = $client.PostAsync("/contract/create", (New-Object System.Net.Http.StringContent($createBody, [System.Text.Encoding]::UTF8, "application/json"))).Result
    Write-Host $resp.Content.ReadAsStringAsync().Result

    Write-Host "POST /call runtime.probe"
    $resp = $client.PostAsync("/call", (New-Object System.Net.Http.StringContent($payload, [System.Text.Encoding]::UTF8, "application/json"))).Result
    Write-Host $resp.Content.ReadAsStringAsync().Result
}
finally {
    Stop-Server $proc
}
