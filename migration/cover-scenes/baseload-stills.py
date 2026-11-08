"""One-off (Nov 2026): strip wind turbines and solar panels from the remaining stills and add the geothermal plant
used in the hero, per the Executive Director (baseload sources only). Reuses the painters in hero-animate.py.
Run from this folder: python3 baseload-stills.py  (edits the files in place; run once against the Oct 2026 art)
"""
import importlib.util, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

spec = importlib.util.spec_from_file_location('hero', 'hero-animate.py'); hero = importlib.util.module_from_spec(spec); spec.loader.exec_module(hero)
ART = '../../src/assets/art'

def erase_lines(img, box):
    """Turbines are thin bright strokes: find them with a top-hat (bright minus opened) so leaf dabs and the sun stay.
    Horizontal kernel catches poles and steep blades; vertical kernel catches flat blades, minus long cloud streaks."""
    a = np.asarray(img).copy(); H, W, _ = a.shape
    x0, x1, y0, y1 = int(box[0] * W), int(box[1] * W), int(box[2] * H), int(box[3] * H)
    sub = np.ascontiguousarray(a[y0:y1, x0:x1]); lum = cv2.cvtColor(sub, cv2.COLOR_RGB2GRAY)
    k = max(9, W // 110)
    th = cv2.morphologyEx(lum, cv2.MORPH_TOPHAT, np.ones((1, k), np.uint8)) > 24
    tv = (cv2.morphologyEx(lum, cv2.MORPH_TOPHAT, np.ones((k, 1), np.uint8)) > 24) & ~th
    n, lab, st, _ = cv2.connectedComponentsWithStats(tv.astype(np.uint8))
    clouds = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_WIDTH] > W * .13])
    m = ((th | tv) & ~clouds).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)   # keep long strokes only; leaf dabs are small blobs
    m = np.isin(lab, [i for i in range(1, n) if max(st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]) > 4 * k]).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    a[y0:y1, x0:x1] = cv2.inpaint(sub, m, 4, cv2.INPAINT_TELEA)
    return Image.fromarray(a)

def erase_solar(img, box):
    """Cover the panel rows with the hedge texture directly above them, feathered so no seam shows."""
    W, H = img.size; x0, x1, y0, y1 = int(box[0] * W), int(box[1] * W), int(box[2] * H), int(box[3] * H)
    patch = img.crop((x0, 2 * y0 - y1, x1, y0))
    m = Image.new('L', patch.size, 0); ImageDraw.Draw(m).rounded_rectangle([6, 6, patch.width - 6, patch.height - 6], 14, fill=255)
    img.paste(patch, (x0, y0), m.filter(ImageFilter.GaussianBlur(5)))
    return img

# file, turbine box, solar box, plant (x, ground y, scale)
JOBS = [
    (f'{ART}/ieef-at-work.jpg', (0.63, 0.96, 0.19, 0.50), (0.62, 1.0, 0.545, 0.632), (0.87, 0.432, 2.0)),
    (f'{ART}/poster_energy.jpg', (0.80, 1.0, 0.30, 0.47), None, None),   # sun sits on that ridge: no plant, just clear sky
    ('../../public/og-default.jpg', (0.82, 0.985, 0.0, 0.26), None, (0.885, 0.245, 0.9)),
]

for path, tb, sb, pl in JOBS:
    img = erase_lines(Image.open(path).convert('RGB'), tb)
    if sb: img = erase_solar(img, sb)
    s = hero.kit(img); vents = hero.plant(s, *pl) if pl else []
    W, H = img.size; ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); hero.steam(ov, vents, W, H, 0.0, 1)
    out = img.convert('RGBA'); out.alpha_composite(ov); out.convert('RGB').save(path, quality=92)
    print('done', path)
