"""Retry the solarpunk loop with progressively cheaper settings until one is accepted.
Usage: hf_solar_retry.py <dir>"""
import os, sys, time, urllib.request
os.environ.setdefault("HF_KEY", os.environ.get("HF_CREDENTIALS", ""))
import higgsfield_client as hf
d = sys.argv[1]
PROMPT = ("Smooth cinematic drone flight through a solarpunk paradise city dominated by nature. The drone glides over "
          "lush meadows and curved earthen buildings with green roofs, between giant ancient trees and past glass "
          "domes full of gardens, under floating islands of land with waterfalls pouring into rivers, sunshine and "
          "clean clear air. Midway, a smiling kid on a hoverboard zooms past close to the camera and waves, then flies "
          "off into the distance. The drone flies one long graceful loop around the giant central tree and returns to "
          "exactly where it started. Photoreal, joyful, golden light. One continuous shot, no cuts, no text.")
TRIES = [("bytedance/seedance-2.5/image-to-video", "1080p", 25), ("bytedance/seedance-2.5/image-to-video", "1080p", 20), ("bytedance/seedance-2.5/image-to-video", "720p", 25),
         ("bytedance/seedance-2.5/image-to-video", "720p", 20), ("bytedance/seedance-2.0/image-to-video", "1080p", 15)]
url = hf.upload_file(f"{d}/solarpunk-still.png")
for model, res, dur in TRIES:
    c = hf.submit(model, arguments={"image_url": url, "end_image_url": url, "prompt": PROMPT,
                                    "resolution": res, "duration": dur, "generate_audio": False})
    while True:
        st = c.status()
        if isinstance(st, hf.Completed):
            urllib.request.urlretrieve(c.get()["video"]["url"], f"{d}/solarpunk-loop-raw.mp4")
            print("done", model, res, dur, flush=True); sys.exit(0)
        if isinstance(st, (hf.Failed, hf.NSFW, hf.Cancelled)):
            err = c._transport.request("GET", c.status_url).json().get("error", "")
            print("failed", model, res, dur, str(err)[:200], flush=True); break
        time.sleep(8)
