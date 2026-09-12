#!/usr/bin/env python3
"""
Marigui — static site builder.

Reads every WebP in img/<folder>/ (HD) + img/<folder>/thumbs/ (wall thumbnails),
groups them by series (file-name prefix), and writes the HTML pages at the repo root.

Usage:  python3 tools/build.py        (run from the repo root, needs Pillow)
Then:   git add -A && git commit -m "Update site" && git push
"""
import os, re, glob, html
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

YEAR = "2026"
EMAIL = "marigui@gmail.com"
INSTAGRAM = "https://instagram.com/"

# ---------------------------------------------------------------- sections
# series: (file-name prefix, filter label). Several prefixes may share a label.
SECTIONS = [
    dict(slug="surf", title="Surf", teaser="Line-ups & ocean",
         intro="Where the ocean sets the pace. Dawn sessions, empty line-ups, and the salt that stays on the lens.",
         cover="img/surf/thumbs/surf-13.webp", cta="A surf collab?",
         series=[("surf", "Atlantic"), ("surf-indo", "Indonesia")]),
    dict(slug="vanlife", title="Vanlife", teaser="Life on the road",
         intro="Home is wherever we park. Slow mornings, long roads and the small rituals of living in a few square metres.",
         cover="img/vanlife/thumbs/vanlife-bardenas-04.webp", cta="A road trip to shoot?",
         series=[("vanlife-bardenas", "Bardenas"), ("vanlife-ireland", "Ireland"),
                 ("vanlife-east-coast", "US East Coast"), ("vanlife-west-coast", "US West Coast"),
                 ("vanlife-national-parks", "National Parks")]),
    dict(slug="landscapes", title="Landscapes", teaser="Land, sea & sky",
         intro="Wild places, shot at eye level. Volcanic coasts, fall forests, jungle beaches — and the light in between.",
         cover="img/gallery/thumbs/landscapes-fall-us-10.webp", cta="Need a landscape series?",
         series=[("landscapes-canaries", "Canary Islands"), ("landscapes-costa-rica", "Costa Rica"),
                 ("landscapes-fall-us", "US Fall"), ("landscapes-thailand", "Thailand"),
                 ("landscapes-misc", "More")]),
    dict(slug="cities", title="Cities", teaser="Streets & skylines",
         intro="Cities walked, not toured. Bridges at golden hour, neon after dark, and the quiet corners in between.",
         cover="img/gallery/thumbs/city-new-york-13.webp", cta="A city story to tell?",
         series=[("city-boston", "Boston"), ("baseball", "Boston"), ("city-chicago", "Chicago"),
                 ("city-new-york", "New York"), ("landscapes-san-francisco", "San Francisco"),
                 ("city-vietnam", "Vietnam"), ("city-misc", "More"), ("pastel", "More")]),
    dict(slug="collabs", title="Collabs", teaser="Brand work",
         intro="Selected work shot for and with brands and people — on location, in natural light.",
         cover="img/collabs/thumbs/project-martines-20.webp", cta="Want to collaborate?",
         series=[("project-martines", "Chez Martine"), ("project-arrose", "Arrosé"), ("project-anna", "Anna")]),
]
FEATURED_PREFIX = "featured"

# ---------------------------------------------------------------- scan images
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def scan():
    """Return {prefix: [dict(name, hd, thumb, w, h, n)]} sorted by number."""
    out = {}
    for thumb in glob.glob("img/*/thumbs/*.webp"):
        folder = thumb.split("/")[1]
        name = os.path.basename(thumb)[:-5]
        m = re.match(r"^(.*)-(\d+)$", name)
        if not m:
            continue
        prefix, n = m.group(1), int(m.group(2))
        hd = f"img/{folder}/{name}.webp"
        if not os.path.exists(hd):
            continue
        with Image.open(thumb) as im:
            w, h = im.size
        out.setdefault(prefix, []).append(dict(name=name, hd=hd, thumb=thumb, w=w, h=h, n=n))
    for v in out.values():
        v.sort(key=lambda d: d["n"])
    return out

# ---------------------------------------------------------------- html bits
def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
"""

def topnav(current=None, home=False):
    links = "".join(
        f'<a href="{s["slug"]}.html"{" class=on" if s["slug"] == current else ""}>{s["title"]}</a>'
        for s in SECTIONS)
    about = '<a href="#about">About</a>' if home else '<a href="index.html#about">About</a>'
    contact = "#contact" if home else "index.html#contact"
    return f"""<header class="nav" id="nav"><div class="wrap">
  <a class="mark" href="index.html">Marigui</a>
  <nav class="links">{links}{about}</nav>
  <a class="contact" href="{contact}">Contact</a>
  <button class="navtoggle" aria-label="Menu" aria-expanded="false">Menu</button>
</div></header>
"""

def lightbox():
    return """<div class="lb" id="lb" aria-hidden="true" role="dialog" aria-label="Photo viewer">
  <button class="lb-x" aria-label="Close">×</button>
  <button class="lb-prev" aria-label="Previous">←</button>
  <button class="lb-next" aria-label="Next">→</button>
  <figure><img id="lbimg" alt=""><figcaption><span id="lbcap"></span><span id="lbnum"></span></figcaption></figure>
</div>
<script src="assets/site.js"></script>
</body>
</html>
"""

def shot(p, label, filt):
    return (f'<figure class="shot" data-f="{filt}" data-hd="{p["hd"]}" data-cap="{html.escape(label)}">'
            f'<img src="{p["thumb"]}" width="{p["w"]}" height="{p["h"]}" loading="lazy" decoding="async" '
            f'alt="{html.escape(label)} — {p["n"]:02d}"><figcaption>{html.escape(label)}</figcaption></figure>\n')

# ---------------------------------------------------------------- pages
def build_section(sec, lib):
    # filters, in config order, de-duplicated
    filters = []
    for _, label in sec["series"]:
        if label not in [f[1] for f in filters]:
            filters.append((slugify(label), label))
    shots, count = [], 0
    for prefix, label in sec["series"]:
        for p in lib.get(prefix, []):
            shots.append(shot(p, label, slugify(label)))
            count += 1
    pill = ""
    if len(filters) > 1:
        btns = '<button class="on" data-f="all">All</button>' + "".join(
            f'<button data-f="{k}">{html.escape(l)}</button>' for k, l in filters)
        pill = f'<div class="pill"><div class="bar" id="bar">{btns}</div></div>\n'
    page = head(f"{sec['title']} — Marigui", sec["intro"]) + topnav(sec["slug"]) + f"""
<section class="rhead"><div class="wrap">
  <a class="back" href="index.html">← All works</a>
  <h1>{sec['title']}</h1>
  <p>{html.escape(sec['intro'])}</p>
  <div class="meta">{count} photos</div>
</div></section>
{pill}<section class="wall" id="wall">
{''.join(shots)}</section>
<div class="foot">
  <a href="index.html#contact">{html.escape(sec['cta'])}</a>
  <div class="sub">Let's talk</div>
</div>
""" + lightbox()
    with open(f"{sec['slug']}.html", "w") as fh:
        fh.write(page)
    return count

def build_home(lib):
    tiles = "".join(
        f'<a class="tile" href="{s["slug"]}.html"><img src="{s["cover"]}" alt="{s["title"]}" loading="{"eager" if i < 3 else "lazy"}">'
        f'<span class="label"><span class="t">{s["title"]}</span><span class="c">{html.escape(s["teaser"])}</span></span></a>\n'
        for i, s in enumerate(SECTIONS))
    featured = "".join(shot(p, "Selected", "all") for p in lib.get(FEATURED_PREFIX, []))
    foot_links = "".join(f'<a href="{s["slug"]}.html">{s["title"]}</a>' for s in SECTIONS)
    page = head("Marigui — Travel photographer & filmmaker",
                "Surf, vanlife, landscapes and cities — photo and video shot slow, on location.") + topnav(home=True) + f"""
<section class="hero"><div class="wrap">
  <h1 class="wordmark">Marigui</h1>
  <p class="tagline">Far, slow, in frames.</p>
  <div class="allworks"><span>All works</span><span class="dot"></span><span>{YEAR}</span></div>
</div>
<div class="tiles">
{tiles}</div></section>

<section class="selected"><div class="wrap">
  <div class="allworks"><span>Selected</span><span class="dot"></span><span>A few favourites</span></div>
</div>
<div class="wall sel" id="wall">
{featured}</div></section>

<section class="about" id="about"><div class="wrap"><div class="row">
  <!-- Portrait: drop a file at img/me.webp (portrait format) and it shows up here -->
  <div class="portrait">{'<img src="img/me.webp" alt="Marigui">' if os.path.exists('img/me.webp') else '<span class="ph"></span>'}</div>
  <div>
    <h2>I photograph the road, at eye level.</h2>
    <p>Surf, vanlife, wild places and cities — shot slow. Images made on location, off the beaten path, and edited with care.</p>
  </div>
</div></div></section>

<section class="offer"><div class="wrap">
  <h2>Work together.</h2>
  <div class="offer-grid">
    <div><div class="num">01</div><h3>Brand content</h3><p>On-location reportage, photo and video, delivered ready to publish for your socials and campaigns.</p></div>
    <div><div class="num">02</div><h3>Travel series</h3><p>Surf, outdoor, van, cities — themed series to license or adapt.</p></div>
    <div><div class="num">03</div><h3>Video &amp; editing</h3><p>Short formats built for the web, shot light and edited with care.</p></div>
  </div>
</div></section>

<footer id="contact"><div class="wrap">
  <a class="cta" href="mailto:{EMAIL}?subject=Collaboration">Let's talk →</a>
  <div class="cols">
    <div><div class="h">Contact</div>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></div>
    <div><div class="h">Sections</div>{foot_links}</div>
  </div>
  <div class="fine">© {YEAR} Marigui — Portfolio</div>
</div></footer>
<div class="cpill" id="cpill">See work</div>
""" + lightbox()
    with open("index.html", "w") as fh:
        fh.write(page)

if __name__ == "__main__":
    lib = scan()
    used = set()
    for sec in SECTIONS:
        n = build_section(sec, lib)
        used.update(p for p, _ in sec["series"])
        print(f"{sec['slug']:12s} {n:4d} photos")
    build_home(lib)
    print(f"{'home/featured':12s} {len(lib.get(FEATURED_PREFIX, [])):4d} photos")
    unused = [p for p in lib if p not in used and p != FEATURED_PREFIX]
    if unused:
        print("WARNING — series not shown on any page:", ", ".join(unused))
