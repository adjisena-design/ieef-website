"""Ten cover scenes built from the scene kit. Run: python3 scenes.py <outdir>"""
import sys, math
from scenekit import Scene, W, H, S

def solar(out):          # Islamic finance for renewables: solar farm on terraces, crescent moon
    s = Scene(101, '#7f9fbe', '#e6ebe6'); s.clouds()
    s.sun(.78, .40, r=30, color='#f6d38a', crescent=True)
    s.hills(lambda x: .55 - .05 * math.sin(x * 3.1), .70, '#3e6f86', '#7aa5b8', size=(3, 7))
    s.hills(lambda x: .62 + .03 * math.sin(x * 4 + 1), .78, '#1d5c45', '#8fbf6a')
    s.ground(.74, 1.0, '#2c6b3d', '#b9cf6e')
    s.solar_rows(.69, .86, rows=6)
    s.finish(out)

def school(out):         # Free nutritious meals: school, flag, rice terraces, warm morning
    s = Scene(102, '#d9c4b2', '#f6e3cb'); s.clouds(color=(255, 246, 232))
    s.sun(.84, .55, r=26, color='#f08a3e')
    s.hills(lambda x: .56 + .04 * math.sin(x * 2.6), .70, '#7d8d8a', '#b9bdb2', size=(3, 7))
    s.hills(lambda x: .63 - .02 * math.cos(x * 3), .76, '#4f7a52', '#c8c27a')
    s.ground(.70, 1.0, '#6b8d43', '#d8d98a')
    s.school(.46, .78, .52)
    s.rice_terraces(.79, 1.0)
    s.finish(out)

def city_west_java(out):  # Inclusive growth in West Java: city with tiered-roof landmark, road, hills
    s = Scene(103, '#9fb6cc', '#ece9e1'); s.clouds()
    s.hills(lambda x: .53 + .05 * math.sin(x * 2.2 + .8), .70, '#5b7ea0', '#9bb3c8', size=(3, 7))
    pal = [('#6f8297', '#a9b8c6'), ('#8796a5', '#c4ccd4'), ('#5d708a', '#94a5b8'), ('#9b8f7d', '#cfc4b0')]
    s.skyline(.74, [(.03, .12, .60, None), (.12, .19, .55, 'antenna'), (.70, .80, .52, 'antenna'), (.80, .9, .58, None), (.9, .98, .62, None),
                    (.62, .70, .62, None)], pal, win_rate=.25)
    s.tiered_roof(.41, .76, .34, .24)
    s.ground(.76, 1.0, '#557a4a', '#b8cf7e')
    s.road(.76, 1.0, x_top=(.62, .68), x_bot=(.55, .98))
    s.car(.78, .9, .12, body='#e9eef2', ev=False)
    s.finish(out)

def port(out):           # Strategic exports: port, container ship, cranes, stacked containers
    s = Scene(104, '#8fa8c2', '#e8ece9'); s.clouds()
    s.hills(lambda x: .58 + .03 * math.sin(x * 3 + 2), .68, '#6b86a0', '#a6b9ca', size=(3, 7))
    s.water(.68, '#3d6a8f', '#1d3f63')
    s.ship(.42, .80, .60)
    s.crane(.82, .74, .22); s.crane(.94, .74, .19)
    s.flat(lambda d: d.rectangle([W * .66, H * .735, W, H * .76], fill=255), '#8b8f93')
    s.containers(.68, .99, .735, rows=3)
    s.finish(out)

def offshore_wind(out):  # North-South research divide in renewable investment: offshore wind at sea
    s = Scene(105, '#86a9c4', '#e9eeec'); s.clouds()
    s.sun(.30, .56, r=22, color='#f6c27a')
    s.water(.62, '#4e7c9e', '#16395c', reflect=False, ripple='#d8e6f0')
    for x, h in [(.14, .08), (.28, .11), (.45, .145), (.64, .18), (.85, .22)]:
        s.turbine(x, .62 + h * .25, h)
    s.finish(out)

def grid(out):           # 8% growth via energy infrastructure: transmission towers toward a city
    s = Scene(106, '#93abc8', '#ebe9e2'); s.clouds()
    pal = [('#6a7f96', '#a7b6c5'), ('#7d8ea0', '#bac6d1'), ('#58708b', '#90a3b8')]
    s.skyline(.66, [(.58, .64, .55, None), (.64, .70, .50, 'spire'), (.70, .77, .53, 'antenna'), (.77, .83, .57, None), (.83, .9, .52, None), (.9, .97, .58, None)], pal)
    s.hills(lambda x: .64 + .02 * math.sin(x * 4), .76, '#3f6b5c', '#8fae86')
    s.ground(.70, 1.0, '#4f7a3f', '#c3d17c')
    a = s.tower(.14, 1.0, .50, color='#3a434c'); b = s.tower(.40, .86, .30, color='#3a434c'); c = s.tower(.56, .77, .16, color='#3a434c')
    s.wires(a, b, sag=26, color=(45, 52, 60, 200)); s.wires(b, c, sag=16, color=(45, 52, 60, 200))
    s.finish(out)

def rec_singapore(out):  # REC market vs Singapore: solar panels in front, dense skyline across water
    s = Scene(107, '#8ea7c4', '#e9ece8'); s.clouds()
    pal = [('#5f7690', '#9fb1c4'), ('#7a8da1', '#b8c5d2'), ('#4f6680', '#8aa0b6'), ('#8e9aa6', '#cdd4db')]
    s.skyline(.66, [(.05, .11, .54, None), (.11, .16, .47, 'antenna'), (.16, .22, .52, None), (.22, .27, .44, 'spire'), (.27, .34, .50, None),
                    (.34, .40, .56, None), (.40, .47, .48, 'antenna'), (.47, .53, .53, None), (.53, .60, .58, None)], pal, win_rate=.4)
    s.water(.66, '#46708f', '#21466a')
    s.ground(.76, 1.0, '#3d6a3e', '#a9c36e')
    s.solar_rows(.765, .87, rows=4, x0=-.05, x1=1.05)
    s.finish(out)

def ev_road(out):        # EV adoption gap: road with electric cars and a charging station
    s = Scene(108, '#8fb3c1', '#e8eee8'); s.clouds()
    s.hills(lambda x: .56 - .05 * math.sin(x * 3), .70, '#3f7f80', '#7fb0aa', size=(3, 7))
    s.hills(lambda x: .64 + .02 * math.cos(x * 5), .74, '#1f6655', '#8ec38c')
    s.ground(.70, 1.0, '#4d7d45', '#bed58a')
    s.road(.70, 1.0, x_top=(.40, .48), x_bot=(-.2, .75))
    s.car(.32, .86, .24, body='#f1f4f6'); s.car(.52, .77, .12, body='#c7dbe6')
    s.charger(.84, .84, .12)
    s.turbine(.80, .62, .1); s.turbine(.92, .63, .08)
    s.finish(out)

def ev_city(out):        # EV lessons from other countries: city street, EVs, chargers, office towers
    s = Scene(109, '#9db0cf', '#ece8e3'); s.clouds()
    pal = [('#46608a', '#8aa2c6'), ('#5a6e94', '#9eb0cf'), ('#3b5279', '#7891b8'), ('#6c7b98', '#aab6cb')]
    s.skyline(.74, [(-.02, .14, .48, None), (.14, .26, .53, 'antenna'), (.26, .36, .44, 'spire'), (.64, .74, .50, None), (.74, .86, .45, 'antenna'), (.86, 1.02, .52, None)], pal, win_rate=.45)
    s.ground(.74, 1.0, '#555b66', '#8a8f98')
    s.road(.74, 1.0, x_top=(.38, .62), x_bot=(-.1, 1.1))
    s.car(.32, .86, .26, body='#eef2f5'); s.car(.70, .81, .18, body='#d0e2ea')
    s.charger(.08, .84, .13); s.charger(.93, .84, .13)
    s.finish(out)

def hydro_village(out):  # LPG to induction stoves: waterfall and river powering village homes
    s = Scene(110, '#86a6bf', '#e7ece8'); s.clouds()
    s.hills(lambda x: .50 + .06 * math.sin(x * 2.4 + 1.2), .68, '#3e6f86', '#7aa5b8', size=(3, 7))
    s.hills(lambda x: .56 - .05 * x, .76, '#24563f', '#6fa36a')
    s.waterfall(.72, .52, .72, .085)
    s.ground(.72, 1.0, '#3f7a3d', '#bcd27a')
    river = [(W * .62, H * .72), (W * .82, H * .72), (W * .74, H * .80), (W * .50, H * .88), (W * .30, H * 1.0), (W * .02, H * 1.0), (W * .30, H * .88), (W * .58, H * .78)]
    s.shape(lambda d: d.polygon(river, fill=255), '#6e9fbd', '#d6e8f1', size=(1.5, 4), light_dir=(0, -1), density=1.3)
    for _ in range(40):
        x = s.rnd.uniform(.66, .80) * W; y = s.rnd.uniform(.70, .75) * H; r = s.rnd.uniform(8, 20) * S
        s.d.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(255, 255, 255, 32))
    for x, w in [(.58, .14), (.76, .13), (.91, .12)]:
        s.house(x, .86, w)
    p1 = s.pole(.40, .90, .2); p2 = s.pole(.68, .80, .14); p3 = s.pole(.86, .77, .11)
    s.wires(p1, p2, sag=10, color=(50, 45, 40, 220)); s.wires(p2, p3, sag=7, color=(50, 45, 40, 220))
    s.finish(out)

SCENES = {'solar': solar, 'school': school, 'city': city_west_java, 'port': port, 'offshore-wind': offshore_wind,
          'grid': grid, 'rec-singapore': rec_singapore, 'ev-road': ev_road, 'ev-city': ev_city, 'hydro-village': hydro_village}

if __name__ == '__main__':
    import os
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    only = sys.argv[2:] or list(SCENES)
    for k in only:
        SCENES[k](f'{outdir}/{k}.jpg'); print('painted', k)
