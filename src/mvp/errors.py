"""
Error schema v1 for the MVP core.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class MvpErrorCode(str, Enum):
    contract_required = "contract_required"
    tool_not_allowed = "tool_not_allowed"
    capability_required = "capability_required"
    runtime_unavailable = "runtime_unavailable"
    invalid_request = "invalid_request"
    internal_error = "internal_error"


class MvpError(BaseModel):
    code: MvpErrorCode
    message: str
    details: dict | None = None
    hint: str | None = None
    retryable: bool = False


def err(
    code: MvpErrorCode,
    message: str,
    *,
    details: dict | None = None,
    hint: str | None = None,
    retryable: bool = False,
) -> dict[str, Any]:
    error = MvpError(code=code, message=message, details=details, hint=hint, retryable=retryable)
    return {"ok": False, "error": error.model_dump()}
