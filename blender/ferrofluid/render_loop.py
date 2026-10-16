import bpy, sys
a = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=a[0])
s = bpy.context.scene; s.camera = bpy.data.objects[a[1]]
s.render.resolution_percentage = int(a[2]); s.cycles.samples = int(a[3])
s.render.filepath = a[4]; s.frame_start, s.frame_end = 1, 96
bpy.ops.render.render(animation=True)
