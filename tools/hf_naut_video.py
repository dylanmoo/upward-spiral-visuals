"""Animate the chosen nautilus still as a seamless 10 s loop. Usage: hf_naut_video.py <still> <out_mp4>"""
import os, sys, time, urllib.request
os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf
still, out = sys.argv[1:3]
url = hf.upload_file(still)
c = hf.submit("bytedance/seedance-2.0/image-to-video", arguments={
    "image_url": url, "end_image_url": url, "resolution": "1080p", "duration": 10, "generate_audio": False,
    "prompt": "Real macro footage of a halved nautilus shell resting on black velvet. Locked-off camera. A soft band of "
              "natural daylight drifts slowly across the shell, the mother-of-pearl nacre inside the chambers "
              "shimmering with subtle shifting iridescence, faint dust motes floating in the light. The shell itself "
              "does not move or change shape. Calm, hypnotic, true-to-life. One continuous shot, no cuts, no text."})
while True:
    st = c.status()
    if isinstance(st, hf.Completed):
        urllib.request.urlretrieve(c.get()["video"]["url"], out); print("done", flush=True); break
    if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
        print("failed", repr(st)[:500], flush=True); break
    time.sleep(8)
