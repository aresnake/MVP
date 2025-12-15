"""
MCP tools exposed by the M0 stdio server.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from mcp.server.fastmcp import FastMCP
from mcp import types

from . import __version__
from .contracts import Capability, SessionContract
from .errors import MvpErrorCode, err
from .runtime import (
    ExternalHttpRuntimeAdapter,
    NullRuntimeAdapter,
    get_runtime,
    runtime_error,
    set_runtime,
)
from .profiles import get_host_profile, get_runtime_profile

IGNORED_NAMES = {".git", ".venv", "__pycache__"}

_active_contract: SessionContract | None = None
_TOOLS_ALWAYS_ALLOWED = {"system.health", "echo", "contract.create", "contract.get_active", "system.tools_catalog"}
_CAPABILITY_REQUIREMENTS = {
    "runtime.probe": "DATA_ONLY",
    "scene.list_objects": "DATA_ONLY",
}
_RUNTIME_TOOLS = {"runtime.probe", "scene.list_objects"}


def _contract_error(code: str, message: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=message)],
        structuredContent=err(MvpErrorCode(code), message),
        isError=True,
    )


def _success_payload(data: object) -> types.CallToolResult:
    payload = {"ok": True, "result": data}
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(payload, indent=2))],
        structuredContent=payload,
        isError=False,
    )


def _maybe_gate(tool_name: str) -> types.CallToolResult | None:
    if tool_name in _TOOLS_ALWAYS_ALLOWED:
        return None

    if _active_contract is None:
        return _contract_error(MvpErrorCode.contract_required.value, "An active session contract is required.")

    if _active_contract.tool_allowlist is not None and tool_name not in _active_contract.tool_allowlist:
        return _contract_error("tool_not_allowed", f"Tool '{tool_name}' is not allowed by the active contract.")

    if required_cap := _CAPABILITY_REQUIREMENTS.get(tool_name):
        cap_values = {cap.value for cap in _active_contract.capabilities}
        if required_cap not in cap_values:
            return _contract_error(
                MvpErrorCode.capability_required.value,
                f"Capability '{required_cap}' is required by this tool.",
            )

    return None


def register_tools(server: FastMCP, workspace_root: Path) -> None:
    """
    Register the M0 tools on the provided server.
    """

    @server.tool(name="system.health", description="Return basic health information for the MVP core.")
    def system_health() -> types.CallToolResult:
        return _success_payload({"name": "mvp", "version": __version__})

    @server.tool(name="echo", description="Echo the provided text.")
    def echo(text: str) -> types.CallToolResult:
        return _success_payload(text)

    @server.tool(
        name="workspace.list_files",
        description="List files under the workspace root up to a maximum depth.",
    )
    def workspace_list_files(max_depth: int = 3) -> types.CallToolResult:
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
        return _success_payload({"files": files})

    @server.tool(
        name="contract.create",
        description="Create a session contract to gate subsequent tool calls.",
    )
    def contract_create(
        host_profile: str,
        runtime_profile: str,
        capabilities: list[str] | None = None,
        tool_allowlist: list[str] | None = None,
    ) -> types.CallToolResult:
        global _active_contract
        resolved: dict[str, object] = {}

        if host := get_host_profile(host_profile):
            resolved["host"] = host.model_dump()
            host_profile_name = host.name
        else:
            host_profile_name = host_profile

        if runtime := get_runtime_profile(runtime_profile):
            resolved["runtime"] = runtime.model_dump()
            runtime_profile_name = runtime.name
            if runtime.name == "mcpblender_http":
                base_url = os.getenv("MVP_RUNTIME_URL", runtime.base_url or "http://127.0.0.1:9876")
                set_runtime(ExternalHttpRuntimeAdapter(base_url))
        else:
            runtime_profile_name = runtime_profile

        try:
            _active_contract = SessionContract.create(
                host_profile=host_profile_name,
                runtime_profile=runtime_profile_name,
                capabilities=capabilities or [],
                tool_allowlist=tool_allowlist,
            )
            payload = _active_contract.model_dump(mode="json")
            if resolved:
                payload["resolved"] = resolved
            return _success_payload(payload)
        except ValueError as exc:
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=str(exc))],
                structuredContent=err(MvpErrorCode.invalid_request, str(exc)),
                isError=True,
            )

    @server.tool(
        name="contract.get_active",
        description="Return the active session contract, if any.",
    )
    def contract_get_active() -> types.CallToolResult:
        payload = _active_contract.model_dump(mode="json") if _active_contract else None
        return _success_payload(payload)

    @server.tool(
        name="runtime.probe",
        description="Probe the injected runtime for metadata.",
    )
    def runtime_probe() -> types.CallToolResult:
        adapter = get_runtime()
        try:
            return _success_payload(adapter.probe())
        except Exception as exc:  # pragma: no cover - guarded
            return runtime_error(str(exc))

    @server.tool(
        name="scene.list_objects",
        description="List objects in the active scene via the injected runtime.",
    )
    def scene_list_objects() -> types.CallToolResult:
        adapter = get_runtime()
        try:
            objects = adapter.list_scene_objects()
            return _success_payload({"objects": objects})
        except Exception as exc:  # pragma: no cover - guarded
            return runtime_error(str(exc))

    @server.tool(
        name="system.tools_catalog",
        description="List available tools and their gating metadata.",
    )
    def system_tools_catalog() -> types.CallToolResult:
        tools = []
        for tool in server._tool_manager.list_tools():
            name = tool.name
            tools.append(
                {
                    "name": name,
                    "description": tool.description,
                    "gating": {
                        "requires_contract": name not in _TOOLS_ALWAYS_ALLOWED,
                        "required_capabilities": [_CAPABILITY_REQUIREMENTS[name]]
                        if name in _CAPABILITY_REQUIREMENTS
                        else [],
                        "allowlist_respected": name not in _TOOLS_ALWAYS_ALLOWED,
                    },
                    "input_schema": tool.parameters,
                    "output_schema": tool.output_schema,
                }
            )
        return _success_payload({"tools": tools})

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
