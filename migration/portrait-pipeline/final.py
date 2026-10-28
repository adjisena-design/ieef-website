import json, numpy as np
from PIL import Image, ImageFilter, ImageChops
from rembg import remove, new_session
from clean import clean
SRC = '/tmp/claude-0/-home-claude/41787a81-572f-50b0-86a1-f00bbfc220f3/scratchpad/imgs/people/'
W, H = 900, 1125
FACE_H, CX, CY = 330, 450, 480         # common face height and face-centre position
FACES = json.load(open('faces.json'))
bg = Image.open('bg_light.jpg').convert('RGB').crop((0, 0, 900, 1125)).filter(ImageFilter.GaussianBlur(2.5))
logo = Image.open('logo600.png').convert('RGBA'); logo = logo.resize((220, round(logo.height * 220 / logo.width)), Image.LANCZOS)

# where each figure would end, to put one shared fade line above the shortest
def placement(n):
    x, y, w, h = FACES[n][:4]; s = FACE_H / h
    return s, CX - (x + w / 2) * s, CY - (y + h / 2) * s
bottoms = {n: placement(n)[2] + 1200 * placement(n)[0] for n in FACES}
print({k[:12]: round(v) for k, v in bottoms.items()})

sess = new_session('isnet-general-use')
import os
ONLY = os.environ.get('ONLY')
for n in sorted(FACES):
    if ONLY and n != ONLY: continue
    fixed = f'cut_{n.split("-")[0]}_fixed.png'
    if os.path.exists(fixed):          # hand-checked cutout (e.g. watermark touching the figure)
        person = Image.open(fixed).convert('RGBA')
    else:
        remove(Image.open(SRC + n + '.png').convert('RGB'), session=sess).save('cut_' + n + '.png')
        person = clean('cut_' + n + '.png')
    s, ox, oy = placement(n)
    person = person.resize((round(person.width * s), round(person.height * s)), Image.LANCZOS)
    if s > 1.15:   # light sharpening for enlarged originals
        person = person.filter(ImageFilter.UnsharpMask(radius=1.6, percent=int(min(90, (s - 1) * 110)), threshold=2))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(person, (round(ox), round(oy))) if ox >= 0 and oy >= 0 else layer.paste(person, (round(ox), round(oy)), person)
    a = np.asarray(layer).astype(float)
    # figures that end just above the frame edge fade over their last 70px instead of showing a hard cut
    end = int(oy + person.height)
    if end < H + 2:
        ramp = np.clip((end - 4 - np.arange(H)) / 70, 0, 1)[:, None]
        a[..., 3] *= ramp
    layer = Image.fromarray(a.astype(np.uint8))
    alpha = layer.split()[3]
    canvas = bg.copy().convert('RGBA')
    sh = Image.new('RGBA', (W, H), (10, 25, 35, 0)); sh.putalpha(alpha.point(lambda v: int(v * .16)).filter(ImageFilter.GaussianBlur(26)))
    canvas.alpha_composite(sh, (0, 6))
    rgb = Image.blend(layer.convert('RGB'), Image.new('RGB', (W, H), (240, 230, 210)), 0.05)
    edge = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(9))).filter(ImageFilter.GaussianBlur(4))
    rgb = Image.composite(Image.blend(rgb, bg.filter(ImageFilter.GaussianBlur(12)), 0.45), rgb, edge.point(lambda v: int(v * .7)))
    fig = rgb.convert('RGBA'); fig.putalpha(alpha)
    canvas.alpha_composite(fig)
    canvas.alpha_composite(logo, (40, 44))
    canvas.convert('RGB').save(f'final_{n}.jpg', quality=92)
print('done')
