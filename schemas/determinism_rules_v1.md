# Determinism Rules v1 (Spec-Only)

## Classes
- `deterministic`: same inputs → same outputs; no randomness.
- `deterministic_with_seed`: deterministic when provided a seed; seed MUST be an input and echoed in output.
- `nondeterministic`: outputs may vary; MUST be declared and justified; use sparingly.

## Requirements
- Tools and macros MUST declare their determinism class.
- For `deterministic_with_seed`, the seed MUST flow through: inputs → execution → outputs; no hidden RNG.
- Canonical ordering: collections, objects, materials, and arrays MUST be ordered deterministically (e.g., by name).
- Float tolerances: define comparison tolerance for verification (e.g., 1e-6); do not rely on UI rounding.
- Fingerprinting: when returning fingerprints, use canonicalized ordering and normalized floats.
- Macros propagate determinism: the macro class is the strictest of its steps; if any step is nondeterministic, the macro MUST declare nondeterministic.

## Reporting
- Outputs SHOULD include determinism class when relevant, especially for macros and snapshot-producing tools.
- Seeds (when used) MUST be echoed back to the caller.
