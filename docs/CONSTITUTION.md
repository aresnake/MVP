1. Strict separation: LLM host ≠ MCP core ≠ Blender runtime
2. MCP tool surface must remain minimal and stable (≤ 35 tools)
3. MCP tools are interfaces, never business logic
4. All execution is data-first by default
5. Blender ops are optional accelerators, never dependencies
6. Every execution requires an explicit session contract
7. Knowledge lives in immutable banks, versioned by fingerprint
8. Search is mandatory: the LLM never sees the full bank
9. UI live execution is opt-in via contract only
10. Learning is structured: capture → candidate → validation → tests → publish

Any feature violating these rules must not be implemented.
