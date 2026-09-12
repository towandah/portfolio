#!/usr/bin/env python3
"""
Regenerate wall thumbnails from the HD WebP files.

img/<folder>/<name>.webp  ->  img/<folder>/thumbs/<name>.webp  (800 px long edge, q78)

Usage:  python3 tools/make_thumbs.py            (only missing thumbs)
        python3 tools/make_thumbs.py --force    (rebuild all)
"""
import os, sys, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MAXE, Q = 800, 78
force = "--force" in sys.argv
n = 0
for src in sorted(glob.glob("img/*/*.webp")):
    folder = os.path.dirname(src)
    dst = os.path.join(folder, "thumbs", os.path.basename(src))
    if os.path.exists(dst) and not force:
        continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        w, h = im.size
        s = MAXE / max(w, h)
        if s < 1:
            im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
        kw = dict(quality=Q, method=4)
        if icc:
            kw["icc_profile"] = icc
        im.save(dst + ".tmp.webp", "WEBP", **kw)
    os.replace(dst + ".tmp.webp", dst)
    n += 1
print(f"{n} thumbnails written")
