"""Alien at the peephole: photoreal fisheye still (Qwen edit, 1:1), then two 480p Seedance videos:
a seamless loop (same first and last frame) and a free take (first frame only).
Usage: hf_alien.py <out_dir> <ref_image>"""
import os
import sys
import time
import urllib.request

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

out, ref = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)

STILL = (
    "A hyperrealistic photograph of the alien from image 1, seen from inside a home through a door peephole: an extreme "
    "fisheye lens view with strong barrel distortion, the alien's huge head bulging toward the center of a circular frame "
    "that fades to black at the edges, slight vignette and glass imperfections. Keep the alien's design from image 1: "
    "large smooth cranium, huge glossy black almond eyes, tiny nostrils, small closed mouth, fine wrinkled skin around the "
    "eyes and nose, thin neck, pale skin with soft blue, lavender and faint green mottling. Render it as real living skin "
    "with subsurface scattering, moist reflections in the eyes and fine pores, not a painting. Its expression is gentle, "
    "curious and a little shy, leaning close to the door. Dim apartment hallway behind it with a warm ceiling light. "
    "Cinematic, shallow depth of field, photoreal. No text, no watermark, no signature."
)
LOOP = (
    "Seen through a door peephole fisheye lens. The friendly alien leans in close to the peephole, curious and a little "
    "cautious. It tilts its head slowly to one side, its big glossy black eyes scanning around as if looking for someone "
    "inside, blinks softly, then eases back to where it started. Gentle, inquisitive, never menacing. Subtle breathing, "
    "the hallway light flickers faintly. Handheld-free locked camera, fisheye distortion stays constant. One continuous "
    "shot, no cuts."
)
FREE = (
    "Seen through a door peephole fisheye lens. The friendly alien approaches the door, hesitates, then leans in close to "
    "the peephole with curious, slightly shy body language. It tilts its head one way, then the other, big glossy black "
    "eyes searching as if looking for someone inside, blinks slowly, and its small mouth softens into the hint of a "
    "friendly expression. Gentle, inquisitive, never menacing. Locked camera, fisheye distortion stays constant. One "
    "continuous shot, no cuts."
)


def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)


ref_url = hf.upload_file(ref)
res = wait(hf.submit("alibaba/qwen-image-3/edit", arguments={
    "prompt": STILL, "image_urls": [ref_url], "resolution": "1k", "aspect_ratio": "1:1",
    "negative_prompt": "text, watermark, letters, signature, logo, painting, illustration, cartoon, scary, menacing teeth"}))
still_url = res["images"][0]["url"]
urllib.request.urlretrieve(still_url, f"{out}/alien-peephole-still.png")
print("still done", flush=True)

jobs = {
    "alien-peephole-loop": dict(image_url=still_url, end_image_url=still_url, prompt=LOOP),
    "alien-peephole-free": dict(image_url=still_url, prompt=FREE),
}
ctrls = {n: hf.submit("bytedance/seedance-2.0/image-to-video", arguments=dict(
    a, resolution="480p", duration=8, generate_audio=False)) for n, a in jobs.items()}
for n, c in ctrls.items():
    try:
        urllib.request.urlretrieve(wait(c)["video"]["url"], f"{out}/{n}.mp4")
        print("video done", n, flush=True)
    except Exception as e:
        print("video failed", n, type(e).__name__, str(e)[:200], flush=True)
