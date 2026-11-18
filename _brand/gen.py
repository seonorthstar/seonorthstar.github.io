"""SEO Northstar logo generator — 3 directions, all geometry + outlined text."""
import math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

NAVY = "#0F1B2D"
GOLD = "#E8B54D"
OFF = "#F6F4EF"
OUT = "out"
os.makedirs(OUT, exist_ok=True)
FONTS = {}

def font(name):
    if name not in FONTS:
        FONTS[name] = TTFont(f"fonts/{name}.ttf")
    return FONTS[name]

def text_path(s, fontname, size, x, y, tracking=0.0):
    """Return (svg path d, advance width) for text with baseline at (x,y)."""
    f = font(fontname)
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f["head"].unitsPerEm
    sc = size / upm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:
            raise ValueError(f"missing glyph {ch!r} in {fontname}")
        tp = TransformPen(pen, (sc, 0, 0, -sc, x + cx, y))
        gs[g].draw(tp)
        cx += gs[g].width * sc + tracking * size
    return pen.getCommands(), cx - tracking * size

def text_width(s, fontname, size, tracking=0.0):
    return text_path(s, fontname, size, 0, 0, tracking)[1]

def star4(cx, cy, n, e, s, w, inner):
    """4-point star: tip lengths n/e/s/w, inner vertex radius (at 45deg)."""
    k = inner / math.sqrt(2)
    pts = [(cx, cy - n), (cx + k, cy - k), (cx + e, cy), (cx + k, cy + k),
           (cx, cy + s), (cx - k, cy + k), (cx - w, cy), (cx - k, cy - k)]
    return "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in pts) + " Z"

# ---------------------------------------------------------------- marks
# Each mark is drawn in a 100x100 box. fg = main colour, accent = star colour.

def mark_lens(fg, accent):
    """A — Lens Star: magnifying glass, north star inside the lens."""
    return f"""
  <circle cx="42" cy="42" r="27" fill="none" stroke="{fg}" stroke-width="9"/>
  <line x1="62.5" y1="62.5" x2="86" y2="86" stroke="{fg}" stroke-width="12" stroke-linecap="round"/>
  <path d="{star4(42, 42.5, 22, 15, 15, 15, 5.2)}" fill="{accent}"/>"""

def mark_pin(fg, accent):
    """B — North Pin: map pin (local search) with north star cut-out."""
    # teardrop: circle centre (50,40) r 31, point at (50,95)
    r, cx, cy, tipy = 31, 50, 40, 95
    d = tipy - cy
    a = math.acos(r / d)                    # tangent angle from vertical-down
    tx = r * math.sin(a); ty = r * math.cos(a)
    pin = (f"M{cx},{tipy} L{cx - tx:.2f},{cy + ty:.2f} "
           f"A{r},{r} 0 1 1 {cx + tx:.2f},{cy + ty:.2f} Z")
    return f"""
  <path d="{pin}" fill="{fg}"/>
  <path d="{star4(50, 41, 22, 15.5, 15.5, 15.5, 5.4)}" fill="{accent}"/>"""

def mark_ascent(fg, accent):
    """C — Ascent: geometric N whose right stroke rises into a north star."""
    return f"""
  <path d="M14,88 L14,50 L28,50 L28,88 Z" fill="{fg}"/>
  <path d="M14,50 L28,50 L72,88 L58,88 Z" fill="{fg}"/>
  <path d="M58,88 L58,36 L72,36 L72,88 Z" fill="{fg}"/>
  <path d="{star4(65, 17, 17, 11.5, 11.5, 11.5, 4.0)}" fill="{accent}"/>"""

MARKS = {
    "a-lens":   ("Lens Star", mark_lens),
    "b-pin":    ("North Pin", mark_pin),
    "c-ascent": ("Ascent", mark_ascent),
}

# ---------------------------------------------------------------- lockups

def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">{rect}{body}</svg>\n')

def icon(markfn, fg, accent, bg=None, pad=0, rounded=False):
    size = 100 + 2 * pad
    body = ""
    if bg:
        rx = size * 0.22 if rounded else 0
        body += f'<rect width="{size}" height="{size}" rx="{rx:.1f}" fill="{bg}"/>'
    body += f'<g transform="translate({pad},{pad})">{markfn(fg, accent)}</g>'
    return svg(size, size, body)

def horizontal(markfn, fg, accent, text_fg, tag_fg, bg=None, tagline=True):
    """Mark left, 'SEO Northstar' + tagline right."""
    H = 100
    seo_d, seo_w = text_path("SEO", "sg-500", 40, 0, 0)
    gap = 10
    ns_w = text_width("Northstar", "sg-700", 40)
    word_w = seo_w + gap + ns_w
    tx = 118
    base = 56 if tagline else 64
    d1, w1 = text_path("SEO", "sg-500", 40, tx, base)
    d2, _ = text_path("Northstar", "sg-700", 40, tx + w1 + gap, base)
    body = f'<g>{markfn(fg, accent)}</g>'
    body += f'<path d="{d1}" fill="{text_fg}" opacity="0.78"/>'
    body += f'<path d="{d2}" fill="{text_fg}"/>'
    width = tx + word_w
    if tagline:
        tsize = 12.5
        trk = (word_w - text_width("GUIDING YOUR GROWTH", "inter-500", tsize)) / (len("GUIDING YOUR GROWTH") - 1) / tsize
        trk = min(trk, 0.32)
        d3, _ = text_path("GUIDING YOUR GROWTH", "inter-500", tsize, tx + 1, base + 24, trk)
        body += f'<path d="{d3}" fill="{tag_fg}"/>'
    W = width + 6
    if bg:
        p = 40
        return svg(W + 2 * p, H + 2 * p,
                   f'<rect width="{W + 2*p:.0f}" height="{H + 2*p:.0f}" fill="{bg}"/>'
                   f'<g transform="translate({p},{p})">{body}</g>')
    return svg(W, H, body)

def stacked(markfn, fg, accent, text_fg, tag_fg, bg=None):
    W = 360
    body = f'<g transform="translate({W/2 - 60},0) scale(1.2)">{markfn(fg, accent)}</g>'
    gap = 12
    w1 = text_width("SEO", "sg-500", 44); w2 = text_width("Northstar", "sg-700", 44)
    x0 = (W - (w1 + gap + w2)) / 2
    d1, _ = text_path("SEO", "sg-500", 44, x0, 172)
    d2, _ = text_path("Northstar", "sg-700", 44, x0 + w1 + gap, 172)
    body += f'<path d="{d1}" fill="{text_fg}" opacity="0.78"/><path d="{d2}" fill="{text_fg}"/>'
    t = "GUIDING YOUR GROWTH"; ts = 13; trk = 0.3
    tw = text_width(t, "inter-500", ts, trk)
    d3, _ = text_path(t, "inter-500", ts, (W - tw) / 2, 200, trk)
    body += f'<path d="{d3}" fill="{tag_fg}"/>'
    H = 212
    if bg:
        p = 36
        return svg(W + 2*p, H + 2*p, f'<rect width="{W+2*p}" height="{H+2*p}" fill="{bg}"/>'
                   f'<g transform="translate({p},{p})">{body}</g>')
    return svg(W, H, body)

if __name__ == "__main__":
    for key, (label, fn) in MARKS.items():
        files = {
            "icon":            icon(fn, NAVY, GOLD),
            "icon-reverse":    icon(fn, OFF, GOLD),
            "app-icon":        icon(fn, OFF, GOLD, bg=NAVY, pad=18, rounded=True),
            "mono-navy":       icon(fn, NAVY, NAVY),
            "horizontal":      horizontal(fn, NAVY, GOLD, NAVY, "#4A5568"),
            "horizontal-dark": horizontal(fn, OFF, GOLD, OFF, GOLD, bg=NAVY),
            "horizontal-light":horizontal(fn, NAVY, GOLD, NAVY, "#4A5568", bg=OFF),
            "stacked-dark":    stacked(fn, OFF, GOLD, OFF, GOLD, bg=NAVY),
            "stacked-light":   stacked(fn, NAVY, GOLD, NAVY, "#4A5568", bg=OFF),
        }
        for k, v in files.items():
            open(f"{OUT}/{key}-{k}.svg", "w").write(v)
    print("ok")
