import numpy as np
from PIL import Image
from scipy import ndimage
def clean(path):
    im = Image.open(path).convert('RGBA'); a = np.asarray(im).copy()
    al = a[..., 3].astype(float)
    solid = ndimage.binary_opening(al > 160, structure=np.ones((3, 3)), iterations=7)   # drops thin slivers left by the old watermark
    lab, n = ndimage.label(solid)
    if n:
        sizes = ndimage.sum(solid, lab, range(1, n + 1))
        keep = lab == (np.argmax(sizes) + 1)
        keep = ndimage.binary_fill_holes(keep)
        near = ndimage.binary_dilation(keep, iterations=3)      # allow soft hair/edge pixels next to the figure
        al = np.where(near, al, 0)
    # pale, non-skin pixels in the top band of the figure are leftovers of the old watermark (heads are hair/scarf/skin)
    rows = np.where((al > 160).any(axis=1))[0]
    if len(rows):
        top, bottom = rows[0], rows[-1]
        band = slice(top, top + int(0.12 * (bottom - top)))
        rgb = a[..., :3].astype(int)
        lum = rgb.mean(axis=2)
        warm = (rgb[..., 0] - rgb[..., 2]) > 22
        pale = (lum > 150) & ~warm
        region = np.zeros_like(pale); region[band] = True
        cand = pale & region & (al > 0)
        outside = ndimage.binary_dilation(al < 24, iterations=2)
        lab, n = ndimage.label(cand)
        kill = np.zeros_like(cand)
        for i in range(1, n + 1):
            comp = lab == i
            if (comp & outside).any():           # only pale patches on the outline, never inside the face
                kill |= comp
        kill = ndimage.binary_dilation(kill, iterations=2) & region & ~(warm & (lum < 235))
        al[kill] = 0
        # re-keep the main body after removal
        lab, n = ndimage.label(al > 160)
        if n > 1:
            sizes = ndimage.sum(al > 160, lab, range(1, n + 1))
            main = ndimage.binary_dilation(lab == (np.argmax(sizes) + 1), iterations=3)
            al = np.where(main, al, 0)
    # anywhere on the outline: small pale, low-saturation patches are watermark leftovers (not white shirts,
    # which sit inside the figure, and not skin, which is warm)
    rgb = a[..., :3].astype(int)
    lum = rgb.mean(axis=2); sat = rgb.max(axis=2) - rgb.min(axis=2)
    warm = (rgb[..., 0] - rgb[..., 2]) > 22
    pale = (lum > 175) & (sat < 45) & ~warm & (al > 0)
    outside = ndimage.binary_dilation(al < 24, iterations=2)
    figure = (al > 160).sum()
    lab, n = ndimage.label(pale)
    for i in range(1, n + 1):
        comp = lab == i
        if (comp & outside).any() and comp.sum() < 0.04 * figure:
            al[ndimage.binary_dilation(comp, iterations=2)] = 0
    lab, n = ndimage.label(al > 160)
    if n > 1:
        sizes = ndimage.sum(al > 160, lab, range(1, n + 1))
        al = np.where(ndimage.binary_dilation(lab == (np.argmax(sizes) + 1), iterations=3), al, 0)
    al[al < 24] = 0
    a[..., 3] = al.astype(np.uint8)
    return Image.fromarray(a)
if __name__ == '__main__':
    import sys
    for p in sys.argv[1:]: clean(p).save(p)
