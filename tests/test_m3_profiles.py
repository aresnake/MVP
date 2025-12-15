from __future__ import annotations

import sys
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.anyio
async def test_profiles_resolve_and_capabilities_are_versioned():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            created = await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "inmemory",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["runtime.probe"],
                },
            )
            assert not created.isError
            contract = created.structuredContent
            assert contract["contract_version"] == "1.0"
            assert "DATA_ONLY" in contract["capabilities"]
            assert contract["host_profile"] == "codex_stdio"
            assert contract["runtime_profile"] == "inmemory"
            assert contract["resolved"]["host"]["transport"] == "stdio"
            assert contract["resolved"]["runtime"]["mode"] == "data_only"


@pytest.mark.anyio
async def test_capability_hierarchy_enforced():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            result = await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "inmemory",
                    "capabilities": ["UI_LIVE"],
                },
            )
            assert result.isError
            assert any("UI_LIVE requires DATA_ONLY" in block.text for block in result.content if hasattr(block, "text"))
