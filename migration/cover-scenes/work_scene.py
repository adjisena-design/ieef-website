"""'IEEF at work' painting for the home page arch: campus building with researchers at a data board,
city behind, solar and wind on the hill, a power line linking them. Run: python3 work_scene.py out.jpg"""
import sys, math
import scenekit
scenekit.W, scenekit.H = 1400 * scenekit.S, 1100 * scenekit.S
from scenekit import Scene, S, hx
W, H = scenekit.W, scenekit.H

def person(s, x, base, h, shirt, trousers='#2e3b4e', skin='#c98d63', hair='#2a211c', hijab=None, point=None):
    """Small painted figure: x/base in 0..1, h = height in fractions of H."""
    X, B, Hh = x * W, base * H, h * H
    d = s.d
    leg_w = Hh * .07
    d.rounded_rectangle([X - Hh * .11, B - Hh * .46, X - Hh * .11 + leg_w * 1.4, B], radius=leg_w * .6, fill=hx(trousers) + (255,))
    d.rounded_rectangle([X + Hh * .11 - leg_w * 1.4, B - Hh * .46, X + Hh * .11, B], radius=leg_w * .6, fill=hx(trousers) + (255,))
    d.rounded_rectangle([X - Hh * .17, B - Hh * .80, X + Hh * .17, B - Hh * .40], radius=Hh * .08, fill=hx(shirt) + (255,))
    if point:  # arm pointing towards a board
        ax = X + point * Hh * .42
        d.line([(X + point * Hh * .12, B - Hh * .70), (ax, B - Hh * .86)], fill=hx(shirt) + (255,), width=int(Hh * .07))
        d.ellipse([ax - Hh * .035, B - Hh * .90, ax + Hh * .035, B - Hh * .82], fill=hx(skin) + (255,))
    r = Hh * .11
    cy = B - Hh * .80 - r * .9
    if hijab:
        d.ellipse([X - r * 1.25, cy - r * 1.2, X + r * 1.25, cy + r * 1.35], fill=hx(hijab) + (255,))
        d.ellipse([X - r * .78, cy - r * .7, X + r * .78, cy + r * .85], fill=hx(skin) + (255,))
    else:
        d.ellipse([X - r, cy - r, X + r, cy + r], fill=hx(skin) + (255,))
        d.chord([X - r * 1.05, cy - r * 1.1, X + r * 1.05, cy + r * .6], 180, 360, fill=hx(hair) + (255,))

def board(s, x, base, w, h):
    X0, X1, B, T = (x - w / 2) * W, (x + w / 2) * W, base * H, (base - h) * H
    d = s.d
    d.line([((X0 + X1) / 2 - w * W * .3, B), ((X0 + X1) / 2, T + h * H * .55)], fill=(70, 62, 52, 255), width=5 * S)
    d.line([((X0 + X1) / 2 + w * W * .3, B), ((X0 + X1) / 2, T + h * H * .55)], fill=(70, 62, 52, 255), width=5 * S)
    top = T; bot = T + h * H * .62
    d.rounded_rectangle([X0, top, X1, bot], radius=8 * S, fill=(250, 247, 238, 255), outline=(60, 72, 88, 255), width=3 * S)
    # rising bar chart and trend line (energy x economy x finance)
    bars = [.30, .42, .38, .55, .66, .80]
    bw = (X1 - X0 - 40 * S) / len(bars)
    cols = ['#5898c0', '#189080', '#5898c0', '#189080', '#ec9a4c', '#189080']
    pts = []
    for i, v in enumerate(bars):
        bx = X0 + 20 * S + i * bw
        by = bot - 14 * S - v * (bot - top - 36 * S)
        d.rectangle([bx + bw * .18, by, bx + bw * .82, bot - 14 * S], fill=hx(cols[i]) + (235,))
        pts.append((bx + bw / 2, by - 12 * S))
    d.line(pts, fill=(8, 56, 104, 255), width=4 * S, joint='curve')
    for p in pts: d.ellipse([p[0] - 5 * S, p[1] - 5 * S, p[0] + 5 * S, p[1] + 5 * S], fill=(8, 56, 104, 255))

def campus(s, x0, x1, top, base):
    """Modern campus block: warm stone frame, glass curtain wall, flat canopy roof."""
    X0, X1, T, B = x0 * W, x1 * W, top * H, base * H
    s.shape(lambda d: d.rectangle([X0, T, X1, B], fill=255), '#cdbb9c', '#ede2cc', size=(2, 4), light_dir=(-.8, -.2))
    d = s.d
    gx0, gx1, gy0, gy1 = X0 + (X1 - X0) * .08, X1 - (X1 - X0) * .08, T + (B - T) * .10, B - (B - T) * .22
    cols, rows = 7, 6
    for i in range(cols):
        for j in range(rows):
            px0 = gx0 + i * (gx1 - gx0) / cols; py0 = gy0 + j * (gy1 - gy0) / rows
            shade = (92 + 10 * ((i + j) % 3), 132 + 8 * (j % 2), 160 + 10 * (i % 2), 255)
            d.rectangle([px0 + 3 * S, py0 + 3 * S, px0 + (gx1 - gx0) / cols - 3 * S, py0 + (gy1 - gy0) / rows - 3 * S], fill=shade)
            if (i * 3 + j) % 5 == 0:
                d.rectangle([px0 + 3 * S, py0 + 3 * S, px0 + (gx1 - gx0) / cols - 3 * S, py0 + (gy1 - gy0) / rows * .45], fill=(214, 230, 238, 200))
    # entrance and canopy
    ex = (X0 + X1) / 2
    d.rectangle([ex - (X1 - X0) * .12, B - (B - T) * .18, ex + (X1 - X0) * .12, B], fill=(70, 88, 104, 255))
    d.polygon([(X0 - 16 * S, T), (X1 + 16 * S, T), (X1 - 10 * S, T - 26 * S), (X0 + 10 * S, T - 26 * S)], fill=(77, 91, 103, 255))

def main(out):
    s = Scene(301, '#8fb0c8', '#eef0e8'); s.clouds(n=6, y=(.05, .30))
    s.sun(.60, .17, r=30, color='#f4b468')
    # distant hills and city
    s.hills(lambda x: .42 + .05 * math.sin(x * 2.3 + .5), .62, '#6d8ca8', '#a9bfd0', size=(3, 7))
    pal = [('#6f8297', '#a9b8c6'), ('#8796a5', '#c4ccd4'), ('#5d708a', '#94a5b8')]
    s.skyline(.58, [(.40, .45, .47, 'antenna'), (.45, .50, .43, None), (.50, .55, .49, 'spire'), (.55, .60, .45, None)], pal, win_rate=.3)
    # hill with turbines and solar on the right
    ridge = lambda x: .50 - .10 * max(0, x - .55) / .45
    s.hills(ridge, .66, '#2f6f52', '#9cc47a')
    for x, h in [(.70, .15), (.80, .17), (.91, .15)]:
        s.turbine(x, ridge(x) + .015, h)
    s.solar_rows(.56, .64, rows=3, x0=.60, x1=1.02)
    # campus building (left), modern block with tiered roof canopy
    campus(s, .03, .36, .28, .64)
    # power line from solar hill to the campus
    a = s.tower(.52, .63, .20, color='#3a434c'); b = s.tower(.40, .66, .16, color='#3a434c')
    s.wires(a, b, sag=14, color=(45, 52, 60, 200))
    # plaza in front
    s.ground(.64, 1.0, '#6f9160', '#c6d79a')
    s.shape(lambda d: d.polygon([(0, H * .655), (W * .58, H * .655), (W * .78, H), (0, H)], fill=255), '#c9b996', '#ece2cc', size=(2, 5), light_dir=(0, -1))
    # researchers around the data board (kept above the bottom label band)
    board(s, .32, .755, .17, .19)
    person(s, .19, .755, .13, '#083868', point=1)
    person(s, .45, .75, .125, '#189080', hijab='#5b4a7a')
    person(s, .52, .76, .12, '#ec9a4c', trousers='#3b3b48')
    person(s, .10, .77, .12, '#f2f0ea', trousers='#41506a', hijab='#1f5e7a')
    person(s, .62, .75, .115, '#5898c0')
    s.finish(out)

if __name__ == '__main__':
    main(sys.argv[1])
