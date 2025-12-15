"""
MCP tools exposed by the M0 stdio server.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from mcp.server.fastmcp import FastMCP

from . import __version__

IGNORED_NAMES = {".git", ".venv", "__pycache__"}


def register_tools(server: FastMCP, workspace_root: Path) -> None:
    """
    Register the M0 tools on the provided server.
    """

    @server.tool(name="system.health", description="Return basic health information for the MVP core.")
    def system_health() -> dict[str, object]:
        return {"ok": True, "name": "mvp", "version": __version__}

    @server.tool(name="echo", description="Echo the provided text.")
    def echo(text: str) -> str:
        return text

    @server.tool(
        name="workspace.list_files",
        description="List files under the workspace root up to a maximum depth.",
    )
    def workspace_list_files(max_depth: int = 3) -> dict[str, list[str]]:
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
        return {"files": files}
