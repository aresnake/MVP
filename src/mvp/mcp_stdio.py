"""Minimal MCP stdio server exposing a single Blender move-cube tool.

The tool launches Blender headless, creates (or reuses) a cube, applies a delta with explicit
semantics, and returns deterministic JSON. No runtime sidecar or HTTP bridge is used; each call is
isolated with no inter-call persistence.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

import anyio
from mcp.server import Server
from mcp.server.session import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities, TextContent, Tool, ToolsCapability

RUNTIME_DIR = Path(__file__).resolve().parents[2] / ".runtime"
DEFAULT_NAME = "MVP_Cube"
DEFAULT_DELTA = [0.0, 0.0, 2.0]
DEFAULT_MODE = "set"


def _return_error(code: str, message: str, details: Any = None) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message, "details": details}}


def _resolve_blender_executable(provided: str | None, *, allow_fallback: bool = True) -> str | None:
    """Resolve blender executable path from argument, env, or common install paths."""
    candidates: list[str] = []
    if provided:
        candidates.append(provided)
        if not allow_fallback:
            # Only check the provided path; no additional candidates.
            return candidates[0] if Path(candidates[0]).is_file() else None

    env_path = os.environ.get("BLENDER_EXE")
    if env_path:
        candidates.append(env_path)
    candidates.extend(
        [
            r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        ]
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _write_move_cube_script(path: Path, name: str, delta: Sequence[float], mode: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    script = f"""\
import bpy
import json

NAME = {name!r}
DELTA = ({float(delta[0])}, {float(delta[1])}, {float(delta[2])})
MODE = {mode!r}


def ensure_cube(target_name: str):
    obj = bpy.data.objects.get(target_name)
    if obj:
        return obj

    mesh = bpy.data.meshes.new(f"{{target_name}}_mesh")
    obj = bpy.data.objects.new(target_name, mesh)

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
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)

    scene = bpy.context.scene or bpy.data.scenes[0]
    scene.collection.objects.link(obj)
    return obj


def move_cube(target_name: str, delta, mode: str):
    obj = ensure_cube(target_name)
    if mode == "set":
        obj.location.x = delta[0]
        obj.location.y = delta[1]
        obj.location.z = delta[2]
    elif mode == "add":
        obj.location.x += delta[0]
        obj.location.y += delta[1]
        obj.location.z += delta[2]
    else:
        raise ValueError(f"Unsupported mode: {{mode}}")
    return obj


def main():
    try:
        cube = move_cube(NAME, DELTA, MODE)
        result = {{
            "ok": True,
            "result": {{
                "name": cube.name,
                "position": list(cube.location),
                "blender_version": bpy.app.version_string,
                "mode": MODE,
            }},
        }}
    except Exception as exc:
        result = {{
            "ok": False,
            "error": {{"code": "blender_script_error", "message": str(exc), "details": None}},
        }}

    print("MVP_RESULT=" + json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
"""
    path.write_text(script, encoding="utf-8")


def run_blender_move_cube(
    name: str = DEFAULT_NAME,
    delta: Sequence[float] = DEFAULT_DELTA,
    blender_exe: str | None = None,
    mode: str = DEFAULT_MODE,
) -> dict[str, Any]:
    """Blocking helper that launches Blender, moves a cube, and returns parsed JSON."""
    blender_path = _resolve_blender_executable(blender_exe, allow_fallback=blender_exe is None)
    if not blender_path:
        return _return_error(
            code="blender_not_found",
            message="Blender executable was not found. Provide blender_exe or set BLENDER_EXE.",
            details=None,
        )

    script_path = RUNTIME_DIR / "move_cube.py"
    _write_move_cube_script(script_path, name, delta, mode)

    proc = subprocess.run(
        [
            blender_path,
            "--background",
            "--python",
            str(script_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    stdout = proc.stdout or ""
    result_line = None
    for line in stdout.splitlines():
        if line.startswith("MVP_RESULT="):
            result_line = line.split("MVP_RESULT=", 1)[1].strip()

    if not result_line:
        return _return_error(
            code="no_result",
            message="Blender did not produce a result line.",
            details={"returncode": proc.returncode, "stdout": stdout, "stderr": proc.stderr},
        )

    try:
        parsed = json.loads(result_line)
    except json.JSONDecodeError as exc:
        return _return_error(
            code="parse_error",
            message="Failed to parse Blender result.",
            details={"error": str(exc), "raw": result_line, "stderr": proc.stderr},
        )

    # If Blender returned error payload, propagate as-is.
    if isinstance(parsed, dict) and not parsed.get("ok", False):
        return parsed

    return parsed


server = Server("mvp-mcp-stdio", version="0.1.0")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="blender_move_cube",
            description=(
                "Launch Blender headless, create or reuse a cube, apply a delta (mode=set|add), "
                "and report its position. Calls are isolated; no inter-call persistence."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "default": DEFAULT_NAME},
                    "delta": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                        "default": DEFAULT_DELTA,
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["set", "add"],
                        "default": DEFAULT_MODE,
                        "description": "set=assign location to delta; add=offset location by delta within this call.",
                    },
                    "blender_exe": {
                        "type": "string",
                        "description": "Override path to blender.exe; otherwise uses BLENDER_EXE or common install paths.",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                    "result": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "position": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                            "blender_version": {"type": "string"},
                            "mode": {"type": "string"},
                        },
                        "required": ["name", "position", "blender_version", "mode"],
                    },
                    "error": {"type": "object"},
                },
                "required": ["ok"],
                "additionalProperties": True,
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Iterable[TextContent] | dict[str, Any]:
    if name != "blender_move_cube":
        return _return_error(code="unknown_tool", message=f"Unsupported tool: {name}", details=None)

    cube_name = arguments.get("name", DEFAULT_NAME)
    delta = arguments.get("delta", DEFAULT_DELTA)
    blender_exe = arguments.get("blender_exe")
    mode = arguments.get("mode", DEFAULT_MODE)

    # Normalize delta to three floats
    if not isinstance(delta, (list, tuple)) or len(delta) != 3:
        return _return_error(code="invalid_delta", message="delta must be an array of three numbers.", details=delta)

    if mode not in ("set", "add"):
        return _return_error(code="invalid_mode", message="mode must be 'set' or 'add'.", details=mode)

    if blender_exe is not None and not Path(blender_exe).is_file():
        return _return_error(
            code="blender_not_found",
            message="Blender executable was not found at the provided path.",
            details=blender_exe,
        )

    result = await anyio.to_thread.run_sync(run_blender_move_cube, cube_name, delta, blender_exe, mode)
    if result.get("ok", False):
        return result
    return _return_error(code=result["error"]["code"], message=result["error"]["message"], details=result["error"].get("details"))


async def main() -> None:
    initialization_options = InitializationOptions(
        server_name="mvp-mcp-stdio",
        server_version="0.1.0",
        capabilities=ServerCapabilities(tools=ToolsCapability(listChanged=False)),
        instructions="MVP Blender move-cube tool over MCP stdio.",
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options=initialization_options,
        )


if __name__ == "__main__":
    # Dev mode: when stdin is a TTY, avoid JSON-RPC parsing by running a local self-test.
    if sys.stdin.isatty():
        try:
            dev_result = run_blender_move_cube()
        except Exception as exc:  # pragma: no cover - defensive guard
            dev_result = _return_error("dev_exception", "Exception during dev self-test.", str(exc))

        print("MVP_DEV_RESULT=" + json.dumps(dev_result, separators=(",", ":")))
        sys.exit(0 if dev_result.get("ok") else 1)

    # Normal MCP stdio server for Claude Desktop.
    anyio.run(main)
