import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageChops
ART = '/home/claude/ieef-website/src/assets/art/'
W, H = 900, 1200

def cover(img, w, h, fy=0.5):
    s = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))

def bg_forest():
    art = Image.open(ART + 'paint_mobile.jpg').convert('RGB')         # 900x1800 portrait painting
    im = cover(art, W, H, fy=0.42).filter(ImageFilter.GaussianBlur(5))
    return im

def bg_dusk():
    art = Image.open(ART + 'paint_dusk.jpg').convert('RGB')
    im = cover(art, W, H, fy=0.35)
    im = im.filter(ImageFilter.GaussianBlur(5))
    return im

def bg_paper():
    paper = Image.new('RGB', (W, H), (244, 239, 227))
    # soft sky wash at the top
    g = np.linspace(0, 1, H)[:, None]
    sky = (np.array([214, 225, 230]) * (1 - g) + np.array([244, 239, 227]) * g)
    paper = Image.fromarray(np.repeat(sky[:, None, :], W, 1).squeeze().astype(np.uint8))
    art = Image.open(ART + 'paint_mobile.jpg').convert('RGB')
    hills = cover(art, W, int(H * 0.6), fy=0.62)
    mask = Image.new('L', hills.size, 0); d = np.asarray(hills).astype(int)
    # take only the painted hills (drop the sky of the painting): sky pixels are blue-grey and bright
    sky_like = (d[..., 2] > d[..., 1] - 5) & (d.mean(2) > 150)
    m = Image.fromarray(np.where(sky_like, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
    paper.paste(hills, (0, H - hills.height), m)
    d = ImageDraw.Draw(paper)
    d.ellipse([W * 0.68, H * 0.16, W * 0.68 + 120, H * 0.16 + 120], fill=(236, 154, 76))
    return paper.filter(ImageFilter.GaussianBlur(1.2))

def compose(cut_path, bg, grade):
    person = Image.open(cut_path).convert('RGBA')
    person = person.resize((W, round(person.height * W / person.width)), Image.LANCZOS)
    canvas = bg.copy().convert('RGBA')
    # soft contact shadow under the figure
    alpha = person.split()[3]
    # soft ambient shadow behind the figure (no offset, so no dark halo on one side)
    sh = Image.new('RGBA', person.size, (10, 25, 35, 0)); sh.putalpha(alpha.point(lambda v: int(v * .18)).filter(ImageFilter.GaussianBlur(26)))
    canvas.alpha_composite(sh, (0, H - person.height + 6))
    # gentle colour grade so the person sits in the scene's light
    rgb = person.convert('RGB'); tint = Image.new('RGB', person.size, grade)
    rgb = Image.blend(rgb, tint, 0.06)
    # light wrap: background glow bleeding onto the figure's edges
    edge = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(9))).filter(ImageFilter.GaussianBlur(4))
    bgcrop = bg.crop((0, H - person.height, W, H)).filter(ImageFilter.GaussianBlur(12))
    rgb = Image.composite(Image.blend(rgb, bgcrop, 0.45), rgb, edge.point(lambda v: int(v * .7)))
    out = rgb.convert('RGBA'); out.putalpha(alpha)
    canvas.alpha_composite(out, (0, H - person.height))
    return canvas.convert('RGB')

P = '/home/claude/ieef/portraits/'
def soft(name, blur):
    return lambda: Image.open(P + name).convert('RGB').filter(ImageFilter.GaussianBlur(blur))
VARIANTS = {'A_forest': (soft('bg_day.jpg', 3.5), (120, 150, 110)),
            'B_dusk': (soft('bg_dusk.jpg', 3.5), (90, 110, 170)),
            'C_light': (soft('bg_light.jpg', 2.5), (240, 230, 210))}
if __name__ == '__main__':
    import sys
    for n in sys.argv[1:]:
        for v, (fn, grade) in VARIANTS.items():
            compose(f'cut_{n}.png', fn(), grade).save(f'{v}_{n}.jpg', quality=90)
