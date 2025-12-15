# TOOLING POLICY

## Tool count
- Maximum **35** first-class tools. Additional functionality must be deterministic macros.

## Naming
- Prefer domain.action (e.g. scene.snapshot, object.move).
- Keep names stable once published.

## Error model (mandatory)
All tools return:
- Success: { "ok": true, "result": { ... } }
- Failure: { "ok": false, "error": { "code": "...", "message": "...", "details": {...} } }

## Versioning
- Contracts and schemas are versioned (e.g. v1).
- Tools declare compatibility with Blender versions and optional capabilities.

## Deterministic macros
- Macros must be reproducible: same inputs + same contract + same scene state → same outputs.
- When non-determinism exists, it must be explicitly declared in the contract.
