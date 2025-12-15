# ARCHITECTURE

## Components
- **LLM Host**: Claude Desktop / Codex / other MCP clients.
- **MCP Blender Core**: contracts, schemas, tool policy, planning/macro rules.
- **Blender Bridge**: Blender-coupled execution (headless/UI), version probe, snapshots.
- **Blender Runtime**: actual Blender scene state and datablocks.

## Flow
LLM Host ↔ (MCP protocol) ↔ MCP Blender Core ↔ (contract-approved calls) ↔ Blender Bridge ↔ Blender

## Contracts
- Session starts by negotiating: host profile + blender profile → **session contract**.
- Contract defines: allowed tool set, safety gates, deterministic macro rules, version constraints.

## Tool surface rule
- Hard cap: **≤35 tools**.
- Everything else is expressed as deterministic, versioned macros composed from these tools.

## Version-awareness
- Every response can include: blender_version, feature flags, and contract version.
- Tools/macros must declare compatibility and fail predictably when unsupported.
