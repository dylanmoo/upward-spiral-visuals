"""Portal loops: photoreal square stills (Grok Image 2.0), then seamless loops (same first and last frame).
Usage: hf_portal.py <out_dir> [scene ...]"""
import os
import sys
import time
import urllib.request

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

out = sys.argv[1]
only = set(sys.argv[2:])
os.makedirs(out, exist_ok=True)

PHOTO = (" Photorealistic, shot on a high-end cinema camera, natural light, rich detail, square composition centered for a "
         "circular frame. No text, no watermark, no people unless described.")
SCENES = {
    "nautilus": dict(
        still="A real nautilus shell cut in half to reveal its chambered spiral interior, lying on dark slate, lit by a "
              "soft warm key light, pearly nacre glowing in iridescent pink, gold and silver, the logarithmic spiral of "
              "chambers perfectly centered in the frame, macro photography, shallow depth of field, deep black background."
              + PHOTO,
        video="Macro shot of a halved nautilus shell centered in frame. A soft band of light slowly sweeps across the "
              "pearly chambers, the nacre shimmering with shifting iridescent color, tiny dust motes drifting in the light. "
              "Camera very slowly pushes in and drifts, then settles back. Calm, hypnotic, photoreal. One continuous shot, "
              "no cuts, no text.",
        model="bytedance/seedance-2.0/image-to-video", duration=10),
    "forest": dict(
        still="Looking straight up from the forest floor into a canopy of towering old-growth trees, trunks converging "
              "toward a circle of bright sky at the center, sunlight streaming through layers of green leaves, wide-angle "
              "lens, perfectly centered radial composition." + PHOTO,
        video="Looking straight up into a canopy of towering trees. The treetops sway slowly and gently in the wind, "
              "leaves rustling and shimmering, sunbeams flickering through the gaps, a few leaves drifting down. The camera "
              "stays still and centered. Peaceful, photoreal. One continuous shot, no cuts, no text.",
        model="bytedance/seedance-2.0/image-to-video", duration=10),
    "solarpunk": dict(
        still="Aerial drone view of a solarpunk utopia city at golden hour, dominated by nature: giant ancient trees "
              "growing between curved earthen buildings with living green roofs, glass domes full of gardens, waterfalls "
              "pouring from floating islands of land with grass and trees, rivers and lush meadows, clean clear air, warm "
              "sunshine, birds, a feeling of paradise on earth. Centered composition looking toward a giant central tree "
              "with floating islands around it." + PHOTO,
        video="Smooth cinematic drone flight through a solarpunk paradise city dominated by nature. The drone glides over "
              "lush meadows and curved earthen buildings with green roofs, between giant ancient trees and past glass "
              "domes full of gardens, under floating islands of land with waterfalls pouring into rivers, sunshine and "
              "clean clear air. Midway, a smiling kid on a hoverboard zooms past close to the camera and waves, then flies "
              "off into the distance. The drone flies one long graceful loop around the giant central tree and returns to "
              "exactly where it started. Photoreal, joyful, golden light. One continuous shot, no cuts, no text.",
        model="bytedance/seedance-2.5/image-to-video", duration=25),
}


def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)


scenes = {k: v for k, v in SCENES.items() if not only or k in only}
stills = {k: hf.submit("xai/grok-imagine-image-2.0", arguments={
    "prompt": s["still"], "resolution": "2k", "aspect_ratio": "1:1"}) for k, s in scenes.items()}
videos = {}
for k, c in stills.items():
    try:
        url = wait(c)["images"][0]["url"]
        urllib.request.urlretrieve(url, f"{out}/{k}-still.png")
        print("still done", k, flush=True)
        s = scenes[k]
        videos[k] = hf.submit(s["model"], arguments={
            "image_url": url, "end_image_url": url, "prompt": s["video"],
            "resolution": "1080p", "duration": s["duration"], "generate_audio": False})
        print("video submitted", k, flush=True)
    except Exception as e:
        print("failed", k, type(e).__name__, str(e)[:300], flush=True)
for k, c in videos.items():
    try:
        urllib.request.urlretrieve(wait(c)["video"]["url"], f"{out}/{k}-loop-raw.mp4")
        print("video done", k, flush=True)
    except Exception as e:
        print("video failed", k, type(e).__name__, str(e)[:300], flush=True)
