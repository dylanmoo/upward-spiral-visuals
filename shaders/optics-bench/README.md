# Optics Bench shaders (ISF)

Eight live shaders from the Optics Bench preview page, as ISF v2 generators (`.fs`). Each one renders a looping visual from scratch every frame, so it works at any resolution. Square 1080×1080 is the target for the circle screen.

| File | Shader | Sliders A / B / C |
|---|---|---|
| 01-crystal-lens.fs | Crystal lens | Refraction / Lens size / Dispersion |
| 03-reeded-glass.fs | Reeded glass | Refraction / Reed width / Dispersion |
| 05-photoelastic-disc.fs | Photoelastic disc | Load / Second load / Fringe density |
| 07-ferrofluid.fs | Ferrofluid | Spike height / Spike density / Kicks per loop |
| 08-hot-metal.fs | Hot metal | Heat / Temper colors / Hammer texture |
| 09-schlieren.fs | Schlieren | Sensitivity / Sound waves / Color filter |
| 10-gravitational-lens.fs | Gravitational lens | Lens mass / Shadow size / Star color |
| 11-nebula-dust.fs | Nebula dust | Brightness / Dust / Scale |

Every shader also has:
- **Hue shift**: rotates the whole palette.
- **Loop length (s)**: how long one loop takes when running on its own clock.
- **Drive phase manually** and **Phase (0-1)**: turn the first on, then animate Phase from Resolume to lock the loop to the beat (see below).
- **Circle mask**: blacks out everything outside the circle. Turn it off if Resolume's own mask or the projector handles the edge.

## Getting them into Resolume (pick the route that fits the computer)

### Route A: Resolume Wire (if you own Wire)
1. In Wire, create a new patch and add an **ISF** node.
2. On the node's **Fragment Shader** attribute, browse to one of these `.fs` files. The sliders show up as node inputs.
3. Expose the inputs you want, connect the ISF output to the patch output, and save the patch as a **Source**.
4. In Arena or Avenue, the patch appears under Sources with those sliders on the clip's dashboard.

### Route B: An ISF host app, sent into Resolume
- **Magic Music Visuals** (Mac and Windows) and **VDMX** (Mac) load `.fs` files directly with their sliders.
- Send their output into Resolume with **Spout** (Windows) or **Syphon** (Mac). In Resolume it appears under Sources as a Spout or Syphon input.

### Route C: Try Arena directly
Some Arena versions may load ISF files without Wire. Copy the folder into `Documents/Resolume Arena/Extra Effects`, restart Arena, and look under Sources and Effects. If nothing appears, use Route A or B.

## Playing them live
- **Lock loops to the tempo:** turn on *Drive phase manually*. On the *Phase* parameter, set its animation to a forward ramp synced to BPM (for example 8 or 16 beats). The loop then restarts exactly on the bar.
- **Make it react to the music:** link a slider to audio in Resolume. Ferrofluid *Spike height*, Schlieren *Sound waves* and Photoelastic *Load* respond best to the kick.
- **Loop length while free-running:** changing *Loop length* while a shader runs on its own clock makes the motion jump once. Change it between songs, or use the manual phase.

## Performance
They run comfortably on a dedicated GPU at 1080×1080. Nebula dust, Schlieren and Hot metal are the heaviest. If one stutters, run it at 720×720 and let Resolume scale it up.

Preview images are in `previews/`. The `optics-bench.html` page runs all eight in a web browser for tuning; it needs an internet connection for its fonts.
