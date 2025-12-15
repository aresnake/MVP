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
