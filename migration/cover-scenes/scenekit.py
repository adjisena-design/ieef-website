"""Scene kit for IEEF policy-brief covers: painterly stipple style, motifs for energy, economy and finance.
Every scene keeps the top ~46% as calm sky for the title; motifs live in the lower half.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 2                       # supersampling
W, H = 840 * S, 1188 * S

def hx(h):
    if isinstance(h, tuple): return h[:3]
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

class Scene:
    def __init__(self, seed, sky_top, sky_bot):
        self.rnd = random.Random(seed); np.random.seed(seed)
        top, bot = np.array(hx(sky_top), float), np.array(hx(sky_bot), float)
        t = np.linspace(0, 1, H)[:, None] ** .9
        self.img = Image.fromarray(np.repeat((top * (1 - t) + bot * t)[:, None, :], W, 1).astype(np.uint8))
        self.d = ImageDraw.Draw(self.img, 'RGBA')

    # ---------------------------------------------------------------- texture
    def stipple(self, mask, dark, light, density=1.0, size=(3, 7), light_dir=(-.5, -.8), alpha=230):
        """Fill a mask with painterly dabs: colour shifts from dark to light with the light direction."""
        bb = mask.getbbox()
        if not bb: return
        x0, y0, x1, y1 = bb
        layer = Image.new('RGBA', (x1 - x0, y1 - y0), dark + (255,))
        ld = ImageDraw.Draw(layer, 'RGBA')
        n = int((x1 - x0) * (y1 - y0) / (size[1] * S) ** 2 * 2.2 * density)
        dark_a, light_a = np.array(dark), np.array(light)
        for _ in range(n):
            x = self.rnd.uniform(0, x1 - x0); y = self.rnd.uniform(0, y1 - y0)
            u = (x / max(1, x1 - x0)) - .5; v = (y / max(1, y1 - y0)) - .5
            f = .5 + (u * light_dir[0] + v * light_dir[1]) * .9 + self.rnd.gauss(0, .18)
            f = min(1, max(0, f))
            c = (dark_a + (light_a - dark_a) * f + np.random.normal(0, 6, 3)).clip(0, 255).astype(int)
            r = self.rnd.uniform(*size) * S
            ld.ellipse([x - r, y - r * .8, x + r, y + r * .8], fill=tuple(c) + (alpha,))
        self.img.paste(layer, (x0, y0), mask.crop(bb))

    def shape(self, draw_fn, dark, light, **kw):
        m = Image.new('L', (W, H), 0); draw_fn(ImageDraw.Draw(m)); self.stipple(m, hx(dark), hx(light), **kw)
        return m

    def flat(self, draw_fn, color, alpha=255):
        m = Image.new('L', (W, H), 0); draw_fn(ImageDraw.Draw(m))
        c = Image.new('RGBA', (W, H), hx(color) + (alpha,)); self.img.paste(c, (0, 0), m)

    # ---------------------------------------------------------------- sky
    def clouds(self, n=7, y=(0.06, 0.40), color=(255, 250, 240), a=22):
        for _ in range(n):
            cy = self.rnd.uniform(*y) * H; cx = self.rnd.uniform(-.1, .8) * W; L = self.rnd.uniform(.25, .55) * W
            for _ in range(36):
                yy = cy + self.rnd.gauss(0, 4 * S); x0 = cx + self.rnd.uniform(0, L * .3)
                self.d.line([(x0, yy), (x0 + self.rnd.uniform(.3, 1) * L, yy)], fill=color + (a,), width=2 * S)

    def sun(self, x, y, r=34, color='#f2a24e', crescent=False, glow=True):
        X, Y, R = x * W, y * H, r * S
        if glow:
            for rr, a in [(R * 3, 14), (R * 1.9, 22)]:
                self.d.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=hx(color) + (a,))
        self.d.ellipse([X - R, Y - R, X + R, Y + R], fill=hx(color) + (255,))
        if crescent:   # cut a crescent with the sky colour sampled beside it
            sky = self.img.getpixel((int(min(W - 1, X + R * 2.5)), int(Y)))
            self.d.ellipse([X - R * .55, Y - R * 1.05, X + R * 1.45, Y + R * .95], fill=sky + (255,))

    # ---------------------------------------------------------------- land
    def hills(self, ridge, base_y, dark, light, density=1.0, size=(4, 9)):
        pts = [(x, ridge(x / W) * H) for x in range(0, W + 8 * S, 8 * S)]
        def fn(d): d.polygon(pts + [(W, base_y * H), (0, base_y * H)], fill=255)
        # scalloped canopy edge: bumps along the ridge
        m = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(m); fn(dd)
        r = 22 * S
        for x in range(-r, W + r, int(r * 1.3)):
            y = ridge(min(1, max(0, x / W))) * H
            rr = r * self.rnd.uniform(.8, 1.25)
            dd.ellipse([x - rr, y - rr * .9, x + rr, y + rr * .9], fill=255)
        self.stipple(m, hx(dark), hx(light), density=density, size=size)

    def ground(self, y0, y1, dark, light, size=(3, 7)):
        self.shape(lambda d: d.rectangle([0, y0 * H, W, y1 * H], fill=255), dark, light, size=size, light_dir=(0, -1))

    def water(self, y0, top, bot, reflect=True, ripple='#eaf0f6'):
        Y = int(y0 * H)
        if reflect:
            above = self.img.crop((0, max(0, 2 * Y - H), W, Y)).transpose(Image.FLIP_TOP_BOTTOM)
            a = np.asarray(above).astype(float)
            for yy in range(a.shape[0]):
                a[yy] = np.roll(a[yy], int(math.sin(yy * .06 / S) * (2 + yy / a.shape[0] * 9) * S), axis=0)
        else:
            a = np.zeros((H - Y, W, 3))
        t = np.linspace(0, 1, H - Y)[:, None, None]
        water = np.array(hx(top)) * (1 - t) + np.array(hx(bot)) * t
        out = np.zeros((H - Y, W, 3))
        out[:a.shape[0]] = a[:H - Y]
        out = out * (.5 if reflect else 0) + water * (.5 if reflect else 1)
        self.img.paste(Image.fromarray(out.clip(0, 255).astype(np.uint8)), (0, Y))
        self.d = ImageDraw.Draw(self.img, 'RGBA')
        for _ in range(int(700 * W / 1680)):
            y = Y + (self.rnd.random() ** .8) * (H - Y); x = self.rnd.uniform(0, W)
            L = self.rnd.uniform(10, 80) * S * (.4 + (y - Y) / (H - Y))
            self.d.line([(x, y), (x + L, y)], fill=hx(ripple) + (self.rnd.randint(25, 70),), width=int(self.rnd.uniform(1, 2.2) * S))

    def shore(self, y, color='#c9d672'):
        for x in range(0, W, 2 * S):
            gh = self.rnd.uniform(3, 10) * S
            self.d.line([(x, y * H), (x + self.rnd.uniform(-2, 2) * S, y * H - gh)], fill=hx(color) + (220,), width=2 * S)

    # ---------------------------------------------------------------- energy motifs
    def turbine(self, x, base, h, color='#f2f4f5', ang=None):
        X, B, Hh = x * W, base * H, h * H
        c = hx(color) + (245,)
        self.d.polygon([(X - 2.6 * S, B), (X + 2.6 * S, B), (X + 1.2 * S, B - Hh), (X - 1.2 * S, B - Hh)], fill=c)
        a0 = self.rnd.uniform(0, 120) if ang is None else ang
        for k in range(3):
            a = math.radians(a0 + 120 * k); L = Hh * .48
            tip = (X + math.cos(a) * L, B - Hh + math.sin(a) * L)
            side = (math.cos(a + math.pi / 2) * 3.4 * S, math.sin(a + math.pi / 2) * 3.4 * S)
            self.d.polygon([(X, B - Hh), (X + side[0] + math.cos(a) * L * .25, B - Hh + side[1] + math.sin(a) * L * .25), tip], fill=c)
        self.d.ellipse([X - 4 * S, B - Hh - 4 * S, X + 4 * S, B - Hh + 4 * S], fill=c)

    def solar_rows(self, y0, y1, x0=0.0, x1=1.0, rows=6, panel='#27466e', frame='#d9e2ea', tilt=.45):
        for i in range(rows):
            t = i / max(1, rows - 1)
            y = (y0 + (y1 - y0) * t) * H
            h = (10 + 22 * t) * S
            inset = (1 - t) * .08 * W
            X0, X1 = x0 * W + inset, x1 * W - inset
            pts = [(X0, y), (X1, y), (X1 + h * tilt, y + h), (X0 + h * tilt, y + h)]
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
            self.stipple(m, hx(panel), mix(hx(panel), (150, 190, 230), .55), size=(1.5, 3.5), light_dir=(.3, -.9))
            n = int((X1 - X0) / (26 * S * (.6 + t)))
            for k in range(n + 1):
                xx = X0 + (X1 - X0) * k / max(1, n)
                self.d.line([(xx, y), (xx + h * tilt, y + h)], fill=hx(frame) + (150,), width=max(1, S))
            self.d.line([(X0, y), (X1, y)], fill=hx(frame) + (220,), width=S)
            for k in range(0, n + 1, 3):   # legs
                xx = X0 + (X1 - X0) * k / max(1, n) + h * tilt
                self.d.line([(xx, y + h), (xx, y + h + 5 * S * (.5 + t))], fill=(70, 80, 90, 200), width=S)

    def tower(self, x, base, h, color='#4a5560'):
        X, B, Hh = x * W, base * H, h * H; w = Hh * .22; c = hx(color) + (235,)
        lw = max(2, int(1.8 * S))
        self.d.line([(X - w / 2, B), (X - w * .1, B - Hh)], fill=c, width=lw * 2)
        self.d.line([(X + w / 2, B), (X + w * .1, B - Hh)], fill=c, width=lw * 2)
        for k in range(6):
            y1 = B - Hh * k / 6; y2 = B - Hh * (k + 1) / 6
            xa = w / 2 - (w * .4) * k / 6; xb = w / 2 - (w * .4) * (k + 1) / 6
            self.d.line([(X - xa, y1), (X + xb, y2)], fill=c, width=lw)
            self.d.line([(X + xa, y1), (X - xb, y2)], fill=c, width=lw)
        for frac, arm in [(.78, .7), (.92, .5)]:
            y = B - Hh * frac
            self.d.line([(X - w * arm, y), (X + w * arm, y)], fill=c, width=lw * 2)
        return [(X - w * .7, B - Hh * .78), (X + w * .7, B - Hh * .78), (X - w * .5, B - Hh * .92), (X + w * .5, B - Hh * .92)]

    def wires(self, a, b, sag=18, color=(60, 70, 80, 170)):
        for k in range(min(len(a), len(b))):
            (x1, y1), (x2, y2) = a[k], b[k]
            pts = [(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t + math.sin(math.pi * t) * sag * S) for t in np.linspace(0, 1, 30)]
            self.d.line(pts, fill=color, width=max(1, S))

    def pole(self, x, base, h, color='#5b4a3c'):
        X, B, Hh = x * W, base * H, h * H
        self.d.line([(X, B), (X, B - Hh)], fill=hx(color) + (240,), width=3 * S)
        self.d.line([(X - 10 * S, B - Hh * .9), (X + 10 * S, B - Hh * .9)], fill=hx(color) + (240,), width=2 * S)
        return [(X - 9 * S, B - Hh * .9), (X + 9 * S, B - Hh * .9)]

    def dam_waterfall(self, x0, x1, top, bottom, wall='#9aa5a8', water='#e8f1f6'):
        X0, X1, T, B = x0 * W, x1 * W, top * H, bottom * H
        self.shape(lambda d: d.polygon([(X0, T), (X1, T), (X1 + 20 * S, B), (X0 - 20 * S, B)], fill=255), '#7d888c', '#c3cbcd', size=(2, 5), light_dir=(-.8, -.3))
        n = 5
        for k in range(n):   # spillway streams
            cx = X0 + (X1 - X0) * (k + .5) / n; w = (X1 - X0) / n * .55
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rectangle([cx - w / 2, T + 6 * S, cx + w / 2, B], fill=255)
            self.stipple(m, (190, 214, 228), hx(water), size=(1.5, 4), light_dir=(0, -1), density=1.4)
        for _ in range(60):  # mist
            x = self.rnd.uniform(X0 - 30 * S, X1 + 30 * S); y = B + self.rnd.uniform(-10, 18) * S; r = self.rnd.uniform(8, 22) * S
            self.d.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(255, 255, 255, 30))

    def waterfall(self, x, top, bottom, width, rock='#5f6b5a'):
        X, T, B, Wd = x * W, top * H, bottom * H, width * W
        self.shape(lambda d: d.polygon([(X - Wd * 1.7, B), (X - Wd * 1.2, T + (B - T) * .2), (X - Wd * .8, T - 6 * S), (X + Wd * .9, T - 4 * S), (X + Wd * 1.3, T + (B - T) * .25), (X + Wd * 1.8, B)], fill=255), '#3e4a40', rock, size=(3, 7))
        m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
        # several falling strands with ragged edges instead of one block
        for k in range(5):
            cx = X + (k - 2) * Wd * .26 + self.rnd.uniform(-1, 1) * Wd * .05
            pts_l = [(cx - Wd * .16 + math.sin(t * 9 + k) * Wd * .04, T + (B - T) * t) for t in np.linspace(0, 1, 18)]
            pts_r = [(cx + Wd * .16 + math.sin(t * 7 + k * 2) * Wd * .04 + t * Wd * .08, T + (B - T) * t) for t in np.linspace(1, 0, 18)]
            md.polygon(pts_l + pts_r, fill=255)
        self.stipple(m, (196, 220, 232), (252, 253, 254), size=(1.2, 3), light_dir=(0, -1), density=1.8)
        for _ in range(70):
            x2 = X + self.rnd.gauss(0, Wd * .7); y = B + self.rnd.uniform(-14, 14) * S; r = self.rnd.uniform(8, 20) * S
            self.d.ellipse([x2 - r, y - r * .6, x2 + r, y + r * .6], fill=(255, 255, 255, 34))

    # ---------------------------------------------------------------- built environment
    def building(self, x0, x1, top, base, body, light, windows='#f6e3b0', win_rate=.35, roof=None):
        X0, X1, T, B = x0 * W, x1 * W, top * H, base * H
        self.shape(lambda d: d.rectangle([X0, T, X1, B], fill=255), body, light, size=(1.5, 3.5), light_dir=(-.8, -.2))
        cw, ch = 7 * S, 9 * S
        cols = max(1, int((X1 - X0 - 6 * S) / (cw * 1.9))); rows = max(1, int((B - T - 8 * S) / (ch * 1.8)))
        for i in range(cols):
            for j in range(rows):
                wx = X0 + 5 * S + i * (X1 - X0 - 10 * S) / cols; wy = T + 7 * S + j * (B - T - 12 * S) / rows
                lit = self.rnd.random() < win_rate
                col = hx(windows) + (230,) if lit else mix(hx(body), (255, 255, 255), .25) + (150,)
                self.d.rectangle([wx, wy, wx + cw * .8, wy + ch * .7], fill=col)
        if roof == 'antenna':
            self.d.line([((X0 + X1) / 2, T), ((X0 + X1) / 2, T - 26 * S)], fill=hx(body) + (255,), width=2 * S)
        if roof == 'spire':
            self.d.polygon([(X0 + (X1 - X0) * .3, T), (X1 - (X1 - X0) * .3, T), ((X0 + X1) / 2, T - (X1 - X0) * .9)], fill=hx(body) + (255,))

    def skyline(self, base, spec, palette, win_rate=.3):
        for (x0, x1, top, roof) in spec:
            k = self.rnd.randrange(len(palette)); body, light = palette[k]
            self.building(x0, x1, top, base, body, light, win_rate=win_rate, roof=roof)

    def tiered_roof(self, x, base, w, h, body='#e9e4d8', roof='#4d5b67'):
        """A tiered-roof civic landmark (generic, not a copy of any specific building)."""
        X, B, Wd, Hh = x * W, base * H, w * W, h * H
        self.shape(lambda d: d.rectangle([X - Wd / 2, B - Hh * .45, X + Wd / 2, B], fill=255), '#cfc8b8', body, size=(1.5, 3.5))
        for k in range(Wd and 7):
            cx = X - Wd / 2 + Wd * (k + .5) / 7
            self.d.rectangle([cx - 4 * S, B - Hh * .4, cx + 4 * S, B - Hh * .08], fill=(120, 110, 95, 200))
        for i, (ww, yy) in enumerate([(1.15, .45), (.6, .62), (.35, .76)]):
            self.shape(lambda d, ww=ww, yy=yy: d.polygon([(X - Wd * ww / 2, B - Hh * yy), (X + Wd * ww / 2, B - Hh * yy),
                                                         (X + Wd * ww * .3, B - Hh * (yy + .12)), (X - Wd * ww * .3, B - Hh * (yy + .12))], fill=255),
                       roof, mix(hx(roof), (200, 210, 220), .35) and '#7a8996', size=(1.5, 3))
        self.d.line([(X, B - Hh * .88), (X, B - Hh)], fill=hx(roof) + (255,), width=2 * S)

    def house(self, x, base, w, wall='#efe6d3', roof='#b65b3a'):
        X, B, Wd = x * W, base * H, w * W; Hh = Wd * .55
        self.shape(lambda d: d.rectangle([X - Wd / 2, B - Hh, X + Wd / 2, B], fill=255), '#d9ccb4', wall, size=(1.2, 3))
        self.shape(lambda d: d.polygon([(X - Wd * .62, B - Hh), (X + Wd * .62, B - Hh), (X, B - Hh - Wd * .45)], fill=255), roof, '#d98a63', size=(1.2, 3))
        self.d.rectangle([X - Wd * .1, B - Hh * .55, X + Wd * .1, B], fill=(110, 80, 60, 230))
        self.d.rectangle([X + Wd * .2, B - Hh * .7, X + Wd * .38, B - Hh * .4], fill=(246, 227, 176, 230))

    def road(self, y_top, y_bot, x_top=(.46, .54), x_bot=(.1, .9), color='#5c6066', line='#f2efe6'):
        pts = [(x_top[0] * W, y_top * H), (x_top[1] * W, y_top * H), (x_bot[1] * W, y_bot * H), (x_bot[0] * W, y_bot * H)]
        self.shape(lambda d: d.polygon(pts, fill=255), color, '#868b91', size=(1.5, 3.5), light_dir=(0, -1))
        for k in range(8):
            t0 = (k / 8) ** 1.6; t1 = ((k + .45) / 8) ** 1.6
            xm0 = (x_top[0] + x_top[1]) / 2 * W; xm1 = (x_bot[0] + x_bot[1]) / 2 * W
            ya = y_top * H + (y_bot - y_top) * H * t0; yb = y_top * H + (y_bot - y_top) * H * t1
            wa = 1 + 5 * t0; wb = 1 + 5 * t1
            xa = xm0 + (xm1 - xm0) * t0; xb = xm0 + (xm1 - xm0) * t1
            self.d.polygon([(xa - wa * S / 2, ya), (xa + wa * S / 2, ya), (xb + wb * S / 2, yb), (xb - wb * S / 2, yb)], fill=hx(line) + (220,))

    def car(self, x, base, w, body='#e9eef2', glass='#2d3e52', ev=True):
        X, B, Wd = x * W, base * H, w * W; Hh = Wd * .32
        self.shape(lambda d: d.rounded_rectangle([X - Wd / 2, B - Hh, X + Wd / 2, B - Hh * .25], radius=int(Hh * .3), fill=255), mix(hx(body), (0, 0, 0), .2), body, size=(1, 2.4))
        self.flat(lambda d: d.polygon([(X - Wd * .3, B - Hh), (X + Wd * .22, B - Hh), (X + Wd * .1, B - Hh * 1.55), (X - Wd * .2, B - Hh * 1.55)], fill=255), body)
        self.flat(lambda d: d.polygon([(X - Wd * .25, B - Hh * 1.02), (X + Wd * .18, B - Hh * 1.02), (X + Wd * .08, B - Hh * 1.45), (X - Wd * .17, B - Hh * 1.45)], fill=255), glass)
        for wx in (X - Wd * .3, X + Wd * .3):
            r = Hh * .3; self.d.ellipse([wx - r, B - r * 2, wx + r, B], fill=(35, 38, 42, 255)); self.d.ellipse([wx - r * .45, B - r * 1.45, wx + r * .45, B - r * .55], fill=(150, 155, 160, 255))
        if ev:  # small bolt badge
            bx, by = X + Wd * .05, B - Hh * .62; s = Hh * .18
            self.d.polygon([(bx, by - s), (bx - s * .6, by + s * .1), (bx - s * .05, by + s * .1), (bx - s * .2, by + s), (bx + s * .6, by - s * .15), (bx + s * .05, by - s * .15)], fill=(24, 144, 128, 255))

    def charger(self, x, base, h, body='#f4f6f7', accent='#189080'):
        X, B, Hh = x * W, base * H, h * H; Wd = Hh * .38
        self.shape(lambda d: d.rounded_rectangle([X - Wd / 2, B - Hh, X + Wd / 2, B], radius=int(Wd * .2), fill=255), '#c9d1d6', body, size=(1, 2.4))
        self.d.rectangle([X - Wd * .32, B - Hh * .85, X + Wd * .32, B - Hh * .55], fill=hx(accent) + (255,))
        self.d.line([(X + Wd / 2, B - Hh * .5), (X + Wd * 1.1, B - Hh * .2), (X + Wd * 1.4, B - Hh * .05)], fill=(40, 45, 50, 230), width=2 * S)

    def ship(self, x, y, w, hull='#7c2f2a', boxes=('#c0603a', '#2f6f8f', '#e0b34a', '#4b8a5f', '#8a4b6f')):
        X, Y, Wd = x * W, y * H, w * W; Hh = Wd * .12
        self.shape(lambda d: d.polygon([(X - Wd / 2, Y - Hh), (X + Wd / 2 + Hh, Y - Hh), (X + Wd / 2, Y), (X - Wd / 2 + Hh * .6, Y)], fill=255), '#4a1f1c', hull, size=(1.2, 3))
        bw, bh = Wd / 14, Hh * .6
        for row in range(3):
            for k in range(11 - row):
                bx = X - Wd * .42 + k * bw + row * bw * .5
                self.d.rectangle([bx, Y - Hh - bh * (row + 1), bx + bw * .92, Y - Hh - bh * row - 1], fill=hx(self.rnd.choice(boxes)) + (255,))
        self.shape(lambda d: d.rectangle([X + Wd * .36, Y - Hh - bh * 4.5, X + Wd * .46, Y - Hh], fill=255), '#d9dde0', '#f4f6f7', size=(1, 2))

    def crane(self, x, base, h, color='#d9733a'):
        X, B, Hh = x * W, base * H, h * H; c = hx(color) + (245,); lw = 2 * S
        self.d.line([(X - Hh * .12, B), (X - Hh * .05, B - Hh * .7)], fill=c, width=lw * 2)
        self.d.line([(X + Hh * .12, B), (X + Hh * .05, B - Hh * .7)], fill=c, width=lw * 2)
        self.d.line([(X - Hh * .55, B - Hh * .72), (X + Hh * .35, B - Hh * .72)], fill=c, width=lw * 2)
        self.d.line([(X - Hh * .05, B - Hh * .72), (X - Hh * .05, B - Hh), (X - Hh * .55, B - Hh * .72)], fill=c, width=lw)
        self.d.line([(X - Hh * .4, B - Hh * .72), (X - Hh * .4, B - Hh * .45)], fill=(60, 60, 60, 220), width=S)

    def containers(self, x0, x1, base, rows=3, colors=('#c0603a', '#2f6f8f', '#e0b34a', '#4b8a5f')):
        bw, bh = 34 * S, 14 * S; X0, X1, B = x0 * W, x1 * W, base * H
        for r in range(rows):
            x = X0
            while x + bw <= X1:
                self.d.rectangle([x, B - bh * (r + 1), x + bw - 2 * S, B - bh * r - 2 * S], fill=hx(self.rnd.choice(colors)) + (255,))
                for k in range(1, 5):
                    xx = x + (bw - 2 * S) * k / 5; self.d.line([(xx, B - bh * (r + 1)), (xx, B - bh * r - 2 * S)], fill=(0, 0, 0, 40), width=S)
                x += bw

    def school(self, x, base, w, wall='#f1ead9', roof='#a2452f'):
        X, B, Wd = x * W, base * H, w * W; Hh = Wd * .26
        self.shape(lambda d: d.rectangle([X - Wd / 2, B - Hh, X + Wd / 2, B], fill=255), '#d8ccb3', wall, size=(1.2, 3))
        self.shape(lambda d: d.polygon([(X - Wd * .56, B - Hh), (X + Wd * .56, B - Hh), (X + Wd * .44, B - Hh - Wd * .14), (X - Wd * .44, B - Hh - Wd * .14)], fill=255), roof, '#cf7a5a', size=(1.2, 3))
        for k in range(8):
            wx = X - Wd * .44 + k * Wd * .11
            self.d.rectangle([wx, B - Hh * .78, wx + Wd * .06, B - Hh * .38], fill=(120, 160, 190, 230))
        self.d.rectangle([X - Wd * .05, B - Hh * .5, X + Wd * .05, B], fill=(110, 80, 60, 240))
        fx = X + Wd * .62; self.d.line([(fx, B), (fx, B - Hh * 2.6)], fill=(90, 90, 90, 255), width=2 * S)
        self.d.rectangle([fx, B - Hh * 2.6, fx + Wd * .16, B - Hh * 2.33], fill=(206, 45, 45, 255))
        self.d.rectangle([fx, B - Hh * 2.33, fx + Wd * .16, B - Hh * 2.06], fill=(250, 250, 250, 255))

    def rice_terraces(self, y0, y1, n=7, dark='#5d8a3c', light='#cfe08a'):
        for i in range(n):
            t = i / n; ya = (y0 + (y1 - y0) * t) * H; yb = (y0 + (y1 - y0) * (t + 1 / n)) * H
            amp = (6 + 10 * t) * S; ph = self.rnd.uniform(0, 6)
            top = [(x, ya + math.sin(x / W * 5 + ph) * amp) for x in range(0, W + 8 * S, 8 * S)]
            bot = [(x, yb + math.sin(x / W * 5 + ph + .6) * amp) for x in range(W, -8 * S, -8 * S)]
            self.shape(lambda d, p=top + bot: d.polygon(p, fill=255), dark, light, size=(2, 4.5), light_dir=(0, -1))
            self.d.line(top, fill=(240, 236, 200, 120), width=S)

    def chart_bars(self, x0, x1, base, heights, color='#ffffff', a=60):
        n = len(heights); bw = (x1 - x0) * W / n
        for k, h in enumerate(heights):
            X = x0 * W + k * bw
            self.d.rectangle([X + bw * .15, base * H - h * H, X + bw * .85, base * H], fill=hx(color) + (a,))

    # ---------------------------------------------------------------- finish
    def finish(self, path, grain=9):
        a = np.asarray(self.img).astype(float)
        a += np.random.normal(0, grain, a.shape[:2])[..., None] + np.random.normal(0, 4, a.shape)
        Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((W // S, H // S), Image.LANCZOS).save(path, quality=88)
