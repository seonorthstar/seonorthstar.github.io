"""Final SEO Northstar logo asset build (Round 5 spec) → website repo.
Usage: python3 build_final.py /path/to/repo"""
import os, sys, subprocess, io
from PIL import Image
from fontTools.ttLib import TTFont
from shape import shaped
from gen3 import pin_mark, NAVY, GOLD, OFF

REPO = sys.argv[1]
LOGO = os.path.join(REPO, "assets", "logo"); os.makedirs(LOGO, exist_ok=True)
tt = TTFont("fonts/sg-700.ttf")
CAP, OVER = 700, 14
SPACE = tt["hmtx"][tt.getBestCmap()[32]][0]
TRACK = -0.01

def svg(W, H, inner, bg=None, rx=0):
    rect = f'<rect width="{W:.2f}" height="{H:.2f}" rx="{rx:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
            f'width="{W:.0f}" height="{H:.0f}" role="img" aria-label="SEO Northstar">'
            f'<title>SEO Northstar</title>{rect}{inner}</svg>\n')

def primary_inner(fg, star):
    """Round 5 lockup at cap height 70 (font size 100). Returns inner, W, H."""
    S = 100; k = S / 1000
    cap, over = CAP * k, OVER * k; tip = 1.5 * over
    space = SPACE * k + TRACK * S
    d, ww = shaped("SEO Northstar", "sg-700", S, 0, 0, TRACK)
    body, mw, mh = pin_mark(fg, star)
    ih = cap + over + tip; sc = ih / mh; iw = mw * sc
    tx = iw + space
    inner = (f'<g transform="translate(0,0) scale({sc:.5f})">{body}</g>'
             f'<g transform="translate({tx:.3f},{over + cap:.3f})"><path d="{d}" fill="{fg}"/></g>')
    return inner, tx + ww, ih

def stacked_inner(fg, star):
    S = 100; k = S / 1000; cap = CAP * k
    d, ww = shaped("SEO Northstar", "sg-700", S, 0, 0, TRACK)
    body, mw, mh = pin_mark(fg, star)
    ih = 2.6 * cap; sc = ih / mh; iw = mw * sc
    gap = 0.6 * cap
    inner = (f'<g transform="translate({(ww - iw)/2:.3f},0) scale({sc:.5f})">{body}</g>'
             f'<g transform="translate(0,{ih + gap + cap:.3f})"><path d="{d}" fill="{fg}"/></g>')
    return inner, ww, ih + gap + cap

def icon_inner(fg, star, box=100, fill=0.70):
    body, mw, mh = pin_mark(fg, star)
    sc = fill * box / mh; w = mw * sc; h = mh * sc
    return f'<g transform="translate({(box - w)/2:.3f},{(box - h)/2:.3f}) scale({sc:.5f})">{body}</g>'

def pad(inner, W, H, p):
    return f'<g transform="translate({p:.3f},{p:.3f})">{inner}</g>', W + 2 * p, H + 2 * p

def write(path, text):
    open(path, "w").write(text)
    subprocess.run(["svgo", "-q", "--multipass", path, "-o", path], check=True)

def png(svg_path, out, w=None, h=None):
    a = ["rsvg-convert"] + (["-w", str(w)] if w else []) + (["-h", str(h)] if h else []) + [svg_path, "-o", out]
    subprocess.run(a, check=True)
    subprocess.run(["python3", "-c", f"from PIL import Image; Image.open('{out}').save('{out}', optimize=True)"], check=True)

# ---- vector logos (transparent backgrounds, no padding: clear space is a usage rule)
for name, fg in (("seo-northstar-logo", NAVY), ("seo-northstar-logo-reverse", OFF)):
    i, W, H = primary_inner(fg, GOLD); write(f"{LOGO}/{name}.svg", svg(W, H, i))
for name, fg in (("seo-northstar-logo-stacked", NAVY), ("seo-northstar-logo-stacked-reverse", OFF)):
    i, W, H = stacked_inner(fg, GOLD); write(f"{LOGO}/{name}.svg", svg(W, H, i))
i, W, H = primary_inner(NAVY, NAVY); write(f"{LOGO}/seo-northstar-logo-mono.svg", svg(W, H, i))
i, W, H = primary_inner(OFF, OFF); write(f"{LOGO}/seo-northstar-logo-mono-reverse.svg", svg(W, H, i))
write(f"{LOGO}/seo-northstar-icon.svg", svg(100, 100, icon_inner(NAVY, GOLD, fill=1.0)))

# ---- app/favicon tile: gold square, navy pin, off-white star (most distinctive in SERPs)
TILE = svg(100, 100, icon_inner(NAVY, OFF), bg=GOLD, rx=22)
TILE_SQ = svg(100, 100, icon_inner(NAVY, OFF, fill=0.62), bg=GOLD)        # full-bleed for iOS / OG
write(f"{REPO}/favicon.svg", TILE)
write(f"{LOGO}/seo-northstar-app-icon.svg", TILE_SQ)

# ---- PNG renders
for s in (16, 32, 48, 96, 144, 192, 512):
    png(f"{REPO}/favicon.svg", f"{REPO}/favicon-{s}.png", w=s, h=s)
png(f"{LOGO}/seo-northstar-app-icon.svg", f"{REPO}/apple-touch-icon.png", w=180, h=180)
ims = []
for s in (16, 32, 48):
    subprocess.run(["rsvg-convert", "-w", str(s), "-h", str(s), f"{REPO}/favicon.svg", "-o", f"/tmp/ico{s}.png"], check=True)
Image.open("/tmp/ico48.png").save(f"{REPO}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

for n in ("seo-northstar-logo", "seo-northstar-logo-reverse", "seo-northstar-logo-stacked", "seo-northstar-logo-stacked-reverse"):
    png(f"{LOGO}/{n}.svg", f"{LOGO}/{n}.png", w=1200)

# ---- existing asset filenames kept stable, regenerated with the new logo
i, W, H = stacked_inner(OFF, GOLD)
sc = 520 / W
write("/tmp/sq.svg", svg(800, 800, f'<g transform="translate({(800 - W*sc)/2:.2f},{(800 - H*sc)/2:.2f}) scale({sc:.4f})">{i}</g>', bg=NAVY))
png("/tmp/sq.svg", f"{REPO}/assets/logo-square.png", w=800, h=800)
i, W, H = primary_inner(OFF, GOLD); sc = 320 / W
write("/tmp/ls.svg", svg(400, 300, f'<g transform="translate({(400 - W*sc)/2:.2f},{(300 - H*sc)/2:.2f}) scale({sc:.4f})">{i}</g>', bg=NAVY))
png("/tmp/ls.svg", f"{REPO}/assets/logo-landscape-400x300.png", w=400, h=300)
write("/tmp/ci.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{GOLD}"/>{icon_inner(NAVY, OFF, fill=0.58)}</svg>')
png("/tmp/ci.svg", f"{REPO}/assets/logo-icon-circular.png", w=800, h=800)

# ---- social share image 1200x630
i, W, H = primary_inner(OFF, GOLD); sc = 760 / W
line = "Local SEO for small businesses across the UK"
d2, w2 = shaped(line, "inter-500", 34, 0, 0)
y0 = 315 - (H * sc + 70) / 2
og = (f'<g transform="translate({(1200 - W*sc)/2:.2f},{y0:.2f}) scale({sc:.4f})">{i}</g>'
      f'<g transform="translate({(1200 - w2)/2:.2f},{y0 + H*sc + 70:.2f})"><path d="{d2}" fill="{GOLD}"/></g>')
write("/tmp/og.svg", svg(1200, 630, og, bg=NAVY))
png("/tmp/og.svg", f"{REPO}/og-image.png", w=1200, h=630)

PRIMARY_REVERSE_W = primary_inner(OFF, GOLD)[1:]
print("header logo aspect W/H =", PRIMARY_REVERSE_W[0] / PRIMARY_REVERSE_W[1])
