"""Kerned text → SVG path using HarfBuzz shaping (applies the font's GPOS kerning)."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
_c = {}
def _load(name):
    if name not in _c:
        data = open(f"fonts/{name}.ttf", "rb").read()
        face = hb.Face(data); font = hb.Font(face)
        tt = TTFont(f"fonts/{name}.ttf")
        _c[name] = (font, tt, tt.getGlyphSet(), tt["head"].unitsPerEm)
    return _c[name]
def shaped(s, name, size, x, y, tracking_em=0.0):
    font, tt, gs, upm = _load(name)
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    sc = size / upm; pen = SVGPathPen(gs); cx = 0.0
    order = tt.getGlyphOrder()
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        g = order[info.codepoint]
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x + cx + pos.x_offset * sc, y - pos.y_offset * sc)))
        cx += pos.x_advance * sc + (tracking_em * size if i < n - 1 else 0)
    return pen.getCommands(), cx
