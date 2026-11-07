"""Animated hero: a seamless loop built from the painted scene.
Energy motifs are steady (baseload) sources only, per the Executive Director: a hydro dam with a running spillway
and a geothermal plant with rising steam. No wind turbines or solar (variable renewables).
Motion: steam plumes, spillway water, a breeze swaying the canopy, drifting leaves, a pulsing sun glow, lake shimmer.

Run: python3 hero-animate.py paint      (one-off: repaints the turbine-era stills in SRC into OUT/base_*.jpg)
     python3 hero-animate.py desktop|mobile|dusk   (writes OUT/<kind>_poster.jpg and, except dusk, OUT/hero-<kind>.mp4)
Then copy the posters over src/assets/art/paint_{hero,mobile,dusk}.jpg and the mp4s into public/media/.
"""
import math, sys, os, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import scenekit as sk

FPS, SECONDS = 24, 10
N = FPS * SECONDS
SRC = '/home/claude/ieef'          # copies of the Oct 2026 stills (with turbines)
OUT = '/home/claude/ieef/anim'

# boxes are fractions of the image. turbines: area to erase. plant: (x, ground y, scale). dam: (x0, x1, top, bottom).
# vents: steam sources (x, y). spill: spillway (x0, x1, top, bottom) whose water runs in the loop.
CONF = {
    'desktop': dict(src='paint_hero.jpg', video=(1600, 1000), horizon=0.83, sun=(0.60, 0.20),
                    turbines=(0.83, 0.98, 0.03, 0.27), plant=(0.875, 0.262, 1.3), dam=(0.385, 0.505, 0.69, 0.832)),
    'mobile': dict(src='paint_mobile.jpg', video=(720, 1440), horizon=0.81, sun=(0.80, 0.55),
                   turbines=(0.06, 0.32, 0.49, 0.60), plant=(0.19, 0.588, 1.1), dam=(0.60, 0.80, 0.752, 0.812)),
    'dusk': dict(src='paint_dusk.jpg', turbines=(0.83, 0.97, 0.0, 0.09), plant=None, dam=None, vents=[(0.90, 0.06)]),
}

def kit(img):
    """Point scenekit's painterly stipple at an existing image."""
    sk.W, sk.H = img.size; sk.S = max(1, round(img.size[0] / 1200))
    s = object.__new__(sk.Scene); s.rnd = random.Random(11); np.random.seed(11)
    s.img = img; s.d = ImageDraw.Draw(img, 'RGBA'); return s

def erase_turbines(img, box):
    a = np.asarray(img).copy(); H, W, _ = a.shape
    x0, x1, y0, y1 = int(box[0] * W), int(box[1] * W), int(box[2] * H), int(box[3] * H)
    sub = a[y0:y1, x0:x1].astype(int)
    bg = cv2.medianBlur(np.ascontiguousarray(sub.astype(np.uint8)), 21).astype(int)
    m = (((sub - bg).mean(2) > 14) & (sub.max(2) - sub.min(2) < 60)).astype(np.uint8) * 255   # lighter than surroundings, unsaturated = turbine
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    a[y0:y1, x0:x1] = cv2.inpaint(np.ascontiguousarray(a[y0:y1, x0:x1]), m, 6, cv2.INPAINT_TELEA)
    return Image.fromarray(a)

def plant(s, x, y, k):
    """Small geothermal plant sitting on a far ridge: turbine hall, separator, pipes. Returns steam vents."""
    W, H = s.img.size; u = W / 2400 * k * 1.6
    X, Y = x * W, y * H
    hall = (X - 46 * u, Y - 22 * u, X + 18 * u, Y + 4 * u)
    s.shape(lambda d: d.rectangle(hall, fill=255), '#9aa7ae', '#e6ebec', size=(1, 2.2), light_dir=(-.8, -.4))
    s.d.polygon([(hall[0] - 2 * u, hall[1]), (hall[2] + 2 * u, hall[1]), (hall[2] - 6 * u, hall[1] - 7 * u), (hall[0] + 6 * u, hall[1] - 7 * u)], fill=(122, 134, 142, 255))
    sep = (X + 26 * u, Y - 30 * u, X + 38 * u, Y + 4 * u)
    s.shape(lambda d: d.rounded_rectangle(sep, 5 * u, fill=255), '#a9b4b9', '#eef1f1', size=(1, 2), light_dir=(-.9, -.2))
    for dy in (0, 5 * u):   # pipelines running down the slope
        s.d.line([(hall[0], Y - 2 * u + dy), (X - 90 * u, Y + 22 * u + dy), (X - 150 * u, Y + 30 * u + dy)], fill=(214, 220, 222, 230), width=max(2, int(2.2 * u)))
    return [((X + 32 * u) / W, (Y - 31 * u) / H), ((X - 30 * u) / W, (Y - 30 * u) / H)]

def dam(s, x0, x1, top, bottom):
    """Concrete dam closing a V-shaped valley: wide crest, narrow base, hillsides overlapping both ends."""
    W, H = s.img.size; X0, X1, T, B = x0 * W, x1 * W, top * H, bottom * H; w = X1 - X0
    src = np.asarray(s.img).astype(int)
    crest = lambda t: T - math.sin(math.pi * t) * w * .025
    face = [*[(X0 + w * t, crest(t)) for t in np.linspace(0, 1, 24)], (X1 - w * .2, B), (X0 + w * .2, B)]
    s.shape(lambda d: d.polygon(face, fill=255), '#98a4a8', '#c6cecf', size=(.8, 1.8), light_dir=(-.9, -.2), density=1.5)
    for t in np.linspace(.2, .8, 6):   # block joints
        s.d.line([(X0 + w * t, crest(t) + 6), (X0 + w * (.5 + (t - .5) * .62), B)], fill=(112, 124, 130, 60), width=2)
    s.d.line([(X0 + w * t, crest(t) + 2) for t in np.linspace(0, 1, 24)], fill=(238, 241, 241, 235), width=5)   # crest road
    s.d.line([(X0 + w * t, crest(t) - 3) for t in np.linspace(0, 1, 24)], fill=(90, 100, 106, 150), width=1)   # railing
    sx0, sx1 = X0 + w * .43, X0 + w * .57
    m = Image.new('L', s.img.size, 0); ImageDraw.Draw(m).polygon([(sx0, crest(.43) + 4), (sx1, crest(.57) + 4), (sx1 - w * .01, B), (sx0 + w * .01, B)], fill=255)
    s.stipple(m, (186, 210, 224), (250, 252, 253), size=(.8, 2), light_dir=(0, -1), density=1.8)
    for sign in (-1, 1):   # hillside sloping into the valley, in the colours of the trees beside it
        cx = X0 if sign < 0 else X1
        a, b = sorted((int(cx + sign * w * .15), int(cx + sign * w * .35)))
        ref = src[int(T):int(B), max(0, a):b].reshape(-1, 3)
        dark, light = tuple(np.percentile(ref, 12, 0).astype(int)), tuple(np.percentile(ref, 88, 0).astype(int))
        m = Image.new('L', s.img.size, 0); md = ImageDraw.Draw(m)
        edge = lambda u: (cx - sign * w * (.03 + .2 * u), T - w * .02 + (B - T) * u)   # the slope line, top to bottom
        md.polygon([edge(0), edge(1), (edge(1)[0] + sign * w * .1, B + 4), (edge(0)[0] + sign * w * .1, T)], fill=255)   # narrow band, blends into the canopy behind
        for j in range(18):
            ex, ey = edge(j / 17); r = w * s.rnd.uniform(.035, .06)
            md.ellipse([ex - r, ey - r, ex + r, ey + r], fill=255)
        s.stipple(m, dark, light, size=(2.5, 5.5), density=1.1, light_dir=(-.5, -.8))
    # faint mirrored reflection in the lake
    box = (int(X0 - w * .1), int(T - w * .05), int(X1 + w * .1), int(B))
    refl = s.img.crop(box).transpose(Image.FLIP_TOP_BOTTOM)
    refl = refl.resize((refl.width, int(refl.height * .7)))
    fade = Image.linear_gradient('L').resize(refl.size).point(lambda v: int((255 - v) * .28))
    s.img.paste(refl, (box[0], int(B) + 2), fade)
    return (sx0 / W, sx1 / W, T / H, B / H)

def paint_all():
    for kind, c in CONF.items():
        img = erase_turbines(Image.open(f"{SRC}/{c['src']}").convert('RGB'), c['turbines'])
        s = kit(img); meta = dict(vents=c.get('vents', []), spill=None)
        if c['dam']: meta['spill'] = dam(s, *c['dam'])
        if c['plant']: meta['vents'] = plant(s, *c['plant'])
        img.save(f'{OUT}/base_{kind}.jpg', quality=95)
        np.save(f'{OUT}/meta_{kind}.npy', meta, allow_pickle=True)
        print('painted', kind, meta)

def steam(ov, vents, W, H, t, TS):
    """Puffs leave each vent, grow, thin out and drift left with the breeze. Phases wrap, so the loop is seamless."""
    layer = Image.new('RGBA', ov.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for vi, (vx, vy) in enumerate(vents):
        for p in range(26):
            age = (t * 2 + p / 26 + vi * .37) % 1.0
            U = max(W, H)   # puff size follows the long side so portrait art gets the same soft plumes
            rise = age * .19 * H; r = (.008 + .032 * age) * U
            x = vx * W - age ** 1.4 * .07 * W + math.sin(age * 9 + p) * .004 * W
            y = vy * H - rise
            a = int(210 * (1 - age) ** 1.2 * min(1, age * 8))
            d.ellipse([(x - r) * TS, (y - r * .8) * TS, (x + r) * TS, (y + r * .8) * TS], fill=(214, 222, 228, a // 2))
            d.ellipse([(x - r * .6) * TS, (y - r * .55) * TS, (x + r * .6) * TS, (y + r * .45) * TS], fill=(255, 255, 255, int(a * .7)))
    ov.alpha_composite(layer.filter(ImageFilter.GaussianBlur(max(W, H) * .0022 * TS)))

def main(kind):
    c = CONF[kind]; meta = np.load(f'{OUT}/meta_{kind}.npy', allow_pickle=True).item()
    base = Image.open(f'{OUT}/base_{kind}.jpg').convert('RGB'); W, H = base.size
    if kind == 'dusk':   # a still band, no video: just add the steam
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); steam(ov, meta['vents'], W, H, 0.0, 1)
        img = base.convert('RGBA'); img.alpha_composite(ov); img.convert('RGB').save(f'{OUT}/dusk_poster.jpg', quality=92); return
    os.makedirs(f'{OUT}/{kind}', exist_ok=True)
    b = np.asarray(base).astype(np.float32)
    hy = int(c['horizon'] * H)
    rnd = random.Random(5)

    lum = b.mean(2); green = b[..., 1] - b[..., 2]
    tree = ((lum < 168) | (green > 6)).astype(np.float32); tree[hy - 2:] = 0
    x0, x1, y0, y1 = c['dam']; tree[int(y0 * H) - 10:int(y1 * H), int(x0 * W):int(x1 * W)] = 0   # concrete does not sway
    tree = cv2.GaussianBlur(tree, (0, 0), 6)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    lake = np.zeros((H, W), np.float32); lake[hy + 4:] = 1
    lake_depth = np.clip((ys - hy) / (H - hy), 0, 1)
    sp0, sp1, spt, spb = meta['spill']
    spill = np.zeros((H, W), np.float32)
    spill[int(spt * H):int(spb * H), int((sp0 - .006) * W):int((sp1 + .006) * W)] = 1
    spill = cv2.GaussianBlur(spill, (0, 0), 1.5)

    sx, sy = c['sun'][0] * W, c['sun'][1] * H
    leaves = []
    for i in range(22):
        k = rnd.choice([1, 1, 2])
        leaves.append(dict(k=k, x0=rnd.uniform(0, 1), y0=rnd.uniform(.18, .78), amp=rnd.uniform(.01, .035),
                           wob=rnd.choice([1, 2, 3]), ph=rnd.uniform(0, 6.28), size=rnd.uniform(.0045, .0085) * W,
                           spin=rnd.choice([-2, -1, 1, 2]), col=rnd.choice([(126, 162, 70), (170, 190, 80), (96, 140, 70), (205, 196, 96)])))
    TS = 2

    for f in range(N):
        t = f / N; ph = 2 * math.pi * t
        dx = (2.4 * np.sin(ph * 2 - xs / (W * .06) - ys / (H * .05)) + 1.1 * np.sin(ph * 3 + xs / (W * .11))) * tree * (W / 1600)
        dy = 0.8 * np.cos(ph * 2 - xs / (W * .07)) * tree * (W / 1600)
        dx += lake * (1.3 + 3.0 * lake_depth) * np.sin(ph * 4 + ys / 3.2) * (W / 1600)
        # spillway: texture slides downward (sample from above), 12 cycles per loop keeps it seamless
        dy -= spill * (6 * (W / 1600)) * ((t * 12) % 1.0)
        frame = cv2.remap(b, xs + dx, ys + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = Image.fromarray(frame.clip(0, 255).astype(np.uint8))

        ov = Image.new('RGBA', (W * TS, H * TS), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for rr, a0 in [(0.11, 10), (0.075, 16)]:
            a = int(a0 + a0 * .9 * math.sin(ph))
            R = rr * min(W, H) * TS
            d.ellipse([sx * TS - R, sy * TS - R, sx * TS + R, sy * TS + R], fill=(246, 194, 122, max(0, a)))
        steam(ov, meta['vents'], W, H, t, TS)
        # mist where the spillway meets the lake
        for m in range(9):
            mx = (sp0 + (sp1 - sp0) * (m + .5) / 9) * W; my = spb * H - 2
            r = (.010 + .004 * math.sin(ph * 3 + m * 1.7)) * W
            d.ellipse([(mx - r * 1.4) * TS, (my - r * .6) * TS, (mx + r * 1.4) * TS, (my + r * .5) * TS], fill=(255, 255, 255, 34))
        for L in leaves:
            u = (L['x0'] - t * L['k']) % 1.0
            x = (u * 1.2 - .1) * W
            y = (L['y0'] + L['amp'] * math.sin(ph * L['wob'] + L['ph'])) * H
            rot = L['ph'] + ph * L['spin']
            s = L['size'] * TS
            pts = []
            for k in range(12):
                q = 2 * math.pi * k / 12
                px, py = math.cos(q) * s, math.sin(q) * s * .42 * (0.6 + 0.4 * abs(math.cos(ph * L['wob'] * 2 + L['ph'])))
                pts.append((x * TS + px * math.cos(rot) - py * math.sin(rot), y * TS + px * math.sin(rot) + py * math.cos(rot)))
            d.polygon(pts, fill=L['col'] + (225,))
        ov = ov.resize((W, H), Image.LANCZOS)
        img = img.convert('RGBA'); img.alpha_composite(ov); img = img.convert('RGB')
        if f == 0:
            img.save(f'{OUT}/{kind}_poster.jpg', quality=92)
            if len(sys.argv) > 2: return   # poster-only preview
        img.resize(c['video'], Image.LANCZOS).save(f'{OUT}/{kind}/f{f:04d}.png')
    vw, vh = c['video']
    mp4 = f'{OUT}/hero-{kind}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{OUT}/{kind}/f%04d.png',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '30', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-movflags', '+faststart', '-an', mp4], check=True)
    print(kind, 'frames', N, 'mp4', os.path.getsize(mp4) // 1024, 'KB')

if __name__ == '__main__':
    paint_all() if sys.argv[1] == 'paint' else main(sys.argv[1])
