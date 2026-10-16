"""Anatomically real nautilus stills, three variants. Usage: hf_naut_stills.py <out_dir>"""
import os, sys, time, urllib.request
os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf
out = sys.argv[1]
ANAT = ("a real Nautilus pompilius shell sliced exactly in half along its center plane, the classic museum cross-section: "
        "one single logarithmic spiral of about thirty gas chambers separated by thin curved pearly septa, the chambers "
        "growing steadily larger as they coil outward from a tiny tight center near one side to the large open body "
        "chamber, the overall outline a rounded snail-like coil, not a circle and not symmetric, a thin siphuncle tube "
        "threading through the septa, the outer wall a cut edge of cream-white shell with brown tiger-stripe flame "
        "markings, the inside lined with real mother-of-pearl nacre with soft natural iridescence, small natural "
        "imperfections, chips and dust. ")
CAM = (" Real photograph, not a render, not an illustration, true-to-life natural color, 100mm macro lens, f/8, sharp "
       "detail, the shell fills most of the square frame and sits centered. No text, no watermark, no symmetry.")
V = {
    "a": "Overhead studio macro photograph of " + ANAT + "Lying flat on a dark weathered slate surface, a single soft "
         "window light from the upper left, deep shadows, dark background." + CAM,
    "b": "Natural history specimen photograph of " + ANAT + "Resting on black velvet, lit by soft diffused daylight, "
         "subtle warm tones, gentle falloff into a pure black background." + CAM,
    "c": "Close-up photograph of " + ANAT + "Lying on wet dark beach sand with tiny grains of sand on the shell, low warm "
         "late-afternoon sunlight raking across the septa, dark moody surroundings." + CAM,
}
cs = {k: hf.submit("xai/grok-imagine-image-2.0", arguments={"prompt": p, "resolution": "2k", "aspect_ratio": "1:1"}) for k, p in V.items()}
for k, c in cs.items():
    while True:
        st = c.status()
        if isinstance(st, hf.Completed):
            r = c.get(); urllib.request.urlretrieve(r["images"][0]["url"], f"{out}/naut2-{k}.png"); print("done", k, r["images"][0]["url"], flush=True); break
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            print("failed", k, type(st).__name__, flush=True); break
        time.sleep(5)
