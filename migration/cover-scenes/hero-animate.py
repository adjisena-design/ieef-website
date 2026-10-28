"""Animated hero: a seamless loop built from the painted scene.
Motion: turbine blades turning, a breeze swaying the canopy, drifting leaves, a pulsing sun glow, lake shimmer.
Run: python3 animate.py desktop|mobile
"""
import math, sys, os, random, subprocess, shutil
import numpy as np, cv2
from PIL import Image, ImageDraw
import importlib.util
spec = importlib.util.spec_from_file_location('paint', '/home/claude/ieef/paint.py'); paint = importlib.util.module_from_spec(spec); spec.loader.exec_module(paint)

FPS, SECONDS = 24, 10
N = FPS * SECONDS
OUT = '/home/claude/ieef/anim'

def hero_ridge(x):
    x = min(1.2, max(0.0, x))
    return 0.75 if x < 0.42 else 0.75 - 0.58 * ((x - 0.42) / 0.58) ** 1.15

CONF = {
    'desktop': dict(size=(2400, 1500), video=(1600, 1000), horizon=0.83, ridge=hero_ridge, sun=(0.60, 0.20),
                    turbines=[(0.86, 0.075), (0.905, 0.075), (0.95, 0.075)], far_offset=0.08,
                    base=lambda: paint.render(2400, 1500, paint.PALETTES['day'], seed=7, horizon=0.83, ridge=hero_ridge,
                                              moon=(0.60, 0.20), boat=(0.16, 0.915), turbines=False)),
    'mobile': dict(size=(900, 1800), video=(720, 1440), horizon=0.81,
                   ridge=lambda x: 0.69 - 0.06 * math.sin(min(1.2, max(0, x)) * math.pi), sun=(0.80, 0.55),
                   turbines=[(0.14, 0.05), (0.24, 0.045)], far_offset=0.08,
                   base=lambda: Image.open('/home/claude/ieef-website/src/assets/art/paint_mobile.jpg').convert('RGB')),
}

def main(kind):
    c = CONF[kind]; W, H = c['size']
    os.makedirs(f'{OUT}/{kind}', exist_ok=True)
    base = c['base']().convert('RGB').resize((W, H))
    b = np.asarray(base).astype(np.float32)
    hy = int(c['horizon'] * H)
    rnd = random.Random(5)

    # canopy mask: everything above the horizon that is not sky (darker or greener than the sky gradient)
    lum = b.mean(2); green = b[..., 1] - b[..., 2]
    tree = ((lum < 168) | (green > 6)).astype(np.float32); tree[hy - 2:] = 0
    tree = cv2.GaussianBlur(tree, (0, 0), 6)
    # sway grows towards canopy tops (where the mask begins from above)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    lake = np.zeros((H, W), np.float32); lake[hy + 4:] = 1
    lake_depth = np.clip((ys - hy) / (H - hy), 0, 1)

    sx, sy = c['sun'][0] * W, c['sun'][1] * H
    leaves = []
    for i in range(22):
        k = rnd.choice([1, 1, 2])                       # crossings per loop (keeps the loop seamless)
        leaves.append(dict(k=k, x0=rnd.uniform(0, 1), y0=rnd.uniform(.18, .78), amp=rnd.uniform(.01, .035),
                           wob=rnd.choice([1, 2, 3]), ph=rnd.uniform(0, 6.28), size=rnd.uniform(.0045, .0085) * W,
                           spin=rnd.choice([-2, -1, 1, 2]), col=rnd.choice([(126, 162, 70), (170, 190, 80), (96, 140, 70), (205, 196, 96)])))
    angles = [rnd.uniform(0, 120) for _ in c['turbines']]
    TS = 2  # supersample overlays

    for f in range(N):
        t = f / N; ph = 2 * math.pi * t
        # breeze: travelling wave, two components with periods that divide the loop
        dx = (2.4 * np.sin(ph * 2 - xs / (W * .06) - ys / (H * .05)) + 1.1 * np.sin(ph * 3 + xs / (W * .11))) * tree * (W / 1600)
        dy = 0.8 * np.cos(ph * 2 - xs / (W * .07)) * tree * (W / 1600)
        # lake shimmer: rows slide gently, stronger towards the viewer
        dx += lake * (1.3 + 3.0 * lake_depth) * np.sin(ph * 4 + ys / 3.2) * (W / 1600)
        frame = cv2.remap(b, xs + dx, ys + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = Image.fromarray(frame.clip(0, 255).astype(np.uint8))

        ov = Image.new('RGBA', (W * TS, H * TS), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        # sun glow pulse
        for rr, a0 in [(0.11, 10), (0.075, 16)]:
            a = int(a0 + a0 * .9 * math.sin(ph))
            R = rr * min(W, H) * TS
            d.ellipse([sx * TS - R, sy * TS - R, sx * TS + R, sy * TS + R], fill=(246, 194, 122, max(0, a)))
        # turbines: blades turn 240 degrees per loop (blades are 120-degree symmetric, so it loops seamlessly)
        for (tx, th), a0 in zip(c['turbines'], angles):
            X = tx * W * TS; B = ((c['ridge'](tx) - c['far_offset']) * H + 6) * TS; Hh = th * H * TS
            col = (233, 238, 240, 240)
            d.polygon([(X - 2.2 * TS, B), (X + 2.2 * TS, B), (X + 1.0 * TS, B - Hh), (X - 1.0 * TS, B - Hh)], fill=col)
            ang = a0 + 240 * t
            for k in range(3):
                a = math.radians(ang + 120 * k); L = Hh * .46
                tip = (X + math.cos(a) * L, B - Hh + math.sin(a) * L)
                n = (math.cos(a + math.pi / 2) * 2.6 * TS, math.sin(a + math.pi / 2) * 2.6 * TS)
                d.polygon([(X, B - Hh), (X + n[0] + math.cos(a) * L * .22, B - Hh + n[1] + math.sin(a) * L * .22), tip], fill=col)
            r = 3.2 * TS; d.ellipse([X - r, B - Hh - r, X + r, B - Hh + r], fill=col)
        # leaves drifting right-to-left on the breeze
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
            img.save(f'{OUT}/{kind}_poster.jpg', quality=90)
        img.resize(c['video'], Image.LANCZOS).save(f'{OUT}/{kind}/f{f:04d}.png')
    vw, vh = c['video']
    mp4 = f'{OUT}/hero-{kind}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{OUT}/{kind}/f%04d.png',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '30', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-movflags', '+faststart', '-an', mp4], check=True)
    print(kind, 'frames', N, 'mp4', os.path.getsize(mp4) // 1024, 'KB')

if __name__ == '__main__':
    main(sys.argv[1])
