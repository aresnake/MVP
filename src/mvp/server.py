"""
Minimal MCP stdio server exposing the M0 tool surface.
"""

from __future__ import annotations

import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import __version__
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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
