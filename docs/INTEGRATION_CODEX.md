# Integration: Codex CLI / HTTP

## Stdio
- Start server: `./scripts/run_stdio.ps1`
- Connect Codex to the MCP stdio server as usual.

## HTTP (optional)
- Start server: `./scripts/run_http.ps1 -Port 8765`
- Simple call with PowerShell curl:
  - Health: `curl http://127.0.0.1:8765/health`
  - Tools: `curl http://127.0.0.1:8765/tools`
  - Call tool: `curl -Method POST -ContentType application/json -Body '{"name":"system.tools_catalog","params":{}}' http://127.0.0.1:8765/call`
- Contract via HTTP:
  - `curl -Method POST -ContentType application/json -Body '{"host_profile":"codex_stdio","runtime_profile":"none","capabilities":["DATA_ONLY"],"tool_allowlist":["runtime.probe","scene.list_objects"]}' http://127.0.0.1:8765/contract/create`

## Tips
- Use `./scripts/run_http.ps1 -InMemory` to enable the in-memory runtime adapter for quick demos.
- To target an external MCPBLENDER HTTP runtime, set `MVP_RUNTIME=external_http` and `MVP_RUNTIME_URL=http://127.0.0.1:9876` (or your URL) before starting the server (works for both stdio/http transports).
- Ensure only one server instance is running on a given port.
