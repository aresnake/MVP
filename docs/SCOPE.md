# Scope — v1

## Goals
- Deliver contract-first definitions for MCP Blender Core and the Blender Bridge.
- Keep tool surface ≤35 with clear naming, semantics, and error contracts.
- Enforce data-first flows with immutable fingerprints and version-aware schemas.
- Make UI optional by ensuring every interaction is defined via contract.
- Provide clarity for host integration: LLM host ↔ MCP core ↔ bridge ↔ Blender.

## Non-goals
- No autonomous agent logic or planner baked into the core.
- No Blender UI implementation or custom panels.
- No bundling of Blender inside the MCP server.
- No business logic or creative “auto-magic” inside tools.

## Out-of-scope
- Networked asset stores or cloud sync features.
- Proprietary render pipelines or studio-specific tooling.
- Security hardening beyond contract-level guardrails.
- Performance tuning for large scenes.

## Future (tracked, not for v1)
- Deterministic macro library layered atop the core tool set.
- Versioned knowledge banks with promotion workflows.
- Hosted observability and policy enforcement.
- UI scaffolding that renders directly from the contracts.
