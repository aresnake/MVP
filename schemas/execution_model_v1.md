# Execution Model v1 (Spec-Only)

## Overview
- Applies to MCP Blender Core executions negotiated via `contract_v1`.
- Headless-first: UI actions are optional and MUST be gated by explicit contract flags; default is no UI use.
- Pipeline: contract → tool calls → (optional) macros → bridge → Blender → return via error model v1.

## Phases (per tool call)
1) Validate input (schema + contract): reject with `invalid_arguments` on failure.
2) Check contract/capabilities: ensure tool is in the negotiated registry, limits honored, capabilities present; else refuse with `contract_violation` or `capability_missing`.
3) Plan (optional): pre-flight checks (e.g., existence of objects/materials) without side effects.
4) Execute: perform deterministic, data-first operations (no UI context, no implicit selection).
5) Snapshot/verify (optional but recommended): minimal verification (e.g., read-back of transforms) within time budget.
6) Return: respond using error model v1; no stack traces; include determinism class if applicable.

## Atomicity and idempotency
- Tool calls MUST be atomic at the tool level: either all side effects apply or none, within negotiated limits.
- Macros define step boundaries; if a step fails, later steps MUST NOT execute. Rollback MAY be defined; if absent, partial effects are allowed but must be reported.
- Idempotency MUST be declared per tool; repeated identical calls should converge or be explicitly non-idempotent.

## Timeouts and cancellation
- Each tool call observes a negotiated timeout (from contract limits). On timeout, respond with `timeout`; partial effects MUST be documented in `details`.
- Cancellation requests (if supported) MUST stop further side effects as soon as feasible and return `timeout` or `internal_error` with `details.cancelled=true`.

## Refusal rules
- `contract_violation`: tool/macros not in registry, exceeds limits, or violates constraints/fingerprints.
- `capability_missing`: required capability absent from host/bridge/blender profile.
- `unsupported_blender_version`: outside declared `blender_min`/`blender_max`.
- Refusals use the error envelope and MUST avoid side effects.

## Determinism
- Tools and macros MUST declare determinism class (see `determinism_rules_v1`). If seeds are required, they must be inputs and echoed back.
- Outputs SHOULD include fingerprints when state snapshots are returned.
