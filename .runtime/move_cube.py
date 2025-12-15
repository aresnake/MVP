import bpy
import json

NAME = 'MVP_Cube'
DELTA = (0.0, 0.0, 0.0)


def ensure_cube(target_name: str):
    obj = bpy.data.objects.get(target_name)
    if obj:
        return obj

    mesh = bpy.data.meshes.new(f"{target_name}_mesh")
    obj = bpy.data.objects.new(target_name, mesh)

    verts = [
        (-1, -1, -1),
        (-1, -1, 1),
        (-1, 1, -1),
        (-1, 1, 1),
        (1, -1, -1),
        (1, -1, 1),
        (1, 1, -1),
        (1, 1, 1),
    ]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (1, 5, 7, 3),
        (0, 2, 6, 4),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)

    scene = bpy.context.scene or bpy.data.scenes[0]
    scene.collection.objects.link(obj)
    return obj


def move_cube(target_name: str, delta):
    obj = ensure_cube(target_name)
    obj.location.x += delta[0]
    obj.location.y += delta[1]
    obj.location.z += delta[2]
    return obj


def main():
    try:
        cube = move_cube(NAME, DELTA)
        result = {
            "ok": True,
            "result": {
                "name": cube.name,
                "position": list(cube.location),
                "blender_version": bpy.app.version_string,
            },
        }
    except Exception as exc:
        result = {
            "ok": False,
            "error": {"code": "blender_script_error", "message": str(exc), "details": None},
        }

    print("MVP_RESULT=" + json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
