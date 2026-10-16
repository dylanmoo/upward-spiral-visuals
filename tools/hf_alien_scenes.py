"""Alien peephole scenes: full-body stills through the same peephole (Qwen edit, anchored on the peephole still and the
design reference), then a seamless 8 s 480p Seedance loop per scene (same first and last frame).
Usage: hf_alien_scenes.py <out_dir> <peephole_still> <ref_image> [scene ...]"""
import os
import sys
import time
import urllib.request

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

out, anchor, ref = sys.argv[1:4]
only = set(sys.argv[4:])
os.makedirs(out, exist_ok=True)

BASE = (
    "Same door peephole view as image 1: the same extreme fisheye lens with barrel distortion, the same circular frame fading "
    "to black, the same dim apartment hallway with the warm ceiling light, wooden floor and framed pictures. The same alien as "
    "images 1 and 2 (large smooth cranium, huge glossy black almond eyes, pale skin with blue, lavender and faint green "
    "mottling), now seen full body a few steps back from the door, with a slender, smooth grey-lavender body and long thin "
    "arms and legs. Hyperrealistic photograph, real living skin, cinematic, photoreal. No text, no watermark. "
)
SCENES = {
    "dance": (
        "The alien is mid-dance in the middle of the hallway, hips cocked to one side, knees bent, long arms up, a happy "
        "playful expression, clearly enjoying itself.",
        "Seen through the same door peephole fisheye lens. The friendly alien dances in the hallway, shaking its hips and "
        "booty side to side to a beat, bouncing its knees, shimmying its shoulders and waving its long thin arms. It turns "
        "to wiggle its backside toward the door, then turns back with a happy look. Goofy, joyful, completely carefree. "
        "Locked camera, fisheye distortion stays constant. One continuous shot, no cuts."),
    "meditate": (
        "The alien floats calmly in mid-air in the exact center of the hallway, about half a meter above the floor, seated "
        "in double lotus pose with each foot resting on the opposite thigh, hands resting on its knees in a mudra, a serene "
        "peaceful expression, a faint soft glow around its body.",
        "Seen through the same door peephole fisheye lens. The friendly alien floats in mid-air in the center of the hallway "
        "in double lotus pose, meditating. It bobs gently up and down a few centimeters, breathing slowly and calmly, the "
        "faint glow around it softly pulsing, dust motes drifting through the warm light. Serene and peaceful. Locked "
        "camera, fisheye distortion stays constant. One continuous shot, no cuts."),
    "handstand": (
        "The alien is crouched in the middle of the hallway with both hands flat on the floor, about to kick up into a "
        "handstand, a determined but slightly nervous expression.",
        "Seen through the same door peephole fisheye lens. The friendly alien tries to do a handstand in the hallway: it "
        "kicks its thin legs up, wobbles upside down for a moment with its legs flailing, then tips over and flops onto the "
        "floor in a goofy heap. It sits up, shakes its big head, gets back up a little embarrassed and crouches with its "
        "hands on the floor, ready to try again. Clumsy, comedic, harmless. Locked camera, fisheye distortion stays "
        "constant. One continuous shot, no cuts."),
}
NEG = "text, watermark, letters, signature, logo, painting, illustration, cartoon, scary, menacing, teeth, clothing"


def wait(ctrl):
    while True:
        st = ctrl.status()
        if isinstance(st, hf.Completed):
            return ctrl.get()
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            raise RuntimeError(type(st).__name__)
        time.sleep(8)


anchor_url, ref_url = hf.upload_file(anchor), hf.upload_file(ref)
scenes = {k: v for k, v in SCENES.items() if not only or k in only}
stills = {k: hf.submit("alibaba/qwen-image-3/edit", arguments={
    "prompt": BASE + pose, "image_urls": [anchor_url, ref_url], "resolution": "1k", "aspect_ratio": "1:1",
    "negative_prompt": NEG}) for k, (pose, _) in scenes.items()}
videos = {}
for k, c in stills.items():
    try:
        url = wait(c)["images"][0]["url"]
        urllib.request.urlretrieve(url, f"{out}/alien-{k}-still.png")
        print("still done", k, flush=True)
        videos[k] = hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
            "image_url": url, "end_image_url": url, "prompt": scenes[k][1],
            "resolution": "480p", "duration": 8, "generate_audio": False})
    except Exception as e:
        print("still failed", k, type(e).__name__, str(e)[:200], flush=True)
for k, c in videos.items():
    try:
        urllib.request.urlretrieve(wait(c)["video"]["url"], f"{out}/alien-{k}-loop.mp4")
        print("video done", k, flush=True)
    except Exception as e:
        print("video failed", k, type(e).__name__, str(e)[:200], flush=True)
