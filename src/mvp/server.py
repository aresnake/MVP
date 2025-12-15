"""
Minimal MCP stdio server exposing the M0 tool surface.
"""

from __future__ import annotations

import logging
import sys
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
