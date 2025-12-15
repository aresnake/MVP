Param(
    [string]$PythonPath
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$projectRoot\.."

if (-not $PythonPath) {
    $venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        $PythonPath = $venvPython
    } else {
        $PythonPath = "python"
    }
}

Write-Host "Using Python: $PythonPath"
Write-Host "BLENDER_EXE (if set): $Env:BLENDER_EXE"

Push-Location $repoRoot
& $PythonPath -m mvp.mcp_stdio @Args
Pop-Location
