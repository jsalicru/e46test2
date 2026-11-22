#!/usr/bin/env python3
"""gen_e46.py - writes the E46 M3 cluster theme's layout (Cluster Themes "e46test2", theme "e46m3").

    python3 tools/gen_e46.py apps/cluster_themes/hud/layouts/e46test2.json

Drawn after the reference render design/e46m3-reference.png (1983 x 793): the E46 M3's cluster with a 0 .. 180 MPH
speedometer (its inner ring 20 .. 300 km/h, the /M badge, MPH), a 0 .. 9 rev counter (a yellow pre-warning band and a
red zone from 7500 rpm), the oil temperature gauge at its foot (120 .. 300 F), fuel and coolant gauges either side and
the orange LCD between the big dials (range, trip, outside temperature). Every measurement below is in the render's
pixels; T() and L() carry them to the cluster's 1920 x 720 at one scale (the render is a little taller than the
cluster, so it is scaled to fit the height and centred).

The same e36dash / e36econ / e36needles widgets as the E36 theme (tools/gen_e36.py, shared/hud.js), with the E46's
additions in the shader: chrome rings ("chrome"), shouldered flat cuts ("cutK"), a yellow zone colour, a black top
lamp window and the oil needle's hub. One face whatever the units and redline settings: the render's MPH face (its
speedometer reads mph, the oil gauge F); the LCD's units follow the units setting.

Angles are degrees clockwise from 12 o'clock round the needle's pivot. Fonts: tools/bake_e46_fonts.py.
Edit this file, not the JSON.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_e36 import W, H, font, ink, digit_ink  # noqa: E402

# BMW's own items in its bottom row that must stay uncovered (x0, x1; the dash's pieces skip them), or BMW draws black
# boxes over the theme. On the G80 M3 (car photos, Nov 22 2026) the drive mode (MDM) from 1214, then the gear number,
# the letter and the shift programme's three lines, together about 1380 .. 1510; the electric range's slot as on the E36.
HOLES = [(1214, 1525), (1680, 1880)]

# the render -> the cluster
S = 0.943
OX, OY = 25.0, -1.0
T = lambda x, y: (round(OX + S * x, 1), round(OY + S * y, 1))
L = lambda v: round(S * v, 2)

TOP = 652                      # the dash layer's foot: BMW's bottom row below it is drawn in pieces round its holes
STRIP_Y = 607                  # the strips (the render's blank boxes either side of the LCD), down past the screen
STRIPS = [[72, STRIP_Y, 608, H - STRIP_Y + 20], [1206, STRIP_Y, 690, H - STRIP_Y + 20], [0, 0, 0, 0]]
STRIP_R = 12
CHROME = 8.0                   # the rings, target px
GAP = 3

# --- the dials (render px): centre, the dial face's radius, the flat cut, the pivot -----------------------------------
SPD = {'c': (657.4, 347.9), 'r': 290, 'cut': 607}
TACH = {'c': (1313.3, 350.0), 'r': 290, 'cut': 607}
# the warm-up lamps: all lit below WARM[0] F oil, one by one out as it climbs, all out at WARM[1]; WARM[2] lamps
WARM = (100, 160, 6)

# each dial's foot: (the flat's half width, the shoulders' slope, mode): the big dials cut flat with sloped shoulders
# (mode 1); the small ones are plain circles cut flat just above their foot, no shoulders (their chrome ring, traced off
# the render: a circle r 163.5 round (180.5, 476), flat at y 620)
BIG_FOOT = (196, 0.72, 1)
SMALL_FOOT = (0, 0, 0)
FUEL = {'c': (189.6, 470.0), 'r': 155, 'cut': 609, 'pivot': (189.6, 560.0)}
COOL = {'c': (1793.5, 470.0), 'r': 155, 'cut': 609, 'pivot': (1793.5, 560.0)}


def mph_ang(v):
    return -133.0 + 264.0 * v / 180.0


def kmh_ang(v):
    return mph_ang(v * 0.621371)


def rpm_ang(k):
    """k in thousands"""
    return -117.5 + 235.0 * k / 9.0


# [dial, first angle, last angle, count, outer radius, length, width] (render px)
TICKS = [
    [1, mph_ang(0), mph_ang(180), 19, 279, 34, 10],          # 0 .. 180 MPH every 10
    [1, mph_ang(5), mph_ang(175), 18, 265, 7.5, 7.5],         # the dots between
    [1, kmh_ang(20), kmh_ang(300), 15, 178, 12, 4],           # the inner km/h ring, every 20
    [2, rpm_ang(0), rpm_ang(9), 10, 279, 34, 10],             # 0 .. 9 thousand
    [2, rpm_ang(0.5), rpm_ang(8.5), 9, 279, 20, 5],           # the halves
    [0, -23, 23, 3, 172, 22, 6.5],                            # fuel: 1/4 1/2 3/4 (round the low pivot, near the rim)
    [3, -17, 17, 3, 192, 20, 6.5],                            # coolant
]
# [dial, from angle, to angle, inner radius, outer radius, colour(, stripes)]
ZONES = [
    # the E46 M3's lamps round the rev counter's rim, one in each 500 rpm step from 4000: yellow to 7000 (the warm-up
    # lamps: hud.js puts them out one by one from the lowest as the oil warms, WARM), orange to 7500, red to 9000 (always lit)
    [2, rpm_ang(4.0), rpm_ang(7.0), 256, 272, 'yellow', 6],
    [2, rpm_ang(7.0), rpm_ang(7.5), 256, 272, 'orange', 1],
    [2, rpm_ang(7.5), rpm_ang(9.0), 256, 272, 'red', 3],
    [3, -42, -31, 168, 200, 'blue'],
    [3, 30, 41, 168, 200, 'red'],
]

# The print, measured off the render (tools/measure_e46.py would redo it: the peach ink's boxes, render px): every
# figure, label and icon is placed by its ink's centre where the render has it, and the fonts are fitted to the
# render's ink sizes (tools/bake_e46_fonts.py).
MPH_AT = {0: (501.0, 497.0), 20: (456.5, 414.0), 40: (446.5, 309.0), 60: (497.5, 210.0), 80: (587.5, 143.0),
          100: (708.5, 138.0), 120: (805.0, 197.0), 140: (865.5, 295.0), 160: (863.0, 396.0), 180: (813.0, 497.0)}
RPM_AT = {0: (1117.0, 450.0), 1: (1086.5, 362.0), 2: (1117.5, 268.0), 3: (1173.5, 195.5), 4: (1262.0, 145.5),
          5: (1370.0, 146.0), 6: (1454.5, 194.0), 7: (1516.0, 274.0), 8: (1540.5, 362.0), 9: (1517.5, 454.0)}
KM_R = 137          # the inner km/h figures' ink centres from the pivot (the render's, 130 .. 142); on the true scale
FIGURES = ([('fs_%d' % v, str(v), 'e4_big') + MPH_AT[v] for v in range(0, 181, 20)]
           + [('ft_%d' % k, str(k), 'e4_rpm') + RPM_AT[k] for k in range(10)]
           + [('fk_%d' % v, str(v), 'e4_km', SPD['c'][0] + KM_R * math.sin(math.radians(kmh_ang(v))),
               SPD['c'][1] - KM_R * math.cos(math.radians(kmh_ang(v)))) for v in range(20, 301, 20)])
TEXTS = [
    ('km/h', 'e4_sm', 665.0, 450.5), ('MPH', 'e4_mph', 662.0, 555.5),
    ('1/min', 'e4_lab', 1315.0, 218.0), ('x1000', 'e4_lab', 1314.0, 250.5),
    ('0', 'e4_gl', 78.5, 428.0), ('1/2', 'e4_gl', 192.5, 364.0), ('1/1', 'e4_gl', 288.5, 429.0),
    ('120', 'e4_oil', 1205.5, 509.5), ('210', 'e4_oil', 1320.5, 483.5), ('300', 'e4_oil', 1432.5, 514.0),
    ('°F', 'e4_degf', 1383.5, 564.5),
]
# icons by their ink: (name, ink centre x, y, ink height or width ('h' / 'w'), render px); ICON_INK: where each icon's
# ink lies in its square (shared/icons.js, measured: x0, x1, y0, y1 as fractions)
ICONS = [('fuel', 200.5, 455.5, 45, 'h'), ('e36cool', 1793.5, 446.0, 52, 'h'), ('e46oil', 1319.0, 530.5, 60, 'w')]
ICON_INK = {'fuel': (0.080, 0.797, 0.220, 0.938), 'e36cool': (0.140, 0.858, 0.040, 0.978), 'e46oil': (0.035, 0.963, 0.247, 0.715)}
LOGO = ('e36m', 660, 503, 96, 34)

# the oil gauge at the rev counter's foot: upright, 120 .. 300 F, its pivot on the flat
OIL_PIV = (1320.0, 575.0)
OIL_ANG = lambda f: -63.0 + 126.0 * (f - 120) / 180.0
# (F, width, inner and outer end): the end ticks short and out past their figures, as the render has them
OIL_TICKS = [(120, 4, 156, 170), (165, 5, 118, 137), (210, 6, 118, 137), (255, 5, 118, 137), (300, 4, 156, 170)]
OIL_LEN, OIL_HUB = 132, 36

# windows: the LCD, the top lamp, (none): x, y, w, h, radius, render px
WINDOWS = [(740, 632, 500, 130, 8), (872, 22, 233, 76, 8), (0, 0, 0, 0, 0)]

# the face: a dark housing under a wide arch through (0, 240), (991, 8), (1983, 240)
FACE = {'box': (-30, -10, 2013, 800), 'radius': 60, 'arch': (991, 2240.6, 2232.6), 'bezel': 8}


def tick(g):
    return [g[0], round(g[1], 2), round(g[2], 2), g[3], L(g[4]), L(g[5]), L(g[6])]


def zone(z):
    return [z[0], round(z[1], 2), round(z[2], 2), L(z[3]), L(z[4]), z[5], z[6] if len(z) > 6 else 0]


def text_at(wid, text, fname, cx, cy, color='mark', align='center'):
    """A text widget whose ink is centred on (cx, cy), target px."""
    f = font(fname)
    hw, hh, dx, dy = ink(text, fname)
    w = sum(f['glyphs'][c]['advance'] for c in text) + 4
    h = f['cellHeight']
    x, y = cx - dx, cy - dy
    return {'id': wid, 'type': 'text', 'class': 'content', 'z': 5, 'x': round(x - w / 2), 'y': round(y - h / 2),
            'w': w, 'h': h, 'text': text, 'font': fname, 'color': color, 'align': align}


def layout():
    dials, needles = [], []
    spec = [  # (dial, signal, pivot, needle length, width, hub, tail, map, rest)
        (FUEL, 'fuel', FUEL['pivot'], 168, 10, 46, 0, [(0, -40), (1, 40)], -46),
        (SPD, 'speed', SPD['c'], 262, 9, 45, 0, [(0, mph_ang(0)), (180, mph_ang(180)), (200, mph_ang(180) + 4)], mph_ang(0) - 3),
        (TACH, 'rpm', TACH['c'], 262, 9, 45, 0, [(0, rpm_ang(0)), (9000, rpm_ang(9)), (9600, rpm_ang(9) + 4)], rpm_ang(0) - 3),
        (COOL, 'coolant', COOL['pivot'], 168, 10, 46, 0,
         [(40, -47), (50, -36.5), (80, -12), (85, 0), (105, 0), (115, 18), (120, 35.5), (130, 45)], -47),
    ]
    for d, sig, piv, nl, nw, hub, tail, mp, rest in spec:
        cut = T(0, d['cut'])[1] if d.get('cut') else 0
        ft = SMALL_FOOT if d in (FUEL, COOL) else BIG_FOOT
        dials.append({'c': list(T(*d['c'])), 'r': L(d['r']), 'cut': cut, 'pivot': list(T(*piv)),
                      'foot': [L(ft[0]), ft[1], ft[2]]})
        needles.append({'signal': sig, 'pivot': list(T(*piv)), 'hub': L(hub), 'tail': L(tail), 'needle': [L(nl), L(nw)],
                        'map': [[v, round(a, 2)] for v, a in mp], 'rest': round(rest, 2)})

    dash = {
        'id': 'dash', 'type': 'e36dash', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': W, 'h': TOP, 'mph': True,
        'face': {'box': list(T(*FACE['box'][:2])) + list(T(*FACE['box'][2:])), 'radius': L(FACE['radius']),
                 'arch': list(T(*FACE['arch'][:2])) + [L(FACE['arch'][2])], 'bezel': L(FACE['bezel'])},
        'dials': dials,
        'ticks': [tick(g) for g in TICKS],
        'zones': [zone(z) for z in ZONES],
        'windows': [list(T(x, y)) + [L(w), L(h), L(r)] if w else [0, 0, 0, 0, 0] for x, y, w, h, r in WINDOWS],
        'strips': STRIPS, 'stripR': STRIP_R,
        'chrome': CHROME, 'pill': True, 'warm': list(WARM),
    }

    # the oil gauge: its ticks (target px) and the needle's scale
    tach_t = [dial for dial in dials][2]
    cx, cy, r, cut = tach_t['c'][0], tach_t['c'][1], tach_t['r'], tach_t['cut']
    px, py = T(*OIL_PIV)
    eticks, emap = [], []
    for f, wd, ri, ro in OIL_TICKS:
        a = math.radians(OIL_ANG(f))
        u = (math.sin(a), -math.cos(a))
        x0, y0 = px + u[0] * L(ro), py + u[1] * L(ro)
        x1, y1 = px + u[0] * L(ri), py + u[1] * L(ri)
        eticks.append([round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1), L(wd)])
        emap.append([f, round(OIL_ANG(f), 2)])
    emap = [[100, round(OIL_ANG(120) - 8, 2)]] + emap + [[320, round(OIL_ANG(300) + 6, 2)]]
    # the window's top line above the rev counter's rim, square: it never shows (the render's gauge has no window),
    # and the oil needle is kept to the dial. The layer itself only spans the ticks.
    top = round(cy - r - 20, 1)
    cham = [-1e5, 0, 1e5, 0]
    xs = [t[0] for t in eticks] + [t[2] for t in eticks]
    ys = [t[1] for t in eticks] + [t[3] for t in eticks]
    ex0, ex1 = math.floor(min(xs)) - 8, math.ceil(max(xs)) + 8
    ey0, ey1 = math.floor(min(ys)) - 8, math.ceil(max(ys)) + 8
    econ = {'id': 'econ', 'type': 'e36econ', 'class': 'content', 'z': 0, 'x': ex0, 'y': ey0, 'w': ex1 - ex0,
            'h': ey1 - ey0, 'mph': True, 'lineColor': 'dial', 'tach': [cx, cy, r, cut],
            'econ': {'top': top, 'cham': cham, 'ticks': eticks}}

    reach = [(n['pivot'], max(n['needle'][0], n['tail'], n['hub']) + n['needle'][1] + 3) for n in needles]
    nx0 = max(0, math.floor(min(p[0] - k for p, k in reach)))
    nx1 = min(W, math.ceil(max(p[0] + k for p, k in reach)))
    ny0 = max(0, math.floor(min(p[1] - k for p, k in reach)))
    ndl = {'id': 'needles', 'type': 'e36needles', 'class': 'content', 'z': 6, 'x': nx0, 'y': ny0, 'w': nx1 - nx0,
           'h': TOP - ny0, 'mph': True, 'dials': needles,
           'econ': {'signal': 'oil', 'pivot': [px, py], 'top': top, 'len': L(OIL_LEN), 'width': L(7), 'cham': cham,
                    'tach': [cx, cy, r, cut], 'map': emap, 'rest': emap[0][1], 'hub': L(OIL_HUB)}}

    # the print
    texts = []
    for wid, t, fn, x, y in FIGURES:
        texts.append(text_at(wid, t, fn, *T(x, y)))
    for i, (t, fn, x, y) in enumerate(TEXTS):
        texts.append(text_at('tx_%d' % i, t, fn, *T(x, y)))
    icons = []
    for name, x, y, size, by in ICONS:
        x0, x1, y0, y1 = ICON_INK[name]
        box = L(size) / ((x1 - x0) if by == 'w' else (y1 - y0))      # the square whose ink is that big
        ix, iy = T(x, y)
        bx, by_ = ix - ((x0 + x1) / 2 - 0.5) * box, iy - ((y0 + y1) / 2 - 0.5) * box
        icons.append({'id': 'ic_' + name, 'type': 'icon', 'icon': name, 'class': 'content', 'z': 5,
                      'x': round(bx - box / 2), 'y': round(by_ - box / 2), 'w': round(box), 'h': round(box), 'color': 'mark'})
    name, x, y, lw, lh = LOGO
    cx_, cy_ = T(x, y)
    icons.append({'id': 'ic_' + name, 'type': 'icon', 'icon': name, 'class': 'content', 'z': 5,
                  'x': round(cx_ - L(lw) / 2), 'y': round(cy_ - L(lh) / 2), 'w': round(L(lw)), 'h': round(L(lh))})

    # the LCD: the range where the render has the odometer (the car sends no odometer), its unit, the trip; under them
    # the outside temperature ({{ambient}}: "+72")
    lx, ly = T(740, 632)

    def lcd(n, text, fname, x0, x1, ycen, align, toggle=None):
        f = font(fname)
        wdg = {'id': 'lcd_' + n, 'type': 'text', 'class': 'content', 'z': 5, 'x': round(lx + L(x0)),
               'y': round(ly + L(ycen) - f['cellHeight'] / 2), 'w': round(L(x1 - x0)), 'h': f['cellHeight'],
               'text': text, 'font': fname, 'color': 'lcd', 'align': align}
        if toggle:
            wdg['toggle'] = toggle
        return wdg
    top_d, bot_d = digit_ink('e4_lcd')
    mid = (top_d + bot_d) / 2 - font('e4_lcd')['cellHeight'] / 2     # the digits' ink middle off the cell's
    r1, r2 = 31 - mid / S, 93 - mid / S
    lcds = [
        lcd('range', '{{range}}', 'e4_lcd', 22, 212, r1, 'right'),
        lcd('mi', 'miles', 'e4_sm', 232, 312, r1 - 4, 'left', 'units=us'),
        lcd('km', 'km', 'e4_sm', 232, 312, r1 - 4, 'left', 'units=metric'),
        lcd('trip', '{{trip}}', 'e4_lcd', 318, 482, r1, 'right'),
        lcd('out', '{{ambient}}', 'e4_lcd', 110, 314, r2, 'right'),
        lcd('outu', '{{u:temp}}', 'e4_sm', 336, 400, r2 - 4, 'left'),
    ]

    # BMW's bottom row: the same picture in pieces round the holes where BMW's own items show
    edges = [0] + [x for h in HOLES for x in h] + [W]
    pieces = [dict(dash, id='dash_' + 'abcd'[i], x=x0, y=TOP, w=x1 - x0, h=H - TOP, stripRow='abcd'[i])
              for i, (x0, x1) in enumerate(zip(edges[::2], edges[1::2]))]
    return {
        'schemaVersion': 2,
        'name': 'E46 M3',
        'packWaste': 3,
        'theme': 'e46m3',
        '_about': 'E46 M3 cluster, generated by tools/gen_e46.py (edit that and regenerate) after the reference render '
                  'design/e46m3-reference.png: a 0 .. 180 MPH speedometer with a 20 .. 300 km/h inner ring, the /M badge, '
                  'a 0 .. 9 rev counter with its yellow pre-warning band and red zone from 7500, the oil temperature gauge '
                  '(120 .. 300 F) at its foot, fuel and coolant gauges, the orange LCD between the dials. Peach print, '
                  'orange needles, chrome rings (theme e46m3). One e36dash shader draws the face, dials, ticks, zones and '
                  'windows; the figures are text widgets; the needles their own layer on top. Widget reference: '
                  'shared/hud.js header.',
        'widgets': [dash, econ] + pieces + texts + icons + lcds + [ndl],
    }


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'apps/cluster_themes/hud/layouts/e46test2.json'
    with open(out, 'w') as f:
        json.dump(layout(), f, indent=2)
        f.write('\n')
    print('wrote', out)
