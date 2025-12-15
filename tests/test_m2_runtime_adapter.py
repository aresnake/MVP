from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.anyio
async def test_runtime_probe_requires_contract_and_capability_and_runtime():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()

            # No contract yet -> denied
            denied = await client.call_tool("runtime.probe", {})
            assert denied.isError
            assert denied.structuredContent["error"]["code"] == "contract_required"

            # Contract created but default runtime is null -> runtime unavailable
            await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "none",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["runtime.probe", "scene.list_objects"],
                },
            )
            unavailable = await client.call_tool("runtime.probe", {})
            assert unavailable.isError
            assert unavailable.structuredContent["error"]["code"] == "runtime_unavailable"


@pytest.mark.anyio
async def test_scene_list_objects_with_inmemory_runtime():
    env = dict(os.environ)
    env["MVP_RUNTIME"] = "inmemory"
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "inmemory",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["runtime.probe", "scene.list_objects"],
                },
            )
            probe = await client.call_tool("runtime.probe", {})
            assert not probe.isError
            assert probe.structuredContent["result"]["name"] == "in-memory-runtime"

            listed = await client.call_tool("scene.list_objects", {})
            assert not listed.isError
            names = {obj["name"] for obj in listed.structuredContent["result"]["objects"]}
            assert {"Cube", "Camera"} <= names
