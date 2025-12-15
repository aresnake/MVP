# MVP Blender UI Bridge (Dev)

DEV-ONLY Blender add-on that mirrors the MVP move-cube logic inside the UI. No MCP transport, no sockets, no background server.

## How to install (from folder)
1. In Blender, go to `Edit > Preferences > Add-ons`.
2. Click `Install...` and pick the folder `bridge_blender/mvp_bridge` (or zip this folder and install the zip).
3. Enable **MVP MCP Dev UI Bridge** in the list.

## Usage
- Open the 3D Viewport, press `N` to show the sidebar, tab **MVP**, panel **MVP Bridge**.
- Click **Move Cube (Z +2)** to create or update `MVP_Cube_UI` as a data-first mesh cube and set its location to `[0, 0, 2]` (absolute).
- The operator reports the final position in the status bar.

## Notes
- This is a UI-only dev bridge; it does not start or talk to an MCP server yet.
- Geometry is built data-first (no `bpy.ops`), ensuring deterministic cube creation.
