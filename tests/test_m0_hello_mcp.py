from __future__ import annotations

import sys
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from mvp import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.anyio
async def test_m0_server_serves_tools_and_responds():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:

            init_result = await client.initialize()
            assert init_result.serverInfo.name == "mvp"
            assert init_result.serverInfo.version == __version__

            tools_result = await client.list_tools()
            tool_names = {tool.name for tool in tools_result.tools}
            assert {"system.health", "echo", "workspace.list_files"} <= tool_names

            health_result = await client.call_tool("system.health", {})
            assert not health_result.isError
            assert health_result.structuredContent["ok"] is True
            assert health_result.structuredContent["name"] == "mvp"
            assert health_result.structuredContent["version"] == __version__

            echo_result = await client.call_tool("echo", {"text": "ping"})
            echoed_texts = [block.text for block in echo_result.content if hasattr(block, "text")]
            assert "ping" in echoed_texts

            created_contract = await client.call_tool(
                "contract.create",
                {
                    "host_profile": "host-m0",
                    "runtime_profile": "rt-m0",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["workspace.list_files"],
                },
            )
            assert not created_contract.isError
            assert created_contract.structuredContent["contract_version"] == "1.0"

            list_result = await client.call_tool("workspace.list_files", {"max_depth": 1})
            assert not list_result.isError
            files = list_result.structuredContent["files"]
            assert any(path.endswith("pyproject.toml") for path in files)
            for path in files:
                parts = Path(path).parts
                assert ".git" not in parts
                assert ".venv" not in parts
                assert "__pycache__" not in parts
