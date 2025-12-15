# Macro Registry v1 (Spec-Only)

## Macro definition (normative fields)
- `macro_name` (MUST)
- `version` (MUST)
- `inputs` (MUST): schema-like description of required parameters.
- `preconditions` (SHOULD): required capabilities, registry versions, scene assumptions.
- `steps` (MUST): ordered list of tool calls with arguments templated from inputs.
- `postconditions` (SHOULD): expected state assertions (e.g., object exists at location).
- `rollback` (MAY): deterministic undo path if a step fails.
- `determinism` (MUST): declaration of determinism scope and allowed variability.
- `fingerprint` (SHOULD): hash of the macro spec for immutability.

## Examples

### demo.move_cube_abs
- macro_name: demo.move_cube_abs
- version: 1.0.0
- inputs: `{ name: string, location: [number,number,number] }`
- preconditions: tool registry v1; capabilities mesh_write/transform.
- steps:
  1. `object.create` with `name`, primitive `cube`, `location`.
  2. `object.move` with `mode="set"`, `location`.
- postconditions: object `name` exists; location equals requested.
- rollback: optional delete `name` if created and failure occurs.
- determinism: deterministic given inputs; idempotent.
- fingerprint: sha256 of this macro definition (to be assigned).

### demo.snapshot_and_find
- macro_name: demo.snapshot_and_find
- version: 1.0.0
- inputs: `{ name_pattern?: string, collection?: string, limit?: integer }`
- preconditions: tool registry v1; capability snapshot.
- steps:
  1. `scene.snapshot` with `include_mesh_data=false`.
  2. `scenegraph.find` with provided filters.
- postconditions: returns matches array consistent with snapshot data.
- rollback: none.
- determinism: deterministic; pure read.
- fingerprint: sha256 to be assigned.

### demo.assign_basic_material
- macro_name: demo.assign_basic_material
- version: 1.0.0
- inputs: `{ object: string, material: string, base_color?: [number,number,number,number] }`
- preconditions: capabilities materials/object_write; tool registry v1.
- steps:
  1. `material.ensure_principled` with `material`, `base_color` default `[0.8,0.8,0.8,1.0]`.
  2. `mesh.assign_material` with `object`, `material`.
- postconditions: object has the material assigned in slot 0 (or appended) and material exists.
- rollback: optional remove material slot if added and failure occurs.
- determinism: deterministic; idempotent on repeat.
- fingerprint: sha256 to be assigned.
