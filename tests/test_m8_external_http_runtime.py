from __future__ import annotations

import json
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _MockRuntimeHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        match self.path:
            case "/health":
                self._send_json({"ok": True, "result": {"name": "mock-runtime", "version": "0.0.0"}})
            case "/runtime/probe":
                self._send_json({"ok": True, "result": {"name": "mock-runtime", "version": "0.0.0"}})
            case "/scene/objects":
                self._send_json({"ok": True, "result": {"objects": [{"name": "Cube"}, {"name": "Camera"}]}})
            case _:
                self.send_error(404)


def _start_mock_runtime_server(port: int):
    server = HTTPServer(("127.0.0.1", port), _MockRuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.mark.anyio
async def test_external_http_runtime_happy_path():
    port = _free_port()
    server = _start_mock_runtime_server(port)
    env = dict(os.environ)
    env["MVP_RUNTIME"] = "external_http"
    env["MVP_RUNTIME_URL"] = f"http://127.0.0.1:{port}"

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "mcpblender_http",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["runtime.probe", "scene.list_objects"],
                },
            )
            probe = await client.call_tool("runtime.probe", {})
            assert not probe.isError
            assert probe.structuredContent["result"]["name"] == "mock-runtime"

            listed = await client.call_tool("scene.list_objects", {})
            assert not listed.isError
            names = {obj["name"] for obj in listed.structuredContent["result"]["objects"]}
            assert {"Cube", "Camera"} <= names
    server.shutdown()


@pytest.mark.anyio
async def test_external_http_runtime_unavailable():
    port = _free_port()
    # do not start server to force unavailable
    env = dict(os.environ)
    env["MVP_RUNTIME"] = "external_http"
    env["MVP_RUNTIME_URL"] = f"http://127.0.0.1:{port}"

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mvp.server"],
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            await client.call_tool(
                "contract.create",
                {
                    "host_profile": "codex_stdio",
                    "runtime_profile": "mcpblender_http",
                    "capabilities": ["DATA_ONLY"],
                    "tool_allowlist": ["runtime.probe"],
                },
            )
            probe = await client.call_tool("runtime.probe", {})
            assert probe.isError
            assert probe.structuredContent["error"]["code"] == "runtime_unavailable"
