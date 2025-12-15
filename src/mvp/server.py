"""
Minimal MCP stdio server exposing the M0 tool surface.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import anyio
from mcp import types
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import __version__
from .errors import MvpErrorCode, err
from .runtime import ExternalHttpRuntimeAdapter, InMemoryRuntimeAdapter, set_runtime
from .tools import register_tools


def build_server(workspace_root: Path | None = None) -> FastMCP:
    """
    Construct the FastMCP server with the M0 tool surface.
    """
    server = FastMCP(name="mvp", log_level="INFO")
    # FastMCP does not expose a version argument; set it directly for the handshake.
    server._mcp_server.version = __version__  # type: ignore[attr-defined]

    root = workspace_root or Path(__file__).resolve().parents[2]
    register_tools(server, root)
    return server


async def _call_tool_http(server: FastMCP, name: str, params: dict | None) -> dict:
    try:
        request = types.CallToolRequest(
            params=types.CallToolRequestParams(name=name, arguments=params or {}),
        )
        handler = server._mcp_server.request_handlers.get(types.CallToolRequest)
        if handler is None:
            return err(MvpErrorCode.internal_error, "CallTool handler not available")
        server_result = await handler(request)
        result = server_result.root
        if isinstance(result, types.CallToolResult) and result.structuredContent:
            return result.structuredContent
        return err(MvpErrorCode.internal_error, "Unexpected tool result")
    except Exception as exc:
        return err(MvpErrorCode.internal_error, str(exc))


def _http_app(server: FastMCP) -> Starlette:
    async def health(_: Request):
        payload = await _call_tool_http(server, "system.health", {})
        return JSONResponse(payload)

    async def tools(_: Request):
        payload = await _call_tool_http(server, "system.tools_catalog", {})
        return JSONResponse(payload)

    async def contract_create(request: Request):
        body = await request.json()
        payload = await _call_tool_http(server, "contract.create", body or {})
        return JSONResponse(payload)

    async def call(request: Request):
        body = await request.json()
        name = body.get("name")
        params = body.get("params") or {}
        if not name:
            return JSONResponse(err(MvpErrorCode.invalid_request, "Missing tool name"), status_code=400)
        payload = await _call_tool_http(server, name, params)
        return JSONResponse(payload)

    return Starlette(
        debug=False,
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/tools", tools, methods=["GET"]),
            Route("/contract/create", contract_create, methods=["POST"]),
            Route("/call", call, methods=["POST"]),
        ],
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    server = build_server()
    if os.getenv("MVP_RUNTIME", "").lower() == "inmemory":
        set_runtime(InMemoryRuntimeAdapter())
        logging.info("Using in-memory runtime adapter (MVP_RUNTIME=inmemory).")
    elif os.getenv("MVP_RUNTIME", "").lower() == "external_http":
        url = os.getenv("MVP_RUNTIME_URL", "http://127.0.0.1:9876")
        set_runtime(ExternalHttpRuntimeAdapter(url))
        logging.info("Using external HTTP runtime adapter at %s", url)
    transport = os.getenv("MVP_TRANSPORT", "stdio").lower()
    if transport == "http":
        host = "127.0.0.1"
        port = int(os.getenv("MVP_HTTP_PORT", "8765"))
        logging.info("Starting HTTP transport on http://%s:%s", host, port)
        app = _http_app(server)
        import uvicorn

        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        logging.info("MVP stdio server expects a MCP client (Claude Desktop, Codex, etc.). Waiting on stdio...")
        try:
            server.run(transport="stdio")
        except KeyboardInterrupt:
            logging.info("Received interrupt, shutting down.")
            sys.exit(130)
        except (BrokenPipeError, EOFError):
            logging.info("Stdio closed, exiting.")
        except Exception as exc:  # pragma: no cover - defensive guard
            logging.error("Server stopped unexpectedly: %s", exc)
            sys.exit(1)


if __name__ == "__main__":
    main()
