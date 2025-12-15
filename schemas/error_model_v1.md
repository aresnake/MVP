# Error Model v1 (Normative)

## Envelope
- Success: `{ "ok": true, "result": { ... } }`
- Failure: `{ "ok": false, "error": { "code": "<token>", "message": "<human-readable>", "details": { ... } } }`
- `code` is stable and machine-friendly; `message` is concise and non-sensitive; `details` is structured, optional, and redaction-safe.

## Error codes (taxonomy)
- `invalid_arguments`: schema/validation failure, missing or malformed inputs.
- `capability_missing`: requested feature not supported by host/bridge/Blender profile.
- `unsupported_blender_version`: version outside declared bounds.
- `contract_violation`: tool/macro call outside negotiated contract/limits/registry.
- `not_found`: referenced entity absent (object/material/collection).
- `execution_failed`: deterministic execution failure inside Blender.
- `timeout`: exceeded negotiated time limit.
- `internal_error`: unexpected bridge-side error that is not actionable by the host.

## Rules
- Never return stack traces in `message`; if needed, place redacted technical hints in `details`.
- `details` SHOULD be structured (e.g., `{ "field": "delta", "reason": "out_of_range" }`).
- Audit/log fields are separate from tool outputs; contract defines log sinks and redaction. Tool responses remain minimal.
- Macros propagate underlying tool errors; they MAY wrap with additional context in `details.context`.
