"""
Runtime adapter boundary (no real runtime in MVP).
"""

from __future__ import annotations

from typing import Protocol

from mcp import types

import httpx

from .errors import MvpErrorCode, err


class RuntimeUnavailableError(Exception):
    """Raised when a runtime adapter cannot serve a request."""


class RuntimeAdapter(Protocol):
    def probe(self) -> dict:
        """Return runtime metadata."""
        ...

    def list_scene_objects(self) -> list[dict]:
        """List scene objects in the active document/scene."""
        ...


class NullRuntimeAdapter:
    """Default adapter that signals no runtime is available."""

    def probe(self) -> dict:
        raise RuntimeUnavailableError("Runtime unavailable")

    def list_scene_objects(self) -> list[dict]:
        raise RuntimeUnavailableError("Runtime unavailable")


class InMemoryRuntimeAdapter:
    """In-memory adapter useful for tests."""

    def __init__(
        self,
        *,
        name: str = "in-memory-runtime",
        version: str = "0.0.0",
    ):
        self._meta = {"name": name, "version": version}
        self._objects = [
            {"id": "obj-cube", "name": "Cube", "type": "MESH"},
            {"id": "obj-camera", "name": "Camera", "type": "CAMERA"},
        ]

    def probe(self) -> dict:
        return dict(self._meta)

    def list_scene_objects(self) -> list[dict]:
        return list(self._objects)


class ExternalHttpRuntimeAdapter:
    """HTTP runtime adapter for external MCP runtime (e.g., MCPBLENDER)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _get_json(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.get(url, timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise RuntimeUnavailableError(str(exc)) from exc

    def probe(self) -> dict:
        data = self._get_json("/runtime/probe")
        if not isinstance(data, dict):
            raise RuntimeUnavailableError("Invalid response from runtime probe")
        return data.get("result", data)

    def list_scene_objects(self) -> list[dict]:
        data = self._get_json("/scene/objects")
        if not isinstance(data, dict):
            raise RuntimeUnavailableError("Invalid response from scene objects")
        objects = data.get("result", data.get("objects", data))
        if isinstance(objects, dict) and "objects" in objects:
            objects = objects["objects"]
        if not isinstance(objects, list):
            raise RuntimeUnavailableError("Invalid objects payload")
        return objects


_runtime_adapter: RuntimeAdapter = NullRuntimeAdapter()


def set_runtime(adapter: RuntimeAdapter) -> None:
    global _runtime_adapter
    _runtime_adapter = adapter


def get_runtime() -> RuntimeAdapter:
    return _runtime_adapter


def runtime_error(message: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=message)],
        structuredContent=err(MvpErrorCode.runtime_unavailable, message),
        isError=True,
    )
