"""Round 3 — constructed on a grid. Every size and gap derives from one unit:
u = cap height of the wordmark. Marks are symmetric, upright, and centred on
their construction geometry. Tagline is justified to the wordmark's width."""
import math, os
from gen import text_path, text_width, NAVY, GOLD, OFF

OUT = "out3"; os.makedirs(OUT, exist_ok=True)
SLATE = "#4A5568"

def poly(pts):
    return "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z"

def star(cx, cy, R, r):
    """Upright, fully symmetric 4-point star: tip radius R, inner radius r."""
    k = r / math.sqrt(2)
    return poly([(cx, cy - R), (cx + k, cy - k), (cx + R, cy), (cx + k, cy + k),
                 (cx, cy + R), (cx - k, cy + k), (cx - R, cy), (cx - k, cy - k)])

# ---------------------------------------------------------------- marks
# Each returns (svg_body, width, height) drawn from (0,0).

def pin_mark(fg, accent):
    """Head circle radius 1 (scaled to 50). Tip 1.9r below centre.
    Star centred exactly on the circle centre; star radius 0.58r,
    inner radius 0.30 of star radius (one ratio, reused everywhere)."""
    R = 50; cx, cy = R, R; tip = cy + 1.9 * R
    a = math.acos(R / (tip - cy)); tx, ty = R * math.sin(a), R * math.cos(a)
    body = (f'<path d="M{cx},{tip:.3f} L{cx - tx:.3f},{cy + ty:.3f} '
            f'A{R},{R} 0 1 1 {cx + tx:.3f},{cy + ty:.3f} Z" fill="{fg}"/>'
            f'<path d="{star(cx, cy, 0.58 * R, 0.58 * R * 0.30)}" fill="{accent}"/>')
    return body, 2 * R, tip

def rank_mark(fg, accent, muted):
    """3 rows on a modular grid: row height h, gap h/2 (constant rhythm).
    Star occupies a square cell h×h... scaled 1.5h so its optical size
    matches the bars; bars share one corner radius (h/2)."""
    h = 20; g = 10; W = 100
    s = 1.5 * h                      # star cell
    y1 = 0; y2 = s + g; y3 = y2 + h + g
    bar_x = s + g
    body = (f'<path d="{star(s/2, s/2, s/2, s/2*0.30)}" fill="{accent}"/>'
            f'<rect x="{bar_x}" y="{(s-h)/2}" width="{W-bar_x}" height="{h}" rx="{h/2}" fill="{fg}"/>'
            f'<rect x="0" y="{y2}" width="{W*0.80}" height="{h}" rx="{h/2}" fill="{muted}"/>'
            f'<rect x="0" y="{y3}" width="{W*0.60}" height="{h}" rx="{h/2}" fill="{muted}"/>')
    return body, W, y3 + h

def ascent_mark(fg, accent):
    """N on a 5-column grid: stem width = 1 column (w). Right stem rises one
    module above the left; star radius = w, centred on right stem axis, gap
    above stem = w/2."""
    w = 18; H = 100; step = 18
    xL, xR = 0, 4 * w                 # stems at col 0 and col 4  -> width 5w
    topL = 50                         # left stem top (half height)
    topR = topL - step                # right stem one module higher
    sy = topR - w / 2 - w             # star centre: gap w/2 above stem
    body = (f'<path d="M{xL},{H} L{xL},{topL} L{xL+w},{topL} L{xL+w},{H} Z" fill="{fg}"/>'
            f'<path d="M{xL},{topL} L{xL+w},{topL} L{xR+w},{H} L{xR},{H} Z" fill="{fg}"/>'
            f'<path d="M{xR},{H} L{xR},{topR} L{xR+w},{topR} L{xR+w},{H} Z" fill="{fg}"/>'
            f'<path d="{star(xR + w/2, sy, w, w*0.30)}" fill="{accent}"/>')
    top = sy - w
    # shift so the drawing starts at y=0
    return f'<g transform="translate(0,{-top:.3f})">{body}</g>', 5 * w, H - top

# ---------------------------------------------------------------- lockup system

CAP_SG = 0.700      # Space Grotesk cap height / em
CAP_IN = 1490/2048  # Inter cap height / em

def lockup(mark, word_fg, tag_fg, bg=None, pad_u=1.0):
    S = 48; u = CAP_SG * S                 # u = cap height
    tag_cap = 0.36 * u; T = tag_cap / CAP_IN
    gap_text = 0.55 * u                     # baseline -> tagline cap top
    block_h = u + gap_text + tag_cap        # cap top -> tagline baseline
    body, mw, mh = mark
    over = 0.03 * block_h                   # optical overshoot (2–4%)
    mark_h = block_h + 2 * over
    sc = mark_h / mh; mark_w = mw * sc
    gap_mark = 0.75 * u                     # mark -> wordmark
    tx = mark_w + gap_mark
    base1 = over + u                        # wordmark baseline
    w_seo = text_width("SEO", "sg-400", S); sp = 0.28 * S
    d1, _ = text_path("SEO", "sg-400", S, tx, base1)
    d2, w_ns = text_path("Northstar", "sg-700", S, tx + w_seo + sp, base1)
    word_w = w_seo + sp + w_ns
    t = "GUIDING YOUR GROWTH"
    raw = text_width(t, "inter-500", T)
    trk = (word_w - raw) / (len(t) - 1) / T     # justify exactly to wordmark
    d3, _ = text_path(t, "inter-500", T, tx, base1 + gap_text + tag_cap, trk)
    W = tx + word_w; H = mark_h
    p = pad_u * u                            # clear space = 1u
    inner = (f'<g transform="scale({sc:.5f})">{body}</g>'
             f'<path d="{d1}" fill="{word_fg}"/><path d="{d2}" fill="{word_fg}"/>'
             f'<path d="{d3}" fill="{tag_fg}"/>')
    Wt, Ht = W + 2 * p, H + 2 * p
    rect = f'<rect width="{Wt:.2f}" height="{Ht:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wt:.2f} {Ht:.2f}" '
            f'width="{Wt:.0f}" height="{Ht:.0f}">{rect}<g transform="translate({p:.2f},{p:.2f})">{inner}</g></svg>\n')

def stacked(mark, word_fg, tag_fg, bg):
    S = 48; u = CAP_SG * S; tag_cap = 0.36 * u; T = tag_cap / CAP_IN
    body, mw, mh = mark
    mark_h = 2.6 * u; sc = mark_h / mh; mark_w = mw * sc
    w_seo = text_width("SEO", "sg-400", S); sp = 0.28 * S
    w_ns = text_width("Northstar", "sg-700", S); word_w = w_seo + sp + w_ns
    W = word_w; base1 = mark_h + 0.9 * u + u
    d1, _ = text_path("SEO", "sg-400", S, 0, base1)
    d2, _ = text_path("Northstar", "sg-700", S, w_seo + sp, base1)
    t = "GUIDING YOUR GROWTH"; trk = (word_w - text_width(t, "inter-500", T)) / (len(t) - 1) / T
    tb = base1 + 0.55 * u + tag_cap
    d3, _ = text_path(t, "inter-500", T, 0, tb, trk)
    p = 1.2 * u; Wt, Ht = W + 2 * p, tb + 2 * p
    inner = (f'<g transform="translate({(W - mark_w)/2:.2f},0) scale({sc:.5f})">{body}</g>'
             f'<path d="{d1}" fill="{word_fg}"/><path d="{d2}" fill="{word_fg}"/><path d="{d3}" fill="{tag_fg}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wt:.2f} {Ht:.2f}" width="{Wt:.0f}" height="{Ht:.0f}">'
            f'<rect width="{Wt:.2f}" height="{Ht:.2f}" fill="{bg}"/><g transform="translate({p:.2f},{p:.2f})">{inner}</g></svg>\n')

def tile(mark, bg, fill=0.62):
    """App/favicon tile: mark's larger side = 62% of tile, centred on its
    bounding box (pin: optically nudged up so the head sits centred)."""
    body, mw, mh = mark; S = 100
    sc = fill * S / max(mw, mh); w, h = mw * sc, mh * sc
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
            f'<rect width="{S}" height="{S}" rx="22" fill="{bg}"/>'
            f'<g transform="translate({(S-w)/2:.2f},{(S-h)/2:.2f}) scale({sc:.5f})">{body}</g></svg>\n')

def construction(mark_name):
    """Construction drawing of the pin: circle, centre axes, star radii, tip."""
    R = 50; cx = cy = R; tip = cy + 1.9 * R
    body, mw, mh = pin_mark("#0F1B2D", GOLD)
    g = "#D14D72"
    guides = (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{g}" stroke-width="0.6" stroke-dasharray="2 2"/>'
              f'<circle cx="{cx}" cy="{cy}" r="{0.58*R}" fill="none" stroke="{g}" stroke-width="0.6" stroke-dasharray="2 2"/>'
              f'<line x1="{cx}" y1="-12" x2="{cx}" y2="{tip+8}" stroke="{g}" stroke-width="0.6"/>'
              f'<line x1="-12" y1="{cy}" x2="{2*R+12}" y2="{cy}" stroke="{g}" stroke-width="0.6"/>'
              f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="{g}"/>')
    pad = 20
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {2*R+2*pad} {tip+2*pad}" width="{(2*R+2*pad)*3}" height="{(tip+2*pad)*3}">'
            f'<rect x="{-pad}" y="{-pad}" width="{2*R+2*pad}" height="{tip+2*pad}" fill="#F6F4EF"/>'
            f'<g opacity="0.9">{body}</g>{guides}</svg>\n')

if __name__ == "__main__":
    # extra weight instance
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    if not os.path.exists("fonts/sg-400.ttf"):
        pass
    M = {
        "1-pin":    (lambda d: pin_mark(OFF if d else NAVY, GOLD), lambda: pin_mark(NAVY, OFF)),
        "2-rank":   (lambda d: rank_mark(OFF if d else NAVY, GOLD, "#5B6B84" if d else "#9AA6B8"),
                     lambda: rank_mark(NAVY, OFF, "#8A6A1E")),
        "3-ascent": (lambda d: ascent_mark(OFF if d else NAVY, GOLD), lambda: ascent_mark(NAVY, OFF)),
    }
    for k, (fn, gold_fn) in M.items():
        open(f"{OUT}/{k}-hl.svg", "w").write(lockup(fn(False), NAVY, SLATE, OFF))
        open(f"{OUT}/{k}-hd.svg", "w").write(lockup(fn(True), OFF, GOLD, NAVY))
        open(f"{OUT}/{k}-sl.svg", "w").write(stacked(fn(False), NAVY, SLATE, OFF))
        open(f"{OUT}/{k}-tn.svg", "w").write(tile(fn(True), NAVY))
        open(f"{OUT}/{k}-tg.svg", "w").write(tile(gold_fn(), GOLD))
    open(f"{OUT}/1-pin-construction.svg", "w").write(construction("pin"))
    print("ok")
