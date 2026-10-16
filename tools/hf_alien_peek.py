"""Alien sneaks up to the peephole: empty-hallway still and a tap-the-glass still (Qwen edit, anchored on the peephole
still), then two Seedance 480p videos: a 12 s loop (empty -> peek -> tap -> duck away -> empty) and an 8 s one-shot
(empty -> tapping the glass).
Usage: hf_alien_peek.py <out_dir> <peephole_still> <ref_image>"""
import os
import sys
import time
import urllib.request

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

out, anchor, ref = sys.argv[1:4]
os.makedirs(out, exist_ok=True)

KEEP = ("Keep exactly the same door peephole view as image 1: the same extreme fisheye lens with barrel distortion, the same "
        "circular frame fading to black, the same dim apartment hallway, warm ceiling light, wooden floor and framed "
        "pictures. Hyperrealistic photograph, photoreal. No text, no watermark. ")
EMPTY = KEEP + "The hallway is completely empty: remove the alien entirely and show the hallway and floor behind where it stood."
TAP = KEEP + (
    "The same alien as images 1 and 2 stands a little further back from the door than in image 1, so its head, shoulders, "
    "slender chest and arms are visible. It raises one long thin finger and touches the peephole glass, its fingertip large "
    "and close to the lens in the foreground, its head tilted with a curious, inspecting, friendly expression. Real living "
    "skin with blue, lavender and faint green mottling, huge glossy black almond eyes.")
LOOP = (
    "Seen through a door peephole fisheye lens, locked camera, the hallway starts empty. Slowly the top of the friendly "
    "alien's big head sneaks up from the bottom edge of the frame, then its huge glossy black eyes peek over, cautious and "
    "curious. It rises up, looks around, steps a little closer, raises one long thin finger and taps on the peephole glass "
    "two or three times, inspecting it with its head tilted, curious and friendly. Then it slowly ducks back down out of "
    "the bottom of the frame, leaving the hallway empty again. Gentle and playful, never menacing. Fisheye distortion stays "
    "constant. One continuous shot, no cuts.")
SHOT = (
    "Seen through a door peephole fisheye lens, locked camera, the hallway starts empty. Slowly the top of the friendly "
    "alien's big head sneaks up from the bottom edge of the frame, then its huge glossy black eyes peek over, cautious and "
    "curious. It rises up, looks around, then raises one long thin finger and taps on the peephole glass, inspecting it with "
    "its head tilted, curious and friendly. Gentle and playful, never menacing. Fisheye distortion stays constant. One "
    "continuous shot, no cuts.")
NEG = "text, watermark, letters, signature, logo, painting, illustration, cartoon, scary, menacing, teeth"


def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)


anchor_url, ref_url = hf.upload_file(anchor), hf.upload_file(ref)
c_empty = hf.submit("alibaba/qwen-image-3/edit", arguments={
    "prompt": EMPTY, "image_urls": [anchor_url], "resolution": "1k", "aspect_ratio": "1:1", "negative_prompt": NEG + ", alien, creature, person"})
c_tap = hf.submit("alibaba/qwen-image-3/edit", arguments={
    "prompt": TAP, "image_urls": [anchor_url, ref_url], "resolution": "1k", "aspect_ratio": "1:1", "negative_prompt": NEG})
urls = {}
for name, c in (("empty", c_empty), ("tap", c_tap)):
    urls[name] = wait(c)["images"][0]["url"]
    urllib.request.urlretrieve(urls[name], f"{out}/alien-peek-{name}-still.png")
    print("still done", name, flush=True)

vids = {
    "alien-peek-loop": hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
        "image_url": urls["empty"], "end_image_url": urls["empty"], "prompt": LOOP,
        "resolution": "480p", "duration": 12, "generate_audio": False}),
    "alien-peek-oneshot": hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
        "image_url": urls["empty"], "end_image_url": urls["tap"], "prompt": SHOT,
        "resolution": "480p", "duration": 8, "generate_audio": False}),
}
for name, c in vids.items():
    try:
        urllib.request.urlretrieve(wait(c)["video"]["url"], f"{out}/{name}.mp4")
        print("video done", name, flush=True)
    except Exception as e:
        print("video failed", name, type(e).__name__, str(e)[:200], flush=True)
