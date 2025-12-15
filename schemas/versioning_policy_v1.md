# Versioning Policy v1

## Scope
- Applies to contracts, tool registry, macro registry, schemas, and fingerprints.

## Versions
- Use semantic versioning: MAJOR.MINOR.PATCH.
- Breaking changes increment MAJOR; additive, backward-compatible changes increment MINOR; fixes increment PATCH.

## Compatibility
- Contract negotiation requires exact `contract_version` match or declared compatibility matrix; absent matrix ⇒ exact match.
- Tools/macros include version identifiers; hosts must call versions they negotiated.
- Blender version-awareness: use version string (e.g., `"5.0.0"`) plus optional build hash. Each tool declares `blender_min` and optional `blender_max`.
- Fingerprints (hashes) pair with versions to prevent silent mutation; changing content requires new fingerprint (and usually a version bump).

## Deprecation
- Deprecate at MINOR with clear end-of-life; remove at next MAJOR.
- Deprecated items must remain functional until removal or until contract negotiation rejects them.

## Backporting and rollout
- Macro changes should follow tool availability; macros cannot depend on tools absent from the negotiated registry.
- Registries are immutable once published; updates create new registry files and fingerprints.

## Logging/Audit versioning
- Logging schemas follow the same versioning; audit sinks must tolerate additional fields but treat removals as breaking.
