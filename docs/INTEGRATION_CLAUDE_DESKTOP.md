# Integration: Claude Desktop (stdio)

1) Start the server (stdio)
- PowerShell: `./scripts/run_stdio.ps1`
- Keep only one instance running.

2) Configure Claude Desktop MCP
- Add to `mcpServers`:
```json
{
  "mcpServers": {
    "mvp": {
      "command": "powershell.exe",
      "args": [
        "-NoLogo",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "D:/MVP/scripts/run_stdio.ps1"
      ]
    }
  }
}
```
- Adjust the path to your repo if needed.

3) Use normally
- Claude will launch the stdio server via the script.
- Do not start a second server manually while Claude runs it.
