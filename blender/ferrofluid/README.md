# Ferrofluid (Blender)

Black liquid metal spiking on a magnet, as an exact 4-second loop (96 frames at 24 fps) for the circle screen. Made because the ferrofluid shader in Optics Bench was the weakest of the eight. Blender's Cycles renderer simulates real reflections, which is what sells glossy black liquid.

## Files

| File | What it is |
|---|---|
| `ferrofluid.blend` | The scene, made in Blender 5.2.2 LTS. Height maps are packed inside, so it opens on its own. |
| `build_ferrofluid.py` | Script that builds the scene from scratch. Use it if your Blender can't open the .blend (older versions often can't open files from newer ones), or to change the spike layout. |
| `renders/` | Low-res CPU test renders from the cloud session (432×432, 32 samples). Final renders happen on the Mac. |

## How the scene works

- **Liquid:** a dense grid pushed up by two Displace modifiers, one for the smooth pool (static) and one for a hex field of sharp spikes.
- **Kicks:** the `FF_Controls` empty has two custom properties:
  - `spike_height` (0–2) scales every spike.
  - `pulse` is keyframed as 4 kicks per loop: an instant rise, then an exponential decay.
  - The Spikes modifier's strength is driven by both.
- **Loop:** the liquid turns 60° per loop. The spike lattice has 6-fold symmetry, so frame 97 is identical to frame 1. Render frames 1–96.
- **Lights:** a key softbox, a cool strip, a warm rim and a ring light overhead. The highlights on each spike are reflections of these, so moving a light changes the look most.
- **Cameras:**
  - `Cam_Angle` (low, dramatic) is the hero shot.
  - `Cam_Top` looks straight down and fits the circle exactly, but the spikes read flatter from above.
  - Switch with Scene Properties > Camera.

## Rendering on the Mac

1. **Use the GPU:** Preferences > System > Cycles Render Devices > Metal, then Render Properties > Device > GPU Compute.
2. **Output:** it's already set to 1080×1080 at 128 samples with denoising. In Output Properties, choose a folder, and keep PNG.
3. **Render:** Render > Render Animation renders frames 1–96.
4. **Encode:** convert the PNG sequence to DXV with Alley (Resolume's free converter), or to HAP or ProRes, then set the clip to loop in Resolume.

## Things to tweak

- **Spike size:** set `spike_height` on `FF_Controls`, for example 1.4 for bigger spikes.
- **Kick timing:** move the `pulse` keyframes in the Graph Editor.
  - For a different number of kicks or loop length, change `KICKS` and `FRAMES` at the top of the script and rebuild.
  - To make it react to the actual track, bake the song onto the `pulse` property with Blender's "Bake Sound to F-Curves" operator (find it with F3 in the Graph Editor). That replaces the even kicks with the real ones but breaks the exact loop.
- **Spike layout:** `SPACING`, `SPIKE_RADIUS` and `SPIKE_FIELD` in the script set density, width and how far out the spikes reach.
- **Mood:** tint the light colors. The liquid is black, so it takes on whatever color the lights are.
