# Claude Desktop Setup — MCP Stdio (Move Cube)

Add the MCP stdio server to Claude Desktop so it can call the `blender_move_cube` tool.

## Command
- If `.venv` exists: `D:\MVP\.venv\Scripts\python.exe -m mvp.mcp_stdio`
- Otherwise: `python -m mvp.mcp_stdio`
- Optional: set `BLENDER_EXE` to the path of `blender.exe` (e.g., `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`).

## Steps (Windows)
1) Open Claude Desktop → Settings → Model Context Protocol → Add Server.
2) Choose “Stdio” server type.
3) Command: pick the Python path above; Args: `-m mvp.mcp_stdio`.
4) Ensure Blender 5.0 is installed; set `BLENDER_EXE` if it is not on the default path list.
5) Save. Claude will list the `blender_move_cube` tool with defaults `name="MVP_Cube"` and `delta=[0,0,2]`.

## What the tool does
- Launches Blender headless, creates or reuses a cube (data-first via `bpy.data`/`scene.collection.objects.link`), applies `delta`, and returns JSON with the final position and Blender version.
