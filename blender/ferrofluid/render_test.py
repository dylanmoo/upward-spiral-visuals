import bpy, sys, time
a = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=a[0])
s = bpy.context.scene; s.render.resolution_percentage = int(a[1]); s.cycles.samples = int(a[2])
s.cycles.use_adaptive_sampling = True; s.render.threads_mode = 'AUTO'
for spec in a[3:]:
    cam, fr = spec.split(':'); s.camera = bpy.data.objects[cam]; s.frame_set(int(fr))
    s.render.filepath = f"test/{cam}_f{int(fr):03d}.png"; t = time.time(); bpy.ops.render.render(write_still=True)
    print("RENDERED", cam, fr, "%.1fs" % (time.time() - t), flush=True)
