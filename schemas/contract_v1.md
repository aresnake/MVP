# MCP Blender Contract v1 (Spec-Only)

## Session contract (MUST unless noted)
- `contract_version` (MUST): `"1.0.0"` for this spec.
- `session_id` (MUST): stable identifier for the session; host-generated.
- `host_profile` (MUST): client name/version, capabilities, feature flags, supported tool versions.
- `blender_profile` (MUST): Blender version string, build hash (if available), platform, supported features.
- `capabilities` (MUST): declared support for tools, macros, version negotiation, logging/audit.
- `tool_registry_ref` (MUST): pointer to registry version (e.g., `tool_registry_v1.yaml` + hash/fingerprint).
- `macro_registry_ref` (SHOULD): pointer to macro registry version + hash/fingerprint.
- `constraints` (MUST): resource ceilings (memory, time per tool, temp storage), and safety rails.
- `limits` (MUST): tool surface cap (≤35), maximum concurrent calls, maximum payload size.
- `audit` (SHOULD): requested audit verbosity, redaction rules, and sink identifiers (no stack traces in tool output).
- `fingerprints` (MUST): immutable identifiers for contract artifacts (tools, macros, schemas).
- `ui_optional` (MUST): boolean flag; headless-first. UI rendering is derived from the contract, not required for execution.

## Negotiation
- Inputs: `host_profile`, `blender_profile`, `capabilities`, requested `tool_registry_ref`/`macro_registry_ref`.
- Compatibility: host and bridge agree on contract_version and a compatible Blender version range; mismatches require refusal.
- Feature flags: negotiated as a set intersection; unsupported flags must be rejected explicitly.
- Tool/macros: only tools/macros present in the agreed registry refs may be invoked; others must be refused.
- Limits: host proposals may be tightened by the bridge; resulting limits are part of the contract.
- Refusal: if compatibility fails (version, capabilities, registry mismatch, constraints exceeded), the bridge MUST refuse and emit `ok:false` with `error.code="contract_violation"` and structured `details`.

## Behavior
- Deterministic, data-first; no reliance on UI context or implicit selection.
- UI is optional; headless execution is primary. Any UI projection must be contract-derived.
- Immutable fingerprints: registries, schemas, and macros are addressed by version + hash; mutations create new fingerprints.
- Logging/audit: contract defines which fields are logged; tool outputs exclude stack traces and private data.
