# Scene State v1 (Spec-Only)

## Snapshot structure
- `snapshot_version` (MUST): `"1.0.0"` for this schema.
- `scene_id` (MUST): stable identifier for the scene.
- `scene_name` (MUST): human-readable name.
- `blender_version` (MUST): version string; MAY include build hash.
- `timestamp` (SHOULD): ISO-8601 UTC.
- `objects` (MUST): array of:
  - `name` (MUST): stable identifier; MAY include `uuid` (SHOULD if available).
  - `type` (MUST): mesh/light/camera/empty/etc.
  - `transform` (MUST): `{ location: [x,y,z], rotation_euler: [rx,ry,rz], scale: [sx,sy,sz] }`.
  - `collections` (SHOULD): array of collection names.
  - `materials` (SHOULD): array of material names assigned.
  - `data_fingerprint` (SHOULD): hash of object data (e.g., mesh topology) for change detection.
- `collections` (SHOULD): array of `{ name, parent, children }`.
- `materials` (SHOULD): array of `{ name, type?, properties? }`.
- `indices` (SHOULD): compact lookup tables:
  - `by_name`: mapping name → object summary
  - `by_collection`: mapping collection → object names
  - `by_material`: mapping material → object names
- `fingerprint` (SHOULD): hash of canonicalized snapshot (ordering and floats normalized).

## Canonicalization
- Order arrays deterministically (e.g., sort by name).
- Normalize floats (e.g., fixed precision) before hashing.
- Include schema version and blender_version in the fingerprint preimage.

## Guidance
- Tools returning snapshots SHOULD use this shape or a subset.
- For partial snapshots, include `fingerprint` only if the preimage is well-defined.
- Avoid UI-only state; selection/active is represented as data, not UI context.
