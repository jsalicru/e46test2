#!/usr/bin/env python3
"""bake_e46_fonts.py - the E46 M3 theme's fonts (layout e46test2.json, tools/gen_e46.py).

    python3 tools/bake_e46_fonts.py

Uses tools/bake_fonts.py's bake() (same atlas format as every other font in apps/cluster_themes/hud/fonts/).
Barlow Semi Condensed Medium for the print (the drawing's DIN-like figures), DSEG7 for the orange LCD. DSEG7 has no
'+', which the outside temperature needs ({{ambient}} reads "+72"): it is made here from the font's own '-' and the
same bar stood upright, so it matches the other segments.
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bake_fonts as bf  # noqa: E402

OUT = os.path.join(HERE, '..', 'apps', 'cluster_themes', 'hud', 'fonts')
SEMI = 'BarlowSemiCondensed-Medium.ttf'
D, U, L = bf.DIGITS, bf.UPPER, bf.LOWER

FONTS = [
    ('e4_big', SEMI, 54, D),                          # the MPH figures and the rev counter's 0 .. 9
    ('e4_km', SEMI, 30, D),                           # the inner km/h ring
    ('e4_lab', SEMI, 31, U + L + D + ' /°'),          # 1/min, x1000, MPH
    ('e4_sm', SEMI, 26, U + L + D + ' /°'),           # km/h, miles, °F
    ('e4_gl', SEMI, 36, D + '/°F'),                   # the small gauges' and the oil gauge's figures
    ('e4_lcd', 'DSEG7Classic-Bold.ttf', 40, D + '-.: '),
]


def add_plus(name):
    """Give a DSEG7 font a '+': its '-' bar, and the same bar turned upright through its middle."""
    path = os.path.join(OUT, name + '.json')
    with open(path) as f:
        fnt = json.load(f)
    aw, ah = fnt['width'], fnt['height']
    alpha = bytearray(base64.b64decode(fnt['alpha']))
    g = fnt['glyphs']['-']
    ink = [(x, y, alpha[(g['y'] + y) * aw + g['x'] + x]) for y in range(g['h']) for x in range(g['w'])
           if alpha[(g['y'] + y) * aw + g['x'] + x] > 0]
    xs, ys = [p[0] for p in ink], [p[1] for p in ink]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = (max(xs) - min(xs)) / 2
    w, h = g['w'], g['h']
    plus = bytearray(w * h)
    for x, y, a in ink:
        plus[y * w + x] = max(plus[y * w + x], a)
        # the same pixel turned a quarter round the bar's middle
        rx, ry = int(round(cx + (y - cy))), int(round(cy + (x - cx)))
        if 0 <= rx < w and 0 <= ry < h and abs(ry - cy) <= half:
            plus[ry * w + rx] = max(plus[ry * w + rx], a)
    # place it after the right-most glyph in the atlas
    x0 = max(c['x'] + c['w'] for c in fnt['glyphs'].values()) + bf.PAD
    if x0 + w > aw:
        raise SystemExit('no room in the atlas for +')
    for y in range(h):
        for x in range(w):
            alpha[(g['y'] + y) * aw + x0 + x] = plus[y * w + x]
    fnt['glyphs']['+'] = dict(g, x=x0)
    fnt['alpha'] = base64.b64encode(bytes(alpha)).decode()
    with open(path, 'w') as f:
        json.dump(fnt, f, separators=(',', ':'))


if __name__ == '__main__':
    for spec in FONTS:
        bf.bake(OUT, *spec)
    add_plus('e4_lcd')
