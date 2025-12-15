"""
Session contract model used to gate tool execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Set
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Capability(str, Enum):
    DATA_ONLY = "DATA_ONLY"
    UI_LIVE = "UI_LIVE"


class SessionContract(BaseModel):
    contract_id: str = Field(description="Unique identifier for the session contract (uuid4).")
    contract_version: str = Field(default="1.0", description="Contract schema version.")
    created_at: str = Field(description="ISO8601 timestamp of contract creation.")
    host_profile: str = Field(description="Host profile identifier.")
    runtime_profile: str = Field(description="Runtime profile identifier.")
    capabilities: Set[Capability] = Field(default_factory=set, description="Enabled capabilities.")
    tool_allowlist: list[str] | None = Field(
        default=None,
        description="Optional list of allowed tool names. If set, only these tools may run.",
    )

    @field_validator("capabilities")
    @classmethod
    def _validate_capabilities(cls, value: Iterable[str | Capability]) -> Set[Capability]:
        caps: Set[Capability] = {Capability(cap) for cap in (value or [])}
        if Capability.UI_LIVE in caps and Capability.DATA_ONLY not in caps:
            raise ValueError("UI_LIVE requires DATA_ONLY capability.")
        return caps

    @classmethod
    def create(
        cls,
        *,
        host_profile: str,
        runtime_profile: str,
        capabilities: Iterable[str] | None = None,
        tool_allowlist: list[str] | None = None,
    ) -> "SessionContract":
        return cls(
            contract_id=str(uuid4()),
            contract_version="1.0",
            created_at=datetime.now(tz=timezone.utc).isoformat(),
            host_profile=host_profile,
            runtime_profile=runtime_profile,
            capabilities=set(capabilities or []),
            tool_allowlist=tool_allowlist,
        )
