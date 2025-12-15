from __future__ import annotations

import sys
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.anyio
async def test_contract_gates_tools_and_allows_with_allowlist():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()

            # Without a contract, workspace.list_files should be rejected
            denied = await client.call_tool("workspace.list_files", {"max_depth": 1})
            assert denied.isError
            assert denied.structuredContent["error"]["code"] == "contract_required"

            # Create a contract that allows workspace.list_files
            created = await client.call_tool(
                "contract.create",
                {
                    "host_profile": "host-a",
                    "runtime_profile": "rt-a",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["workspace.list_files"],
                },
            )
            assert not created.isError
            contract = created.structuredContent["result"]
            assert contract["host_profile"] == "host-a"
            assert contract["runtime_profile"] == "rt-a"
            assert contract["contract_id"]
            assert contract["created_at"]

            # Now the tool should succeed
            allowed = await client.call_tool("workspace.list_files", {"max_depth": 1})
            assert not allowed.isError
            assert isinstance(allowed.structuredContent["result"]["files"], list)
