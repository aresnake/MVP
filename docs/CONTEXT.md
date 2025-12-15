# MVP — CONTEXT (Source of Truth)

## Role
MVP is the core MCP orchestration engine.
It contains NO Blender code and NO bpy usage.

## Responsibilities
- Session contracts (creation, validation, gating)
- Tool gating (capabilities, allowlists)
- Host & runtime profiles
- Runtime adapters (none, inmemory, external_http)
- Transports: stdio (default), http (optional)

## Non-Goals
- No modeling logic
- No Blender operators
- No asset generation
- No UI responsibilities

## Runtime Targets
- MCPBLENDER runtime via HTTP (data-only)
- External runtimes must expose stable HTTP APIs

## Architecture Invariants
- Data-first
- Error schema v1
- Envelopes: { ok: true, result } | { ok: false, error }
- Strict separation: core vs runtime

## Current Milestones
- M7: contracts + runtime boundary ✅
- M8: external HTTP runtime adapter (MCPBLENDER) ✅
- M9: modeling orchestration (planned)

## How to Run
See README.md and docs/INTEGRATION_*.md

## Source of Truth
This file defines what MVP IS and IS NOT.
