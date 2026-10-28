"""Landscape painted scenes for the four dashboard cards. Run: python3 dash_scenes.py <outdir>"""
import sys, math, os
import scenekit
scenekit.W, scenekit.H = 1200 * scenekit.S, 760 * scenekit.S
from scenekit import Scene, S
W, H = scenekit.W, scenekit.H

def commodity_export(out):   # plantation hills, coal barge port, container ship heading out
    s = Scene(201, '#8fa9c2', '#ebece6'); s.clouds(n=5, y=(.05, .30))
    s.sun(.18, .30, r=22, color='#f2b264')
    s.hills(lambda x: .44 + .06 * math.sin(x * 2.4 + .6), .62, '#5f7f9b', '#a3b8c9', size=(3, 7))
    s.hills(lambda x: .52 - .05 * math.sin(x * 3.1), .64, '#2f6a45', '#9cc06c')
    s.rice_terraces(.54, .64, n=4, dark='#3f7a3a', light='#b7d27a')
    s.water(.63, '#3d6a8f', '#1d3f63')
    s.ship(.30, .80, .40)
    s.flat(lambda d: d.polygon([(W * .56, H * .63), (W, H * .63), (W, H * .745), (W * .60, H * .745)], fill=255), '#8b8f93')
    s.flat(lambda d: d.rectangle([W * .60, H * .74, W, H * .755], fill=255), '#5d6166')
    s.containers(.64, .99, .70, rows=3)
    s.crane(.70, .70, .26); s.crane(.86, .70, .22)
    s.finish(out)

def jabar(out):              # West Java: rice terraces in front, Bandung skyline with tiered-roof landmark
    s = Scene(202, '#9fb8cc', '#efeae0'); s.clouds(n=5, y=(.05, .30))
    s.hills(lambda x: .40 + .07 * math.sin(x * 2.0 + 1.0), .62, '#5b7ea0', '#9bb3c8', size=(3, 7))
    pal = [('#6f8297', '#a9b8c6'), ('#8796a5', '#c4ccd4'), ('#5d708a', '#94a5b8'), ('#9b8f7d', '#cfc4b0')]
    s.skyline(.64, [(.04, .11, .50, None), (.11, .17, .44, 'antenna'), (.62, .70, .47, None), (.70, .77, .41, 'spire'),
                    (.77, .85, .49, None), (.85, .93, .45, 'antenna')], pal, win_rate=.3)
    s.tiered_roof(.40, .66, .26, .22)
    s.ground(.64, 1.0, '#557a4a', '#b8cf7e')
    s.rice_terraces(.70, 1.0, n=6)
    s.finish(out)

def fastra(out):             # project feasibility: solar farm, wind on the ridge, transmission line, rising bars
    s = Scene(203, '#86a8c4', '#e9eeea'); s.clouds(n=5, y=(.05, .30))
    s.sun(.84, .26, r=24, color='#f6c27a')
    s.hills(lambda x: .46 - .05 * math.sin(x * 2.6), .62, '#3f7f80', '#7fb0aa', size=(3, 7))
    for x, h in [(.56, .14), (.66, .16), (.77, .13)]:
        s.turbine(x, .47 - .05 * math.sin(x * 2.6) + .02, h)
    s.ground(.60, 1.0, '#3d6a3e', '#a9c36e')
    s.solar_rows(.66, .92, rows=5, x0=.30, x1=1.05)
    a = s.tower(.12, .98, .46, color='#3a434c'); b = s.tower(.26, .70, .20, color='#3a434c')
    s.wires(a, b, sag=18, color=(45, 52, 60, 200))
    s.finish(out)

def mof(out):                # public finance: dusk office district, ministry-like low building, evening traffic
    s = Scene(204, '#3f5a86', '#f0c9a0'); s.clouds(n=4, y=(.05, .28), color=(255, 226, 200), a=26)
    s.sun(.50, .46, r=30, color='#f39a52')
    pal = [('#2c3f63', '#55709a'), ('#34496f', '#6680a8'), ('#273a5c', '#4e6890'), ('#3d4c6a', '#71809e')]
    s.skyline(.66, [(-.02, .10, .30, 'antenna'), (.10, .19, .38, None), (.19, .27, .26, 'spire'), (.73, .81, .33, None),
                    (.81, .90, .24, 'antenna'), (.90, 1.02, .36, None)], pal, win_rate=.55)
    s.building(.34, .66, .555, .66, '#cdbfa6', '#e6dac4', windows='#f3c978', win_rate=.35)
    s.flat(lambda d: d.polygon([(W * .33, H * .557), (W * .67, H * .557), (W * .50, H * .50)], fill=255), '#8a5a3c')
    for i in range(9):
        x = .36 + i * .035
        s.flat(lambda d, x=x: d.rectangle([W * x, H * .585, W * (x + .008), H * .66], fill=255), '#efe6d2')
    s.ground(.66, 1.0, '#4a4f5c', '#7d8290')
    s.road(.66, 1.0, x_top=(.44, .56), x_bot=(.12, .88))
    s.car(.30, .88, .22, body='#eef2f5', ev=False); s.car(.66, .80, .14, body='#d0e2ea')
    s.finish(out)

SCENES = {'commodity-export': commodity_export, 'jabar': jabar, 'fasilitas-ekstra': fastra, 'mof-performance': mof}

if __name__ == '__main__':
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    for k, fn in SCENES.items():
        fn(f'{outdir}/{k}.jpg'); print('painted', k)
