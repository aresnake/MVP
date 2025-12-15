# Architecture — MCP Blender Core

## Components
- LLM Host: orchestrates prompts and calls MCP tools.
- MCP Blender Core: MCP server exposing Blender contracts, schemas, and tools (no Blender embedding).
- Blender Bridge: minimal connector inside Blender that executes contracts and enforces fingerprints.
- Blender Runtime: vanilla Blender plus bridge hooks; no extra UI unless derived from contracts.

## Flow (spec-first)
1) Host calls a contract-defined tool on MCP Blender Core.
2) Core validates input against versioned schemas and forwards canonical requests to the bridge.
3) Bridge maps the request to Blender APIs, produces versioned outputs with fingerprints, and returns results.
4) Core returns structured responses to the host using the shared error model.

## Contracts
- Every tool has explicit schemas, versions, expected side effects, and fingerprint rules.
- UI surfaces are generated or omitted based solely on contracts; no hidden behaviors.
- Observability links to contract IDs for deterministic replay.

## Tool surface rule
- Hard cap at 35 tools; each must be focused, composable, and deterministic.
- Tools prefer data transforms over imperative “do everything” commands.

## Version awareness
- Contracts, schemas, tool versions, and fingerprints must declare versions.
- Bridge must reject mismatched versions or unsupported capabilities.
- Hosts must negotiate supported versions before executing tools.

## Status
- Pre-design: no runtime, server, or bridge code is committed yet.
