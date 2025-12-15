"""
Profiles registry (host/runtime) used by session contracts.
"""

from __future__ import annotations

from typing import Dict, Iterable

from pydantic import BaseModel, Field


class HostProfile(BaseModel):
    name: str
    transport: str
    limits: dict | None = Field(default=None)


class RuntimeProfile(BaseModel):
    name: str
    mode: str
    version: str
    base_url: str | None = None


_HOST_PROFILES: Dict[str, HostProfile] = {
    "codex_stdio": HostProfile(name="codex_stdio", transport="stdio"),
}

_RUNTIME_PROFILES: Dict[str, RuntimeProfile] = {
    "none": RuntimeProfile(name="none", mode="data_only", version="0"),
    "inmemory": RuntimeProfile(name="inmemory", mode="data_only", version="0"),
    "mcpblender_http": RuntimeProfile(
        name="mcpblender_http",
        mode="data_only",
        version="0",
        base_url="http://127.0.0.1:9876",
    ),
}


def get_host_profile(name: str) -> HostProfile | None:
    return _HOST_PROFILES.get(name)


def get_runtime_profile(name: str) -> RuntimeProfile | None:
    return _RUNTIME_PROFILES.get(name)


def list_host_profiles() -> Iterable[HostProfile]:
    return _HOST_PROFILES.values()


def list_runtime_profiles() -> Iterable[RuntimeProfile]:
    return _RUNTIME_PROFILES.values()
