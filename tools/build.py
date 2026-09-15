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
EMAIL = "hello@marigui.fr"
INSTAGRAM = "https://www.instagram.com/terriendutout/"
FORMSPREE = "https://formspree.io/f/xnpqknje"

# ---------------------------------------------------------------- sections
# series: (file-name prefix, filter label). Several prefixes may share a label.
SECTIONS = [
    dict(slug="surf", title="Surf", teaser="Line-ups & ocean",
         pitch="Surf shot from the water and the air.",
         reels=["img/video/surf-1", "img/video/surf-2", "img/video/surf-3"],
         intro="Where the ocean sets the pace. Dawn sessions, empty line-ups, good surfing.",
         cover="img/surf/thumbs/surf-indo-03.webp", cta="A surf collab?",
         series=[("surf-indo", "Indonesia"), ("surf", "Atlantic")]),
    dict(slug="vanlife", title="Vanlife", teaser="Life on the road",
         pitch="Real van life, filmed from the inside: the roads, the spots. Content that makes people want to book the trip.",
         reels=["img/video/vanlife-1", "img/video/vanlife-3", "img/video/vanlife-2"],
         intro="Home is wherever we park. Slow mornings, long roads, and the small rituals of living in a few square metres.",
         cover="img/vanlife/thumbs/vanlife-bardenas-08.webp", cta="A road trip to shoot?",
         cols=6,
         series=[("vanlife-east-coast", "US East Coast"), ("vanlife-west-coast", "US West Coast"),
                 ("vanlife-national-parks", "National Parks"), ("vanlife-bardenas", "Bardenas"),
                 ("vanlife-ireland", "Ireland")]),
    dict(slug="landscapes", title="Landscapes", teaser="Land, sea & sky",
         intro="Wild places, shot at eye level. Volcanic coasts, fall forests, jungle beaches, and the light in between.",
         cover="img/gallery/thumbs/landscapes-thailand-11.webp", cta="Need a landscape series?",
         series=[("landscapes-canaries", "Canary Islands"), ("landscapes-costa-rica", "Costa Rica"),
                 ("landscapes-fall-us", "US Fall"), ("landscapes-thailand", "Thailand"),
                 ("landscapes-misc", "Elsewhere")]),
    dict(slug="cities", title="Cities", teaser="Streets & skylines",
         intro="Cities walked, not toured. Bridges at golden hour, neon after dark, and the quiet corners in between.",
         cover="img/gallery/thumbs/city-new-york-12.webp", cta="A city story to tell?",
         series=[("city-vietnam", "Vietnam"), ("pastel", "Pastel"), ("baseball", "Baseball"),
                 ("city-boston", "Boston"), ("city-new-york", "New York"), ("city-chicago", "Chicago"),
                 ("landscapes-san-francisco", "San Francisco"), ("city-misc", "Elsewhere")]),
    dict(slug="projects", title="Projects", teaser="Brand & people work",
         intro="Selected work shot for and with brands and people, on location, in natural light.",
         cover="img/projects/thumbs/project-martines-20.webp", cta="Want to collaborate?",
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
<link rel="stylesheet" href="/assets/site.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='14' fill='%23FFCB3D' stroke='%23111' stroke-width='2'/%3E%3Ccircle cx='11' cy='13' r='1.8' fill='%23111'/%3E%3Ccircle cx='21' cy='13' r='1.8' fill='%23111'/%3E%3Cpath d='M10 19 Q16 24.5 22 19' stroke='%23111' stroke-width='2' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
</head>
<body>
"""

def topnav(current=None, home=False):
    links = "".join(
        f'<a href="/{s["slug"]}/"{" class=on" if s["slug"] == current else ""}>{s["title"]}</a>'
        for s in SECTIONS)
    about = '<a href="#about">About</a>' if home else '<a href="/#about">About</a>'
    contact = "#contact" if home else "/#contact"
    return f"""<header class="nav" id="nav"><div class="wrap">
  <a class="mark" href="/">Marigui</a>
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
<script src="/assets/site.js"></script>
</body>
</html>
"""

def shot(p, label, i):
    return (f'<figure class="shot" data-hd="/{p["hd"]}" data-cap="{html.escape(label)}">'
            f'<img src="/{p["thumb"]}" width="{p["w"]}" height="{p["h"]}" loading="lazy" decoding="async" '
            f'alt="{html.escape(label)} {p["n"]:02d}"><figcaption>{html.escape(label)}</figcaption></figure>\n')

# ---------------------------------------------------------------- pages
def build_section(sec, lib):
    # group photos by label, keeping config order (several prefixes may share a label)
    groups, order = {}, []
    for prefix, label in sec["series"]:
        if label not in groups:
            groups[label] = []; order.append(label)
        groups[label] += lib.get(prefix, [])
    blocks, count = [], 0
    for k, label in enumerate(order, 1):
        photos = groups[label]
        if not photos:
            continue
        shots = "".join(shot(p, label, count + i) for i, p in enumerate(photos))
        count += len(photos)
        blocks.append(f"""<section class="series" id="{slugify(label)}">
  <div class="shead"><span>{html.escape(label)}</span><span class="dot"></span><span>{k:02d}</span></div>
  <div class="wall" style="--cols:{sec.get('cols', 5)}">
{shots}  </div>
</section>
""")
    jump = "".join(f'<a href="#{slugify(l)}">{html.escape(l)}</a>' for l in order if groups[l])
    # optional video reels: <base>.mp4 (+ <base>.webp poster), 9:16, short muted loops
    reels = [r for r in sec.get("reels", []) if os.path.exists(r + ".mp4")]
    hero = ""
    if reels:
        cards = "".join(
            f'<video class="reel" autoplay muted loop playsinline preload="metadata"'
            f'{" poster=" + chr(34) + "/" + r + ".webp" + chr(34) if os.path.exists(r + ".webp") else ""}>'
            f'<source src="/{r}.mp4" type="video/mp4"></video>\n' for r in reels)
        hero = f"""<section class="reelswrap">
<div class="reels reels-{sec['slug']}">
{cards}</div>
<p class="pitch">{html.escape(sec.get("pitch", ""))}</p>
</section>
"""
    page = head(f"{sec['title']} · Marigui", sec["intro"]) + topnav(sec["slug"]) + f"""
<section class="rhead"><div class="wrap">
  <a class="back" href="/">← All works</a>
  <h1>{sec['title']}</h1>
  <p>{html.escape(sec['intro'])}</p>
  <nav class="jump">{jump}</nav>
</div></section>
{hero}{''.join(blocks)}<div class="foot">
  <a href="/#contact">{html.escape(sec['cta'])}</a>
  <div class="sub">Let's talk</div>
</div>
""" + lightbox()
    out_path = f"{sec['slug']}/index.html"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        fh.write(page)
    return count

def build_home(lib):
    tiles = "".join(
        f'<a class="tile" href="/{s["slug"]}/"><img src="/{s["cover"]}" alt="{s["title"]}" loading="{"eager" if i < 3 else "lazy"}">'
        f'<span class="label"><span class="t">{s["title"]}</span></span></a>\n'
        for i, s in enumerate(SECTIONS))
    featured = "".join(shot(p, "Selected", i) for i, p in enumerate(lib.get(FEATURED_PREFIX, [])))
    foot_links = "".join(f'<a href="/{s["slug"]}/">{s["title"]}</a>' for s in SECTIONS)
    page = head("Marigui · Travel photographer & filmmaker",
                "Surf, vanlife, landscapes and cities. Photo and video shot slow, on location.") + topnav(home=True) + f"""
<section class="hero"><div class="wrap">
  <div class="hero-row">
    <h1 class="wordmark">Marigui</h1>
    <p class="claim">Photo &amp; video content, for your channels or mine.</p>
  </div>
  <p class="tagline">Far, slow, in frames</p>
  <div class="allworks"><span>All works</span><span class="dot"></span><span>{YEAR}</span></div>
</div>
<div class="tiles">
{tiles}</div></section>
<section class="offer"><div class="wrap">
  <h2>Work together.</h2>
  <div class="offer-grid">
    <div><div class="num">01</div><h3>Brand content</h3><p>On-location shoots for brands: places, products and people, delivered ready to publish for your socials and campaigns.</p></div>
    <div><div class="num">02</div><h3>Reels &amp; short video</h3><p>Vertical formats filmed on location, cut for Instagram and TikTok, hook to end card.</p></div>
    <div><div class="num">03</div><h3>Editing &amp; colour</h3><p>Cutting and colour grading of what we shoot together, delivered web-ready.</p></div>
    <div><div class="num">04</div><h3>On my channels</h3><p>Posts and reels published on @terriendutout, for a surf, van and outdoor audience that follows the road. Shoot and distribution in one collab.</p></div>
  </div>
  <div class="audience"><a href="{INSTAGRAM}" target="_blank" rel="noopener">@terriendutout</a><span class="sep"></span><span>2 to 6k views per post</span><span class="sep"></span><span>on the road, Asia to Europe, 2026/2027</span></div>
</div></section>


<section class="selected"><div class="wrap">
  <div class="allworks"><span>Selected</span><span class="dot"></span><span>A few favourites</span></div>
</div>
<div class="wall sel">
{featured}</div></section>

<section class="about" id="about"><div class="wrap"><div class="row">
  <div class="portraits">
    <img src="/img/me-1.webp" alt="Marigui" loading="lazy" width="1067" height="1600">
    <img src="/img/me-2.webp" alt="Marigui" loading="lazy" width="1067" height="1600">
  </div>
  <div>
    <h2><span class="I">I</span> photograph the road, at eye level.</h2>
    <p>Surf, vanlife, wild places and cities, shot slow. Images made on location, off the beaten path, and edited with care. Currently on the road, overland across Asia to Europe.</p>
  </div>
</div></div></section>

<footer id="contact"><div class="wrap">
  <div class="talk">
    <div class="cols">
      <div><div class="h">Contact</div>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></div>
      <div><div class="h">Sections</div>{foot_links}</div>
    </div>
    <div class="say">
      <h2 class="cta">Let's talk →</h2>
      <p class="lead">A brand, a trip, a story to shoot? Drop me a line.</p>
    </div>
    <form class="cform" action="{FORMSPREE}" method="POST">
      <label>Name<input type="text" name="name" required autocomplete="name"></label>
      <label>Email<input type="email" name="email" required autocomplete="email"></label>
      <label><span><span class="I">I</span>'m looking for</span><select name="looking_for" required><option value="" selected disabled></option><option>A shoot</option><option>Content on your channels</option><option>Both</option></select></label>
      <label>Message<textarea name="message" rows="3" required></textarea></label>
      <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" style="display:none">
      <button type="submit">Send</button>
    </form>
  </div>
  <div class="fine">© {YEAR} Marigui</div>
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
