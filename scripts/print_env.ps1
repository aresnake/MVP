[CmdletBinding()]
param()

Write-Host "MVP environment variables:"
Write-Host "  MVP_TRANSPORT : $($env:MVP_TRANSPORT)"
Write-Host "  MVP_HTTP_PORT : $($env:MVP_HTTP_PORT)"
Write-Host "  MVP_RUNTIME   : $($env:MVP_RUNTIME)"
