"""Seamless infinite zoom, chained: each segment starts on the previous segment's real last frame.
Levels: L0 galaxy, L1 cluster, L2 nucleus (existing) -> L3 forest, L4 underwater, L5 cymatics, L6 sahara, L7 mandala -> L0.
Usage: hf_zoom2.py <zoom_dir> <style_ref>   (expects L0 at ../galaxy/galaxy1-still.png, L1.png, L2.png, seg0.mp4 in zoom_dir)"""
import os
import subprocess
import sys
import time
import urllib.request
from PIL import Image

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

z, style_ref = sys.argv[1], sys.argv[2]
out = f"{z}/hd"
os.makedirs(out, exist_ok=True)
L0 = os.path.join(z, "..", "galaxy", "galaxy1-still.png")

STYLE = (" Keep the glossy space-filling molecular rendering of the reference image (every form built from clusters of glossy "
         "spheres, soft lighting, shallow depth of field), but let this world's own colors lead. Square composition, centered. No text.")
CROP_INTRO = ("Image 1 is a zoomed-in crop of the center of the previous world. Keep its overall colors and brightness layout at the "
              "edges so it reads as the same view magnified, but reveal that it is ")
LEVELS = {
    3: "a neural forest: towering neurons like trees with branching dendrites and glowing synapses, intertwined with lush greenery, "
       "ferns, vines, moss, leaves and blooming flowers, in emerald, lime and jade greens with golden pulses of light along the branches.",
    4: "an underwater bioluminescent reef: coral formations, sea anemones, swaying kelp and drifting jellyfish in aqua, turquoise, "
       "coral pink and violet, shafts of light falling from above, rising bubbles.",
    5: "a cymatic pattern: an intricate radially symmetric standing-wave pattern like sand on a vibrating plate, thousands of tiny "
       "spheres in pearl white, gold and pale blue arranged into concentric geometric rings, nodes and petals on a dark background.",
    6: "an aerial view looking straight down over Sahara desert dunes at golden hour, the dune crests curving in a great spiral around "
       "the center, sand made of countless tiny glossy golden and orange spheres, long cool blue shadows.",
    7: "a radially symmetric mandala of molecular machinery: concentric rings of protein gears, DNA double helices radiating outward "
       "like petals, rings of nucleotides like beads. At the exact center, small (about one fifth of the frame width), sits the spiral "
       "galaxy from image 3, unchanged.",
}
MOTION = {
    1: "the cluster's central spiral opens into a glowing cell nucleus full of busy molecular machines: helicases unzipping DNA, clamps sliding, chromatin coiling.",
    2: "the nucleus opens into a neural forest: neurons fire pulses of light along branching dendrites, ferns unfurl, vines grow and leaves sway.",
    3: "the forest dissolves into an underwater reef: jellyfish pulse, kelp sways, anemones wave, bubbles rise through shafts of light.",
    4: "the reef resolves into a cymatic pattern that vibrates, ripples and reshapes itself into ever more intricate geometric rings.",
    5: "the cymatic rings become Sahara dunes seen from above, sand streaming off the crests in the wind as the spiral of dunes slowly turns.",
    6: "the dunes give way to a rotating mandala of protein rings and radiating DNA helices, each ring turning in alternating directions.",
    7: "the mandala rings rush outward past the edges of the frame as the tiny spiral galaxy at its center grows to fill the view.",
}
PREFIX = "Continuous smooth camera zoom straight into the center of the frame. As the camera dives in, "
SUFFIX = " The camera never stops moving forward. One continuous shot, no cuts."


def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)


def retry(fn, tries=2):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            print("  attempt failed:", type(e).__name__, str(e)[:200], flush=True)
    raise SystemExit("giving up")


def center_crop(src, dst, frac=0.34):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    cw, ch = int(w * frac), int(h * frac)
    im.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)).resize((1024, 1024), Image.LANCZOS).save(dst, quality=92)


def frame(video, dst, last):
    args = ["ffmpeg", "-v", "error", "-y"] + (["-sseof", "-0.05"] if last else []) + ["-i", video, "-frames:v", "1"] + (["-update", "1"] if last else []) + [dst]
    subprocess.run(args, check=True)


style_url = hf.upload_file(style_ref)
l0_url = hf.upload_file(L0)
stills = {0: L0, 1: f"{z}/L1.png", 2: f"{z}/L2.png"}
urls = {0: l0_url, 1: hf.upload_file(stills[1]), 2: hf.upload_file(stills[2])}

# keyframes L3..L7, each from a crop of the previous one
for i in range(3, 8):
    path = f"{z}/v2/L{i}.png"
    if not os.path.exists(path):
        crop = f"{out}/crop{i-1}.jpg"
        center_crop(stills[i - 1], crop)
        imgs = [hf.upload_file(crop), style_url] + ([l0_url] if i == 7 else [])
        res = retry(lambda: wait(hf.submit("alibaba/qwen-image-3/edit", arguments={
            "prompt": CROP_INTRO + LEVELS[i] + STYLE, "image_urls": imgs, "resolution": "1k", "aspect_ratio": "1:1"})))
        urllib.request.urlretrieve(res["images"][0]["url"], path)
        print("still done", f"L{i}", flush=True)
    stills[i] = path
    urls[i] = hf.upload_file(path)

# segments 1..7 chained from the real last frame of the previous segment
prev = f"{out}/seg0.mp4"
if not os.path.exists(prev):
    res = retry(lambda: wait(hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
        "image_url": urls[0], "end_image_url": urls[1],
        "prompt": PREFIX + "the glowing golden core opens up to reveal a cluster of smaller spiral galaxies, every spiral turning and every helix rippling." + SUFFIX,
        "resolution": "1080p", "duration": 8, "generate_audio": False})))
    urllib.request.urlretrieve(res["video"]["url"], prev)
    print("video done seg0", flush=True)
frame(prev, f"{out}/seg0-first.png", last=False)
loop_target = hf.upload_file(f"{out}/seg0-first.png")
for n in range(1, 8):
    seg = f"{out}/seg{n}.mp4"
    if not os.path.exists(seg):
        frame(prev, f"{out}/seg{n-1}-last.png", last=True)
        start = hf.upload_file(f"{out}/seg{n-1}-last.png")
        end = loop_target if n == 7 else urls[n + 1]
        res = retry(lambda: wait(hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
            "image_url": start, "end_image_url": end, "prompt": PREFIX + MOTION[n] + SUFFIX,
            "resolution": "1080p", "duration": 8, "generate_audio": False})))
        urllib.request.urlretrieve(res["video"]["url"], seg)
        print("video done", f"seg{n}", flush=True)
    prev = seg
print("all done", flush=True)
