bl_info = {
    "name": "MVP MCP Dev UI Bridge",
    "author": "aresnake",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "3D Viewport > Sidebar > MVP",
    "category": "3D View",
    "description": "DEV UI BRIDGE: Move cube data-first to Z+2. No servers or sockets.",
}

# DEV UI BRIDGE: minimal, local-only helper to mirror the MCP move cube behavior inside Blender UI.
# Attempts an MCP stdio roundtrip first; if it fails, falls back to local data-first move.

import json
import os
import subprocess
import sys

import bpy

TARGET_NAME = "MVP_Cube_UI"
TARGET_POS = (0.0, 0.0, 2.0)


def ensure_cube(name: str):
    obj = bpy.data.objects.get(name)
    if obj and obj.type != "MESH":
        bpy.data.objects.remove(obj, do_unlink=True)
        obj = None

    if obj is None:
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        obj = bpy.data.objects.new(name, mesh)
        scene = bpy.context.scene or bpy.data.scenes[0]
        scene.collection.objects.link(obj)

    mesh = obj.data
    verts = [
        (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, -1),
        (-1, 1, 1),
        (1, -1, -1),
        (1, -1, 1),
        (1, 1, -1),
        (1, 1, 1),
    ]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (1, 5, 7, 3),
        (0, 2, 6, 4),
    ]
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    return obj


def _python_executable() -> str:
    return os.environ.get("MVP_PYTHON_EXE") or sys.executable


def _read_until_id(proc: subprocess.Popen, target_id: int, timeout_lines: int = 20):
    for _ in range(timeout_lines):
        line = proc.stdout.readline()
        if not line:
            break
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("id") == target_id:
            return payload
    return None


def call_mcp_move_cube():
    python_exe = _python_executable()
    cmd = [python_exe, "-m", "mvp.mcp_stdio"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as exc:
        return False, f"failed to start MCP stdio: {exc}"

    try:
        def send(msg_id: int, method: str, params: dict):
            payload = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params}
            proc.stdin.write(json.dumps(payload) + "\n")
            proc.stdin.flush()

        send(
            1,
            "initialize",
            {
                "protocolVersion": 1,
                "capabilities": {},
                "clientInfo": {"name": "mvp-blender-ui", "version": "0.1.0"},
            },
        )
        init_resp = _read_until_id(proc, 1)
        if not init_resp or "error" in init_resp:
            stderr = proc.stderr.read() if proc.stderr else ""
            return False, f"initialize failed: {init_resp or 'no response'} {stderr}"

        send(
            2,
            "tools/call",
            {
                "name": "blender_move_cube",
                "arguments": {"mode": "set", "name": TARGET_NAME, "delta": list(TARGET_POS)},
            },
        )
        call_resp = _read_until_id(proc, 2)
        if not call_resp:
            return False, "no response to tools/call"
        if "error" in call_resp:
            return False, f"RPC error: {call_resp['error']}"

        result = call_resp.get("result") or {}
        structured = result.get("structuredContent")
        if structured and structured.get("ok"):
            pos = structured.get("result", {}).get("position")
            return True, f"{TARGET_NAME} -> {pos}"
        else:
            return False, f"tool returned error: {structured or result}"
    except Exception as exc:  # pragma: no cover - Blender UI path
        return False, f"exception during MCP call: {exc}"
    finally:
        try:
            if proc.stdin:
                proc.stdin.close()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()


class MVP_OT_move_cube(bpy.types.Operator):
    bl_idname = "mvp.bridge_move_cube"
    bl_label = "Move Cube (Z +2)"
    bl_description = "DEV UI BRIDGE: set MVP_Cube_UI location to [0,0,2] using data-first logic."
    bl_options = {"REGISTER"}

    def execute(self, context):
        ok, message = call_mcp_move_cube()
        if ok:
            self.report({"INFO"}, f"MCP OK: {message}")
            return {"FINISHED"}

        # Fallback: local data-first move
        try:
            cube = ensure_cube(TARGET_NAME)
            cube.location.x = TARGET_POS[0]
            cube.location.y = TARGET_POS[1]
            cube.location.z = TARGET_POS[2]
            self.report({"INFO"}, f"MCP FAILED, used fallback: {message} (now at {tuple(cube.location)})")
            return {"FINISHED"}
        except Exception as exc:  # pragma: no cover - Blender UI path
            self.report({"ERROR"}, f"MCP FAILED and fallback failed: {message}; {exc}")
            return {"CANCELLED"}


class MVP_PT_panel(bpy.types.Panel):
    bl_label = "MVP Bridge"
    bl_idname = "MVP_PT_bridge_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MVP"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="DEV UI BRIDGE (local)")
        col.operator(MVP_OT_move_cube.bl_idname, text="Move Cube (Z +2)")


classes = (MVP_OT_move_cube, MVP_PT_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
