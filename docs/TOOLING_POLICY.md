# Tooling Policy

## Tool surface
- Maximum 35 tools across MCP Blender Core; each tool must have a single, testable responsibility.
- Names use verb_noun, lowercase with underscores (e.g., `export_scene`, `apply_modifier`).
- Avoid overlapping scopes; prefer composition via host macros, not bloated tools.

## Error model
- Standard failure envelope: `{ ok: false, error: { code, message, details } }`.
- `code` is a stable, machine-friendly token; `message` is human-readable; `details` is structured and optional.
- Success responses must stay deterministic and versioned; no implicit fallbacks.

## Versioning
- Every tool, schema, and contract declares a version.
- Breaking changes require new versions; do not silently upgrade or mutate fingerprints.
- Hosts and bridge must negotiate supported versions before execution.

## Deterministic macros
- Higher-level flows are allowed only if they are deterministic, replayable, and documented as macros on top of the tool set.
- Macros must not expand the tool surface beyond the 35 limit; they orchestrate existing tools.
- Macro outputs must honor the same error model and versioning rules.
