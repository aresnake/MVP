# MCP Blender Core

Standard MCP stack for Blender, built contract-first and data-first to let any LLM host drive Blender deterministically.

## Product definition
- **MCP Blender Core**: the MCP server exposing Blender contracts, tools, and schemas; no Blender embedding, no UI.
- **Blender Bridge**: the thin Blender-side connector that speaks the contracts and enforces immutable data fingerprints.

## Principles
- Contract-first, data-first; UI is optional and derived from the contract.
- Tool surface capped at 35 to keep coordination and audits tractable.
- Immutable knowledge banks and fingerprints; reproducible runs.
- No autonomous agent logic or hidden behaviors.

## Status
Pre-design. No runtime or bridge committed yet.

## Legacy repos (historical reference)
- https://github.com/aresnake/MCPBLA-mirror
- https://github.com/aresnake/MCPBLENDER
