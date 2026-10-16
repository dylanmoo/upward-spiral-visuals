"""Run Seedance draft jobs on Higgsfield and download results. Usage: hf_run.py <drafts_dir> <refs_dir>"""
import os
import sys
import time
import json
import urllib.request

os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf

drafts, refs = sys.argv[1], sys.argv[2]

STYLE = ("Use @image1 only as a style reference for colors and the glossy space-filling atom rendering; "
         "do not reproduce its composition. ")
TAIL = " Dark navy background with out-of-focus molecules. One continuous shot, no cuts. Seamless loop. No text."

up = {}
def url_for(path):
    if path not in up:
        up[path] = hf.upload_file(path)
    return up[path]

base = {"resolution": "480p", "duration": 5, "generate_audio": False}
jobs = {
    "HF-V3-unzip-helicase": ("bytedance/seedance-2.0/reference-to-video", dict(base, aspect_ratio="16:9",
        image_urls=[url_for(f"{refs}/ref1.png")],
        prompt=STYLE + "New scene: a teal helicase protein made of clustered glossy spheres stays fixed in the center of the frame. "
        "A golden-orange DNA double helix flows continuously into it from the left, and two separated single strands flow "
        "continuously out of it to the right, peeling apart. Locked-off camera, constant conveyor motion." + TAIL)),
    "HF-V6a-tunnel-inside-helix": ("bytedance/seedance-2.0/reference-to-video", dict(base, aspect_ratio="16:9",
        image_urls=[url_for(f"{refs}/ref2.png")],
        prompt=STYLE + "New scene: first-person camera flies forward along the central axis of an endless DNA double helix at a "
        "constant speed. The golden-orange backbone spirals around the edges of the frame while blue, violet and magenta base "
        "pairs rush past. Perfectly centered, symmetrical framing, no change in speed or direction." + TAIL)),
    "HF-V8-horizontal-conveyor": ("bytedance/seedance-2.0/reference-to-video", dict(base, aspect_ratio="16:9",
        image_urls=[url_for(f"{refs}/ref5.png")],
        prompt=STYLE + "New scene: a single DNA double helix runs perfectly horizontally through the exact center of the frame "
        "from edge to edge, flowing steadily from left to right like a conveyor belt and rotating on its own axis. "
        "Locked-off camera, perfectly level." + TAIL)),
    "HF-V7-spiral-truloop": ("bytedance/seedance-2.0/image-to-video", dict(base,
        image_url=url_for(f"{drafts}/frame-V7.png"), end_image_url=url_for(f"{drafts}/frame-V7.png"),
        prompt="The spiral tunnel of DNA and histone beads rotates continuously at a slow, constant speed like a screw "
        "turning. Camera holds perfectly still and centered. One continuous shot, no cuts.")),
    "HF-V2-piston-truloop": ("bytedance/seedance-2.0/image-to-video", dict(base,
        image_url=url_for(f"{drafts}/frame-V2.png"), end_image_url=url_for(f"{drafts}/frame-V2.png"),
        prompt="The repair protein complex hammers down on the DNA strand in a steady repeating rhythm like a piston, "
        "each strike making the DNA shudder and releasing a small burst of loose nucleotides. Locked-off camera. "
        "One continuous shot, no cuts.")),
}

only = set(sys.argv[3:])
ctrls = {}
for name, (model, args) in jobs.items():
    if only and name not in only:
        continue
    try:
        ctrls[name] = hf.submit(model, arguments=args)
        print("submitted", name, flush=True)
    except Exception as e:
        print("submit failed", name, type(e).__name__, str(e)[:300], flush=True)

pending = dict(ctrls)
deadline = time.time() + 1500
while pending and time.time() < deadline:
    for name, c in list(pending.items()):
        st = c.status()
        if isinstance(st, hf.Completed):
            res = c.get()
            url = res["video"]["url"]
            urllib.request.urlretrieve(url, f"{drafts}/{name}.mp4")
            print("done", name, flush=True)
            del pending[name]
        elif isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            print("ended", name, type(st).__name__, str(getattr(st, "__dict__", st))[:300], flush=True)
            del pending[name]
    time.sleep(10)
for name in pending:
    print("timed out", name, flush=True)
