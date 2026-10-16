"""Build the ferrofluid scene: black liquid metal spiking on a magnet, as a seamless 4-second loop.

Run inside Blender (Scripting tab > Open > Run Script), or headless:
    blender --background --python build_ferrofluid.py -- --out ferrofluid.blend
With the bpy Python module:
    python build_ferrofluid.py --out ferrofluid.blend

How the scene works
- A dense grid is pushed up by two Displace modifiers: a smooth pool (static) and a hex field of
  conical spikes. Both height maps are generated here with numpy and packed into the .blend.
- The spikes' strength is driven by FF_Controls["spike_height"] and FF_Controls["pulse"].
  "pulse" is keyframed as 4 kicks per 96-frame loop (sharp attack, exponential decay).
- The liquid turns 60 degrees per loop. The spike lattice has 6-fold symmetry, so frame 97 equals
  frame 1 and the loop is exact.
- Two cameras: Cam_Top (straight down, made for the circle screen) and Cam_Angle (low, dramatic).
"""
import math
import sys

import bpy
import bmesh  # after bpy: the bpy module only exposes bmesh once it is loaded
import numpy as np

FRAMES = 96          # one loop at 24 fps = 4 s
KICKS = 4            # kicks per loop
GRID_SIZE = 2.4      # metres across
GRID_SUBDIV = 800    # vertices per side
MAP_RES = 2048       # height map resolution
SPACING = 0.115      # distance between spikes
SPIKE_RADIUS = 0.06  # base radius of one spike
POOL_RADIUS = 0.95
SPIKE_FIELD = 0.9    # spikes fade out past this radius


def arg(name, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    return argv[argv.index(name) + 1] if name in argv else default


def height_maps():
    c = np.linspace(-GRID_SIZE / 2, GRID_SIZE / 2, MAP_RES)
    x, y = np.meshgrid(c, c)
    r = np.hypot(x, y)
    # nearest point on a hex lattice centred on the origin (two offset rectangular sub-lattices)
    sx, sy = SPACING, SPACING * math.sqrt(3)

    def nearest(ox, oy):
        qx, qy = (x - ox) / sx, (y - oy) / sy
        return np.hypot((qx - np.round(qx)) * sx, (qy - np.round(qy)) * sy)

    d = np.minimum(nearest(0, 0), nearest(sx / 2, sy / 2))
    cone = np.clip(1 - d / SPIKE_RADIUS, 0, 1) ** 2.0  # concave flanks, sharp tip
    envelope = np.clip(1 - (r / SPIKE_FIELD) ** 2, 0, 1) ** 0.8
    spikes = cone * envelope
    pool = np.clip(1 - (r / POOL_RADIUS) ** 2, 0, 1) ** 1.8
    return pool.astype(np.float32), spikes.astype(np.float32)


def fcurves_of(obj):
    """All F-curves on an object's action, for both legacy and layered (Blender 4.4+) actions."""
    act = obj.animation_data.action
    try:
        return list(act.fcurves)
    except AttributeError:
        pass
    curves = []
    for layer in act.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                curves += list(bag.fcurves)
    return curves


def make_image(name, data):
    img = bpy.data.images.new(name, MAP_RES, MAP_RES, float_buffer=True, alpha=False)
    rgba = np.empty((MAP_RES, MAP_RES, 4), np.float32)
    rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = data
    rgba[..., 3] = 1
    img.pixels.foreach_set(rgba.ravel())
    img.pack()
    return img


def displace(obj, name, img, strength):
    tex = bpy.data.textures.new(name, type="IMAGE")
    tex.image = img
    tex.extension = "EXTEND"
    tex.use_interpolation = True
    mod = obj.modifiers.new(name, "DISPLACE")
    mod.texture = tex
    mod.texture_coords = "UV"
    mod.direction = "Z"
    mod.mid_level = 0.0
    mod.strength = strength
    return mod


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, FRAMES
    scene.render.fps = 24

    # controls
    ctl = bpy.data.objects.new("FF_Controls", None)
    scene.collection.objects.link(ctl)
    ctl["spike_height"] = 1.0
    ctl["pulse"] = 1.0
    ctl.id_properties_ui("spike_height").update(min=0.0, max=2.0, description="Overall spike height")
    ctl.id_properties_ui("pulse").update(min=0.0, max=1.0, description="Kick envelope (keyframed)")
    step = FRAMES // KICKS
    for k in range(KICKS):
        f0 = 1 + k * step
        ctl["pulse"] = 1.0
        ctl.keyframe_insert('["pulse"]', frame=f0)
        ctl["pulse"] = 0.3
        ctl.keyframe_insert('["pulse"]', frame=f0 + step - 1)
    ctl["pulse"] = 1.0
    ctl.keyframe_insert('["pulse"]', frame=FRAMES + 1)
    for fc in fcurves_of(ctl):
        for kp in fc.keyframe_points:
            if abs(kp.co[1] - 1.0) < 1e-6:
                kp.interpolation, kp.easing = "EXPO", "EASE_OUT"
            else:
                kp.interpolation = "LINEAR"

    # liquid surface
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=GRID_SUBDIV, y_subdivisions=GRID_SUBDIV,
                                    size=GRID_SIZE, calc_uvs=True)
    fluid = bpy.context.active_object
    fluid.name = "Ferrofluid"
    # trim to a disc: a square would not repeat after the 60 degree turn, so the loop would jump
    bm = bmesh.new()
    bm.from_mesh(fluid.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if math.hypot(v.co.x, v.co.y) > GRID_SIZE / 2 - 0.02],
                     context="VERTS")
    bm.to_mesh(fluid.data)
    bm.free()
    bpy.ops.object.shade_smooth()
    pool_img, spike_img = (make_image(n, a) for n, a in zip(("FF_pool", "FF_spikes"), height_maps()))
    displace(fluid, "Pool", pool_img, 0.15)
    spikes = displace(fluid, "Spikes", spike_img, 0.24)
    drv = spikes.driver_add("strength").driver
    drv.type = "SCRIPTED"
    for vname, prop in (("h", "spike_height"), ("p", "pulse")):
        v = drv.variables.new()
        v.name = vname
        v.targets[0].id = ctl
        v.targets[0].data_path = f'["{prop}"]'
    drv.expression = "0.24 * h * (0.35 + 0.65 * p)"
    # 60 degree turn per loop; the hex lattice makes this seamless
    fluid.rotation_euler[2] = 0.0
    fluid.keyframe_insert("rotation_euler", index=2, frame=1)
    fluid.rotation_euler[2] = math.radians(60)
    fluid.keyframe_insert("rotation_euler", index=2, frame=FRAMES + 1)
    for fc in fcurves_of(fluid):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

    mat = bpy.data.materials.new("Ferrofluid_Black")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1)
    bsdf.inputs["Roughness"].default_value = 0.06
    bsdf.inputs["Coat Weight"].default_value = 0.6
    bsdf.inputs["Coat Roughness"].default_value = 0.02
    # matte black floor outside the pool, so the tray doesn't mirror the lights
    nt = mat.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    length = nt.nodes.new("ShaderNodeVectorMath")
    length.operation = "LENGTH"
    edge = nt.nodes.new("ShaderNodeMapRange")
    edge.inputs["From Min"].default_value = POOL_RADIUS * 0.97
    edge.inputs["From Max"].default_value = POOL_RADIUS * 1.05
    nt.links.new(coord.outputs["Object"], length.inputs[0])
    nt.links.new(length.outputs["Value"], edge.inputs["Value"])
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value, rough.inputs["To Max"].default_value = 0.06, 0.9
    coat = nt.nodes.new("ShaderNodeMapRange")
    coat.inputs["To Min"].default_value, coat.inputs["To Max"].default_value = 0.6, 0.0
    spec = nt.nodes.new("ShaderNodeMapRange")
    spec.inputs["To Min"].default_value, spec.inputs["To Max"].default_value = 0.5, 0.0
    for m in (rough, coat, spec):
        nt.links.new(edge.outputs["Result"], m.inputs["Value"])
    nt.links.new(spec.outputs["Result"], bsdf.inputs["Specular IOR Level"])
    nt.links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(coat.outputs["Result"], bsdf.inputs["Coat Weight"])
    fluid.data.materials.append(mat)

    # static matte floor that reaches the horizon (does not rotate)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.002))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor_mat = bpy.data.materials.new("Floor_Matte_Black")
    floor_mat.use_nodes = True
    fb = floor_mat.node_tree.nodes["Principled BSDF"]
    fb.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1)
    fb.inputs["Roughness"].default_value = 0.9
    fb.inputs["Specular IOR Level"].default_value = 0.0
    floor.data.materials.append(floor_mat)

    # studio lights: their reflections are what make it read as liquid metal
    def area(name, loc, rot, size, size_y, energy, color=(1, 1, 1)):
        bpy.ops.object.light_add(type="AREA", location=loc, rotation=[math.radians(a) for a in rot])
        light = bpy.context.active_object
        light.name = name
        light.data.shape = "RECTANGLE"
        light.data.size, light.data.size_y = size, size_y
        light.data.energy = energy
        light.data.color = color
        return light

    area("Key_Softbox", (-1.6, 1.4, 2.4), (-35, -38, 0), 1.2, 0.7, 380, (1.0, 0.97, 0.92))
    area("Strip_Cool", (2.0, -0.6, 1.2), (60, 0, 70), 3.0, 0.25, 500, (0.7, 0.82, 1.0))
    area("Rim_Warm", (0.2, 2.6, 0.5), (-80, 0, 180), 2.5, 0.2, 350, (1.0, 0.75, 0.5))
    ring = area("Ring_Top", (0, 0, 3.6), (0, 0, 0), 1.4, 1.4, 600)
    ring.data.shape = "DISK"

    world = bpy.data.worlds.new("Studio_Dark")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.004, 0.005, 1)
    scene.world = world

    def camera(name, loc, rot, lens):
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = lens
        cam = bpy.data.objects.new(name, cam_data)
        cam.location = loc
        cam.rotation_euler = [math.radians(a) for a in rot]
        scene.collection.objects.link(cam)
        return cam

    top = camera("Cam_Top", (0, 0, 3.0), (0, 0, 0), 50)
    camera("Cam_Angle", (0, -2.2, 1.25), (62, 0, 0), 42)
    scene.camera = top

    r = scene.render
    r.engine = "CYCLES"
    r.resolution_x = r.resolution_y = 1080
    r.image_settings.file_format = "PNG"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    return scene


if __name__ == "__main__":
    out = arg("--out", "ferrofluid.blend")
    build()
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print("saved", out)
