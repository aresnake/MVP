"""
MCP tools exposed by the M0 stdio server.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from mcp.server.fastmcp import FastMCP
from mcp import types

from . import __version__
from .contracts import SessionContract
from .runtime import NullRuntimeAdapter, get_runtime, runtime_error

IGNORED_NAMES = {".git", ".venv", "__pycache__"}

_active_contract: SessionContract | None = None
_TOOLS_ALWAYS_ALLOWED = {"system.health", "echo", "contract.create", "contract.get_active"}
_CAPABILITY_REQUIREMENTS = {
    "runtime.probe": "DATA_ONLY",
    "scene.list_objects": "DATA_ONLY",
}
_RUNTIME_TOOLS = {"runtime.probe", "scene.list_objects"}


def _contract_error(code: str, message: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=message)],
        structuredContent={"code": code, "message": message},
        isError=True,
    )


def _success_payload(data: object) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
        structuredContent=data,
        isError=False,
    )


def _maybe_gate(tool_name: str) -> types.CallToolResult | None:
    if tool_name in _TOOLS_ALWAYS_ALLOWED:
        return None

    if _active_contract is None:
        return _contract_error("contract_required", "An active session contract is required.")

    if _active_contract.tool_allowlist is not None and tool_name not in _active_contract.tool_allowlist:
        return _contract_error("tool_not_allowed", f"Tool '{tool_name}' is not allowed by the active contract.")

    if required_cap := _CAPABILITY_REQUIREMENTS.get(tool_name):
        if required_cap not in _active_contract.capabilities:
            return _contract_error(
                "capability_required",
                f"Capability '{required_cap}' is required by this tool.",
            )

    return None


def register_tools(server: FastMCP, workspace_root: Path) -> None:
    """
    Register the M0 tools on the provided server.
    """

    @server.tool(name="system.health", description="Return basic health information for the MVP core.")
    def system_health() -> dict[str, object]:
        return {"ok": True, "name": "mvp", "version": __version__}

    @server.tool(name="echo", description="Echo the provided text.")
    def echo(text: str) -> str:
        return text

    @server.tool(
        name="workspace.list_files",
        description="List files under the workspace root up to a maximum depth.",
    )
    def workspace_list_files(max_depth: int = 3) -> dict[str, list[str]]:
        if max_depth < 0:
            raise ValueError("max_depth must be non-negative")

        files: list[str] = []
        root = workspace_root.resolve()

        def iter_paths(base: Path, depth: int) -> Iterable[Path]:
            for entry in base.iterdir():
                if entry.name in IGNORED_NAMES:
                    continue
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    if depth < max_depth:
                        yield from iter_paths(entry, depth + 1)
                elif entry.is_file():
                    yield entry

        for path in iter_paths(root, 0):
            files.append(path.relative_to(root).as_posix())

        files.sort()
        return {"files": files}

    @server.tool(
        name="contract.create",
        description="Create a session contract to gate subsequent tool calls.",
    )
    def contract_create(
        host_profile: str,
        runtime_profile: str,
        capabilities: list[str] | None = None,
        tool_allowlist: list[str] | None = None,
    ) -> SessionContract:
        global _active_contract
        _active_contract = SessionContract.create(
            host_profile=host_profile,
            runtime_profile=runtime_profile,
            capabilities=capabilities or [],
            tool_allowlist=tool_allowlist,
        )
        return _active_contract

    @server.tool(
        name="contract.get_active",
        description="Return the active session contract, if any.",
    )
    def contract_get_active() -> SessionContract | None:
        return _active_contract

    @server.tool(
        name="runtime.probe",
        description="Probe the injected runtime for metadata.",
    )
    def runtime_probe() -> types.CallToolResult:
        adapter = get_runtime()
        return _success_payload(adapter.probe())

    @server.tool(
        name="scene.list_objects",
        description="List objects in the active scene via the injected runtime.",
    )
    def scene_list_objects() -> types.CallToolResult:
        adapter = get_runtime()
        objects = adapter.list_scene_objects()
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(objects, indent=2))],
            structuredContent={"objects": objects},
            isError=False,
        )

    original_call_handler = server._mcp_server.request_handlers.get(types.CallToolRequest)

    async def gated_call_tool(req: types.CallToolRequest):
        tool_name = req.params.name
        if error := _maybe_gate(tool_name):
            return types.ServerResult(error)
        if tool_name in _RUNTIME_TOOLS and isinstance(get_runtime(), NullRuntimeAdapter):
            return types.ServerResult(runtime_error("Runtime unavailable"))
        assert original_call_handler is not None
        return await original_call_handler(req)

    server._mcp_server.request_handlers[types.CallToolRequest] = gated_call_tool
