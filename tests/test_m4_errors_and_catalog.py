from __future__ import annotations

import sys
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.anyio
async def test_error_envelope_and_codes():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()

            denied = await client.call_tool("workspace.list_files", {"max_depth": 1})
            assert denied.isError
            assert denied.structuredContent["ok"] is False
            assert denied.structuredContent["error"]["code"] == "contract_required"

            # Capability missing
            await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "none",
                    "capabilities": [],
                    "tool_allowlist": ["runtime.probe"],
                },
            )
            cap_err = await client.call_tool("runtime.probe", {})
            assert cap_err.isError
            assert cap_err.structuredContent["error"]["code"] == "capability_required"


@pytest.mark.anyio
async def test_tools_catalog_available_without_contract():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            catalog = await client.call_tool("system.tools_catalog", {})
            assert not catalog.isError
            assert catalog.structuredContent["ok"] is True
            tools = catalog.structuredContent["result"]["tools"]
            assert any(t["name"] == "system.health" for t in tools)
            assert any(t["name"] == "contract.create" for t in tools)
