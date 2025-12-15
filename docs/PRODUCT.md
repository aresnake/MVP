# PRODUCT (Official)

MVP defines a spec-first, contract-driven “MCP Blender” system split into two parts:
(1) MCP Blender Core and (2) Blender Bridge.

MCP Blender Core is the stable, host-agnostic layer:
- defines contracts, schemas, tool policies, version-awareness, and deterministic macros;
- exposes a small, curated tool surface (≤35);
- guarantees predictable results with an explicit error model.

Blender Bridge is the Blender-coupled execution layer:
- runs inside Blender (headless or UI);
- executes contract-approved actions using data-first APIs when possible;
- provides version-aware capabilities and scene snapshots.

The product goal is reliability and standardization across LLM hosts:
host profile × blender profile → negotiated contract → deterministic execution.
