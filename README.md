# Upward Spiral Visuals

VJ visuals made for a DJ set projected onto a round screen, so almost everything is square (1:1) and composed around the center. Most clips are seamless loops that you can trigger and leave running in Resolume.

To get everything: **Code > Download ZIP**, or `git clone`. No Git LFS needed.

## What's here

### `clips/`: ready-to-play loops (MP4, H.264)

| Folder | What it is | Size |
|---|---|---|
| `portals/` | Photoreal "the circle is a portal" loops. A real halved nautilus shell with light sweeping over the nacre, with or without animated math: φ = (1+√5)/2, Fibonacci ratios converging on φ, and a log spiral r = a·e^(bθ) traced along the coil. Plus looking straight up into a swaying redwood canopy. `nautilus-math-overlay-add` is the math alone on black for Add blending. | 1080×1080 |
| `alien-peephole/` | A friendly, hyperrealistic alien seen through a door peephole: staring and winking, dancing, floating in meditation, failing a handstand, and sneaking up to tap the glass. Most are loops; `*-free` and `*-oneshot` play once. | 1080×1080 |
| `infinite-zoom/` | A 63-second seamless dive through eight worlds: galaxy, galaxy cluster, cell nucleus, neural forest, reef, cymatics, desert dunes, mandala, and back to the galaxy. `keyframes/` holds the world stills. | 1080×1080 |
| `molecular-galaxies/` | Spiral galaxies rebuilt out of DNA and proteins, gently animated. Spin the layer in Resolume for rotation; on a round screen that loops forever. | 640×640 |
| `dna-loops/` | Molecular DNA loops (repair piston, spiral tunnel, unzipping, conveyor), named after the voice lines they were made for. | 496×496 |

### `shaders/optics-bench/`: live GLSL shaders (ISF)

Eight real-time shaders based on real optics, each with sliders:
- **Glass:** crystal lens and reeded glass.
- **Interference:** a photoelastic disc, with stress fringes computed per wavelength.
- **Metal and heat:** ferrofluid, and hot metal with blackbody color and temper tints.
- **Air:** schlieren imaging of a heat plume and sound waves.
- **Space:** a gravitational lens and a nebula.

Each shader loops exactly. It also has a "drive phase manually" input, so you can sync the loop to the beat in Resolume.
- **In Resolume:** load a `.fs` file into an ISF node in **Wire** and save it as a Source. Other ISF apps (VDMX, Magic Music Visuals) load them directly.
- **In a browser:** open `optics-bench.html` to play with all eight.
- **Setup steps:** see `shaders/optics-bench/README.md`.

### `blender/ferrofluid/`: Blender scene

Black ferrofluid spiking on a magnet, as a 4-second exact loop with 4 kicks, rendered in Cycles. Made in Blender 5.2. If your Blender version can't open the file, run `build_ferrofluid.py` to rebuild the scene. Render on a GPU at 1080×1080. The folder's README covers the settings and how to make it react to a track.

### `stills/` and `tools/`

- **`stills/`:** the photoreal first frames the alien and portal clips were animated from.
- **`tools/`:** the scripts that generated and stitched everything.
  - **Generation:** Higgsfield API scripts for Seedance 2.0/2.5 video and Qwen Image 3 / Grok Imagine stills. They read the API key from an environment variable.
  - **Math overlay:** `naut_overlay.py` renders the nautilus math as transparent PNG frames (Python + Pillow). Edit the spiral fit or the text and re-render.
  - **Loops:** `loopify.sh` crossfades a loop seam, and `stitch_zoom.sh` joins the zoom dives.
  - **Shaders:** `make_isf.js` generates the ISF files, and `isf_test.js` compile-tests them.

## Techniques worth stealing

- **Seamless AI loops:** give the video model the same image as both its first and last frame.
- **Seamless infinite zoom:**
  1. Make each world's keyframe from a center crop of the previous world.
  2. Start each dive from the actual last frame of the dive before it.
  3. Dissolve 4 frames at each join.
- **Style references:** one style reference image works better than four. With several, the model copies them instead of following the prompt.
- **Math that matches the footage:** a real nautilus is *not* a golden spiral (it widens about 2.8× per turn; a golden spiral widens about 6.9×). The overlay's spiral is fitted to this shell, so it sits right on the coil. Render text and math yourself instead of asking a video model for it.
- **Loops in Blender:** spin a 6-fold-symmetric pattern 60° per loop, and the last frame matches the first.

## Credits

- **Molecular look:** inspired by Drew Berry's molecular animations for WEHI. No WEHI footage is included.
- **Galaxy layouts:** based on Hubble photographs (ESA/Hubble and NASA). The photos themselves aren't included.
- **Tools:** clips were generated with Seedance 2.0/2.5, Qwen Image 3 and Grok Imagine via Higgsfield, and upscaled with Topaz Video. Shaders and the Blender scene were written by hand with Claude.

## License

Remix and use freely. The media is **CC BY 4.0**: use it anywhere, including paid gigs, with credit to "Upward Spiral Visuals by Dylan Moore". The code is **MIT**. See `LICENSE.md` for the details.
