bl_info = {
    "name": "MVP MCP Dev UI Bridge",
    "author": "aresnake",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "3D Viewport > Sidebar > MVP",
    "category": "3D View",
    "description": "DEV UI BRIDGE: Move cube data-first to Z+2. No servers or sockets.",
}

# DEV UI BRIDGE: minimal, local-only helper to mirror the MCP move cube behavior inside Blender UI.
# Each click runs in-process; there is no persistence beyond the current Blender session and no MCP transport.

import bpy

TARGET_NAME = "MVP_Cube_UI"
TARGET_POS = (0.0, 0.0, 2.0)


def ensure_cube(name: str):
    obj = bpy.data.objects.get(name)
    if obj and obj.type != "MESH":
        bpy.data.objects.remove(obj, do_unlink=True)
        obj = None

    if obj is None:
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        obj = bpy.data.objects.new(name, mesh)
        scene = bpy.context.scene or bpy.data.scenes[0]
        scene.collection.objects.link(obj)

    mesh = obj.data
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
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    return obj


class MVP_OT_move_cube(bpy.types.Operator):
    bl_idname = "mvp.bridge_move_cube"
    bl_label = "Move Cube (Z +2)"
    bl_description = "DEV UI BRIDGE: set MVP_Cube_UI location to [0,0,2] using data-first logic."
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            cube = ensure_cube(TARGET_NAME)
            cube.location.x = TARGET_POS[0]
            cube.location.y = TARGET_POS[1]
            cube.location.z = TARGET_POS[2]
            self.report({"INFO"}, f"{cube.name} moved to {tuple(cube.location)}")
            return {"FINISHED"}
        except Exception as exc:  # pragma: no cover - Blender UI path
            self.report({"ERROR"}, f"MVP move failed: {exc}")
            return {"CANCELLED"}


class MVP_PT_panel(bpy.types.Panel):
    bl_label = "MVP Bridge"
    bl_idname = "MVP_PT_bridge_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MVP"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="DEV UI BRIDGE (local)")
        col.operator(MVP_OT_move_cube.bl_idname, text="Move Cube (Z +2)")


classes = (MVP_OT_move_cube, MVP_PT_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
