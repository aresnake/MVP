# Product Definition — MCP Blender Core
MCP Blender Core is the contract-first backend that lets LLM hosts operate Blender deterministically without embedding Blender in the server.
The system is split into two artifacts to keep responsibilities clean and auditable.
1) MCP Blender Core: an MCP server that exposes Blender contracts, schemas, and tools; it never bundles Blender or UI logic.
2) Blender Bridge: a minimal Blender-side connector that executes those contracts and enforces immutable fingerprints for data exchange.
The goal is to make Blender automation predictable, replayable, and version-aware for any LLM host.
All behavior is driven by explicit contracts and schemas; no “magic addon” or hidden flows.
Data-first: every action is described by structured inputs/outputs; UI surfaces are optional projections of the contract.
Tool surface is deliberately capped at 35 to keep reasoning, review, and compliance manageable.
The bridge only implements what the contract states; it cannot invent behaviors or bypass fingerprints.
Knowledge banks are immutable; updates create new versions with fingerprints, never in-place mutation.
Version-awareness is built in: contracts, schemas, tools, and fingerprints must declare and honor versions.
Determinism is prioritized over breadth; macros or higher-level flows must be reproducible.
Security posture assumes untrusted hosts: explicit permissions, no ad-hoc file writes, and clear error contracts.
Observability is contract-bound: logs and traces map to contract identifiers, not ad-hoc strings.
The system is currently pre-design; no runtime exists yet and no bridge code is committed.
Success is measured by clarity of contracts, stability of schemas, and bounded tool count.
Legacy references remain available for context but are not authoritative.
This document is the authoritative product snapshot for v1 planning.
