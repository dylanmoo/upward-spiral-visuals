"""Galaxy-layout molecular spirals: restyle still (Qwen edit, 1:1) then loop video (Seedance i2v, same first/last frame).
Usage: hf_galaxy.py <out_dir> <style_ref> <galaxy1> [<galaxy2> ...]"""
import os
import sys
import time
import urllib.request

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

out, style_ref, galaxies = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)
style_url = hf.upload_file(style_ref)

STILL_PROMPT = (
    "Recreate the spiral galaxy from image 1 as a scientific biomedical molecular animation still in the exact style of image 2. "
    "Keep the galaxy's layout, proportions, tilt, number of spiral arms and bright central core from image 1, centered in a square frame. "
    "Build the spiral arms out of coiled DNA double helices and clustered protein molecules rendered as space-filling atomic models, "
    "every atom a glossy sphere: golden yellow and orange DNA backbone, blue, violet and magenta base pairs, proteins in cobalt blue, "
    "teal, magenta and crimson. The core is a dense glowing cluster of golden molecules. Scattered loose nucleotides stand in for stars. "
    "Dark navy-black background with out-of-focus molecules, soft lighting, shallow depth of field. No text."
)
VIDEO_PROMPT = (
    "The molecular spiral galaxy turns slowly around its glowing core while the DNA strands and protein clusters in its arms gently "
    "ripple and pulse, and loose nucleotides drift and twinkle like stars. Camera holds perfectly still and centered. "
    "Slow, smooth, hypnotic motion. One continuous shot, no cuts."
)

def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)

# 1) stills, submitted together
stills = {}
for i, g in enumerate(galaxies, 1):
    name = f"galaxy{i}"
    try:
        stills[name] = hf.submit("alibaba/qwen-image-3/edit", arguments={
            "prompt": STILL_PROMPT, "image_urls": [hf.upload_file(g), style_url],
            "resolution": "1k", "aspect_ratio": "1:1"})
        print("still submitted", name, flush=True)
    except Exception as e:
        print("still submit failed", name, type(e).__name__, str(e)[:300], flush=True)

videos = {}
for name, ctrl in stills.items():
    try:
        url = wait(ctrl)["images"][0]["url"]
        path = f"{out}/{name}-still.png"
        urllib.request.urlretrieve(url, path)
        print("still done", name, flush=True)
        videos[name] = hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
            "image_url": url, "end_image_url": url, "prompt": VIDEO_PROMPT,
            "resolution": "480p", "duration": 5, "generate_audio": False})
        print("video submitted", name, flush=True)
    except Exception as e:
        print("still/video failed", name, type(e).__name__, str(e)[:300], flush=True)

for name, ctrl in videos.items():
    try:
        url = wait(ctrl)["video"]["url"]
        urllib.request.urlretrieve(url, f"{out}/{name}-loop.mp4")
        print("video done", name, flush=True)
    except Exception as e:
        print("video failed", name, type(e).__name__, str(e)[:300], flush=True)
