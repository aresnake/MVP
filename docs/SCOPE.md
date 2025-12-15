# SCOPE

## Goals
- Define v1 contracts, schemas, and policies for MCP Blender Core + Blender Bridge.
- Keep tool surface ≤35 and compose complexity as deterministic macros.
- Make version-awareness explicit (Blender version, host profile, feature flags).
- Define immutable banks/fingerprints for traceability and reproducibility.

## Non-goals (v1)
- No full runtime MCP server implementation.
- No HTTP bridge, sockets, or persistent background services.
- No “auto-magic” agents; orchestration must be contract-driven and testable.

## Out-of-scope
- Asset generation pipelines, full production UX, and provider orchestration details.
- Long-running scene watchers, passive learning, or telemetry pipelines.

## Future
- Implement Core runtime (stdio/HTTP) strictly from contracts.
- Implement Bridge execution + probes (headless first, UI optional).
- Add banks (ops/context/RNA) and deterministic macro library with tests.
