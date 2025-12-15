# MVP — MCP Blender (Spec-first)

This repository is a spec-first MVP for an industrial-grade **MCP Blender** stack.

## Product split
- **MCP Blender Core**: MCP-facing contracts, schemas, tool policy, version-awareness, and deterministic macro rules.
- **Blender Bridge**: Blender-coupled execution layer (addon/bridge), driven by contracts. UI is optional via contract.

## Principles
- **Contract-first**: define contracts and error model before runtime.
- **Data-first**: prefer deterministic data APIs; ops/UI is optional and gated by contract.
- **Tool surface ≤ 35**: curated, stable tools; everything else is composed as macros.
- **Immutable banks/fingerprints**: reproducibility, traceability, versioned profiles.

## Status
**Pre-design / spec-first.** No runtime server/bridge implementation is included yet.

## Legacy / history
This repo replaces earlier experimental repos/branches; the MVP is now intentionally spec-first to avoid divergence.

See:
- docs/PRODUCT.md
- docs/SCOPE.md
- docs/ARCHITECTURE.md
- docs/TOOLING_POLICY.md

## Run M0
- Install deps (editable optional): `python -m pip install -e .`
- Dev deps (lint/tests): `python -m pip install -e ".[dev]"`
- Start the stdio server (waits for a MCP client and prints a hint): `python -m mvp.server`
- Run tests: `python -m pytest -q`

If you run `python -m mvp.server` directly in a shell, it will log a short reminder that it expects a MCP client and then wait; closing stdin or pressing Ctrl+C exits cleanly.

## Session Contracts
- Tools are gated until a session contract exists. Without one, only `system.health`, `echo`, and `contract.create/get_active` are allowed; other tools return `code: contract_required`.
- Create a contract by calling `contract.create` with `host_profile`, `runtime_profile`, optional `capabilities` (DATA_ONLY/UI_LIVE), and optional `tool_allowlist`.
- When `tool_allowlist` is set, only listed tools run; others return `code: tool_not_allowed`.
- Example (PowerShell + MCP client): start server with `python -m mvp.server`, then from the client call `contract.create` with `{"host_profile":"dev","runtime_profile":"rt","capabilities":["DATA_ONLY"],"tool_allowlist":["workspace.list_files"]}` before invoking `workspace.list_files`.

## Runtime Adapter
- MVP ships with no real runtime; adapters are injected.
- Default adapter is null and returns `runtime_unavailable`; runtime tools are still gated by session contracts and capabilities (DATA_ONLY).
- An in-memory adapter is available for tests/dev via `MVP_RUNTIME=inmemory` environment variable when starting the server; real runtimes (e.g., Blender) would live outside this core.

## Profiles
- Built-in host profile: `codex_stdio` (transport `stdio`). Built-in runtime profiles: `none` (data_only) and `inmemory` (data_only, for dev/tests).
- `contract.create` will validate/resolve known profile names and include a `resolved` section in its response when matches are found.

## Contracts v1.0
- Contracts now include `contract_version` (defaults to `1.0`) and strict capabilities (`DATA_ONLY`, `UI_LIVE`). `UI_LIVE` requires `DATA_ONLY`.
- Capabilities drive gating alongside allowlists; runtime tools require `DATA_ONLY`.

## Error schema v1
- All tool responses use `{ "ok": true, "result": ... }` on success and `{ "ok": false, "error": { code, message, details?, hint?, retryable } }` on failure.
- Stable error codes: `contract_required`, `tool_not_allowed`, `capability_required`, `runtime_unavailable`, `invalid_request`, `internal_error`.

## Tool catalog
- `system.tools_catalog` (not gated) lists available tools with descriptions, gating flags (requires contract, required capabilities, allowlist respected), and minimal input/output schemas.
