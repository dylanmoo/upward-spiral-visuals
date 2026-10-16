"""Infinite-zoom chain: L0 galaxy -> L1 -> L2 -> L3 -> back to L0. Square, 480p.
Usage: hf_zoom.py <out_dir> <L0_still> <style_ref>"""
import os
import sys
import time
import urllib.request
from PIL import Image

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

out, l0, style_ref = sys.argv[1:4]
os.makedirs(out, exist_ok=True)

STYLE = ("Rendered in the exact style of the molecular reference image: scientific biomedical animation, space-filling atomic "
         "models where every atom is a glossy sphere, golden yellow and orange DNA backbones, blue, violet and magenta base pairs, "
         "proteins in cobalt blue, teal, magenta and crimson, dark navy-black space with out-of-focus molecules, soft lighting. "
         "Square composition, centered. No text.")

LEVELS = [
    ("Image 1 is a zoomed-in crop of the glowing core of a molecular spiral galaxy. Keep its overall colors and brightness layout "
     "so it reads as the same view magnified, but reveal that the core is actually a dense cluster of dozens of smaller spiral "
     "galaxies, each spiral built from coiled DNA double helices and protein clusters in varied colors (gold, magenta, cobalt, teal), "
     "all swirling around one bright central spiral. "),
    ("Image 1 is a zoomed-in crop of the center of a cluster of molecular spiral galaxies. Keep its overall colors and layout so it "
     "reads as the same view magnified, but reveal that the central spiral is a living cell nucleus: a translucent glowing sphere "
     "filled with coiled chromatin, nucleosome beads, ring-shaped protein clamps on DNA, helicases unzipping strands, and nuclear "
     "pore rings around its rim, all intricate and busy. "),
    ("Image 1 is a zoomed-in crop of the center of a molecular cell nucleus. Keep its overall colors and layout so it reads as the "
     "same view magnified, but reveal a radially symmetric mandala of molecular machinery: concentric rings of protein gears, DNA "
     "double helices radiating outward like petals, rings of nucleotides like beads. At the exact center, small (about one fifth of "
     "the frame width), sits the spiral galaxy from image 3, unchanged. "),
]

TRANSITIONS = [
    "Continuous smooth camera zoom straight into the glowing core at the center of the spiral galaxy. As the camera dives in, the "
    "core opens up to reveal a cluster of smaller spiral galaxies, every spiral turning and every helix rippling.",
    "Continuous smooth camera zoom straight into the central spiral of the galaxy cluster. As the camera dives in, it opens into a "
    "glowing cell nucleus full of busy molecular machines: helicases unzipping DNA, clamps sliding, chromatin coiling.",
    "Continuous smooth camera zoom straight into the center of the cell nucleus. As the camera dives in, the machinery arranges "
    "itself into a rotating mandala of protein rings and radiating DNA helices, each ring turning in alternating directions.",
    "Continuous smooth camera zoom straight into the tiny spiral galaxy at the center of the rotating molecular mandala. The mandala "
    "rings rush outward past the edges of the frame as the galaxy grows to fill the view.",
]
SUFFIX = " The camera never stops moving forward. One continuous shot, no cuts."


def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)


def center_crop(src, dst, frac=0.34):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    cw, ch = int(w * frac), int(h * frac)
    box = ((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)
    im.crop(box).resize((1024, 1024), Image.LANCZOS).save(dst, quality=92)


style_url = hf.upload_file(style_ref)
l0_url = hf.upload_file(l0)
stills = [l0]
urls = [l0_url]
for i, text in enumerate(LEVELS, 1):
    crop = f"{out}/crop{i-1}.jpg"
    center_crop(stills[-1], crop)
    imgs = [hf.upload_file(crop), style_url] + ([l0_url] if i == 3 else [])
    for attempt in range(2):
        try:
            res = wait(hf.submit("alibaba/qwen-image-3/edit", arguments={
                "prompt": text + STYLE, "image_urls": imgs, "resolution": "1k", "aspect_ratio": "1:1"}))
            break
        except Exception as e:
            print(f"L{i} still attempt {attempt+1} failed", type(e).__name__, flush=True)
    else:
        sys.exit(f"L{i} still failed")
    url = res["images"][0]["url"]
    path = f"{out}/L{i}.png"
    urllib.request.urlretrieve(url, path)
    stills.append(path)
    urls.append(url)
    print("still done", f"L{i}", flush=True)

pairs = [(urls[0], urls[1]), (urls[1], urls[2]), (urls[2], urls[3]), (urls[3], urls[0])]
ctrls = []
for n, ((a, b), prompt) in enumerate(zip(pairs, TRANSITIONS)):
    ctrls.append(hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
        "image_url": a, "end_image_url": b, "prompt": prompt + SUFFIX,
        "resolution": "480p", "duration": 8, "generate_audio": False}))
    print("video submitted", f"seg{n}", flush=True)
for n, c in enumerate(ctrls):
    try:
        urllib.request.urlretrieve(wait(c)["video"]["url"], f"{out}/seg{n}.mp4")
        print("video done", f"seg{n}", flush=True)
    except Exception as e:
        print("video failed", f"seg{n}", type(e).__name__, flush=True)
