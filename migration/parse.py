"""Turn the raw position-based capture of ieef.or.id (raw-export.json) into clean content files.

Run:  python3 migration/parse.py
Writes migration/content/*.json and migration/issues.md (problems found on the old site).
"""
import json, re, datetime
from pathlib import Path

HERE = Path(__file__).parent
RAW = json.loads((HERE / 'raw-export.json').read_text())
OUT = HERE / 'content'; OUT.mkdir(exist_ok=True)
ZYRO = 'https://assets.zyrosite.com/'
issues = []

def atoms(slug):
    a = RAW[slug]
    last = max(x['s'] for x in a)
    footer = any('Copyright' in (x.get('t') or '') for x in a if x['s'] == last)
    return sorted([x for x in a if not (footer and x['s'] == last)], key=lambda x: (x['s'], x['y'], x['x']))

def img(a):
    v = a.get('img') or ''
    return ZYRO + v[2:] if v.startswith('Z:') else v

def paras(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text or '') if p.strip()]

MONTHS = {m: i for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                       'september', 'october', 'november', 'december'], 1)}
def find_date(text):
    m = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:[–-]\d{1,2})?,\s+(\d{4})', text or '')
    if not m: return None
    return datetime.date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2))).isoformat()

def find_place(text):
    m = re.match(r'\s*([A-Z][A-Za-z .,]+?),\s+(?:Nusa Tenggara Barat,\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)', text or '')
    return m.group(1).strip() if m else None

# ---------------------------------------------------------------- people
# Short role line for cards, condensed from each person's own bio (EN; ID added with the translations).
ROLES = {
    'ir-dzikri-firmansyah-hakam-st-pgdip-msc-phd-cfpr': 'Executive Director, IEEF',
    'yudo-anggoro-stmsmphd': 'Director, Center for Policy and Public Management, SBM ITB',
    'dr-erman-a-sumirat-se-mbuss-csa-crp-cibcwm-ak': 'Strategic finance, investment and risk management',
    'atika-irawan-smn-msc-phd-cand': 'Lecturer, SBM ITB: finance and Islamic finance',
    'achmad-billy-zulqiyami-st-sh-mh-phd-cand': 'Business law, regulation and policy studies',
    'alif-hijriah-ssi-msi': 'Quantitative economic analysis and modelling',
    'nitha-pricillia-se-mm-phd-cand': 'Program Director, CRMS Indonesia',
    'khairil-insan-bintang-spd-mpd': 'Researcher, IEEF',
    'sophia-roosma-hardeny-st-mba': 'Construction management and project risk',
    'anisya-nurfitri-k-spd-msm': 'Project Manager and Research Assistant, IEEF',
    'fadhil-nurilman-muhammad-sm-mba': 'Economic impact and feasibility studies',
    'ihda-farhatun-nisak-spd-mm': 'Researcher, IEEF',
}
about = atoms('about-us')
team_atoms = [a for a in about if a['s'] == 2]
people = []
order = 0
group = None
for a in team_atoms:
    t = a.get('t') or ''
    if t in ('Executive Director', 'Expert and Researcher'):
        group = 'leadership' if t == 'Executive Director' else 'researcher'
    if a.get('href', '').startswith('https://ieef.or.id/') and t:
        slug = a['href'].rsplit('/', 1)[-1]
        order += 1
        people.append({'slug': slug, 'group': group, 'sort': order})

for p in people:
    pa = atoms(p['slug'])
    portrait = next((a for a in pa if a.get('img') and a['x'] < 200), None)
    texts = [a for a in pa if a.get('t') and a['x'] > 400]
    name = texts[0]['t'].strip()
    bio = max(texts, key=lambda a: len(a['t']))['t']
    social = next((a['href'] for a in pa if a.get('href') and 'ieef.or.id' not in a['href']
                   and not re.match(r'https?://(m\.sc|s\.si|s\.pd|m\.si)/?$', a['href'])), None)
    first = paras(bio)[0]
    # role sentence: "... is the X at ..." / "... is a X at ..."
    m = re.search(r'\bis (?:the |an |a )?(.+?)(?: at | of the Institute| and an academic|,)', first)
    p.update(name=name, photo=img(portrait) if portrait else None, bio=paras(bio), social=social,
             role=ROLES.get(p['slug']))
    if not social: issues.append(f"Person `{p['slug']}` has no social/profile link.")
for p in people: p['photo_local'] = f"migrated/people/{p['slug']}.webp"
(OUT / 'people.json').write_text(json.dumps(people, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- about page
vision = next(a['t'] for a in about if a['t' if 't' in a else 'x'] and str(a.get('t', '')).startswith('"To become')).strip('"')
mission_text = next(a['t'] for a in about if str(a.get('t', '')).startswith('Integrating energy'))
exp = [a for a in about if a['s'] == 1 and a.get('t') and a.get('tag') != 'H1']
titles = [a for a in exp if a['w'] <= 330]
descs = [a for a in exp if a['w'] > 330]
expertise = []
for t in titles:
    side = t['x'] > 600
    cand = [d for d in descs if (d['x'] > 600) == side and 0 < d['y'] - t['y'] < 60]
    d = min(cand, key=lambda d: d['y'] - t['y']) if cand else None
    expertise.append({'title': t['t'].strip(), 'body': d['t'].strip() if d else '', 'col': 2 if side else 1, 'y': t['y']})
expertise.sort(key=lambda e: (e['y'], e['col']))
for e in expertise: e.pop('y'); e.pop('col')
(OUT / 'about.json').write_text(json.dumps({
    'vision': vision, 'mission': paras(mission_text), 'expertise': expertise}, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- policy briefs
pb = [a for a in atoms('policy-brief') if a['s'] == 0]
covers = [a for a in pb if a.get('img')]
briefs = []
for i, c in enumerate(covers):
    nxt = [x for x in covers if x['y'] > c['y'] + 50]
    row_end = min((x['y'] for x in nxt), default=10**9)
    col = [a for a in pb if abs(a['x'] - c['x']) < 120 and c['y'] < a['y'] < row_end and not a.get('img')]
    title = next((a['t'] for a in col if a.get('t') and not a.get('href')), None)
    links = [a for a in pb if a.get('href') and c['y'] < a['y'] < row_end and c['x'] - 20 <= a['x'] < c['x'] + c['w']]
    drive = next((a['href'] for a in links if 'drive.google' in a['href']), None)
    journal = next((a['href'] for a in links if 'drive.google' not in a['href']), None)
    briefs.append({'sort': i + 1, 'title': title, 'pdf_url': drive, 'journal_url': journal, 'old_cover': img(c)})
# cover thumbnails of the 3 newest show their dates
for b, date in zip(briefs, ['2026-09-01', '2026-08-01', '2026-07-01']):
    b['published'] = date
# titles on the old site: first brief uses its subtitle; restore the full title shown on the cover
briefs[0]['title_full'] = 'Mapping the Missing Link: What Global Scientometric Evidence Tells Indonesia About Financing Its Renewable Energy Transition Through Islamic Finance'
briefs[1]['title_full'] = 'Mapping the Evidence Before Scaling the Program: What Global Nutrition Research Tells Indonesia About Makan Bergizi Gratis (MBG)'
briefs[2]['title_full'] = 'When Growth Is Not Enough: Building Inclusive and Quality Growth in West Java'
issues.append('Policy briefs: only the three newest show a date (on the cover image). Older briefs have no date on the site; they keep their display order.')
(OUT / 'policy-briefs.json').write_text(json.dumps(briefs, ensure_ascii=False, indent=2))

# highlighted publications block on the policy-brief page
hl = [a for a in atoms('policy-brief') if a['s'] == 1 and a.get('href') and a.get('t')]
highlighted = [{'title': a['t'].strip(), 'url': a['href']} for a in hl]

# ---------------------------------------------------------------- research publications
research = {}
for page in ['research-publication', 'page-2-research-2018-2022', 'page-3-research-2025', 'page-4-research-2025-2-copy', 'page-5-research-2026-2025']:
    ra = atoms(page)
    for a in ra:
        t = (a.get('t') or '').strip()
        m = re.match(r'(.+?)\s*\((\d{4})\)\s*$', t, re.S)
        if not m: continue
        title, year = ' '.join(m.group(1).split()), int(m.group(2))
        dl = [x for x in ra if (x.get('t') or '').strip() == 'Download' and abs(x['y'] - a['y']) < 45]
        row = [x for x in ra if x.get('href') and not x.get('t') and abs(x['y'] - a['y']) < 45]
        url = dl[0]['href'] if dl else (a.get('href') or (row[0]['href'] if row else None))
        if url and not re.match(r'https?://[^/]+\.[a-z]{2,}/', url):
            issues.append(f'Research "{title[:60]}…": broken download link `{url}`; used the row link instead.')
            url = row[0]['href'] if row else None
        key = re.sub(r'\W+', '', title.lower())
        if key in research:
            if research[key]['year'] != year:
                # same title listed with a different year: keep both entries, as on the old site
                issues.append(f'Research "{title[:60]}…" is listed twice with different years ({research[key]["year"]} and {year}); both kept as published.')
                key = f'{key}-{year}'
            else:
                continue
        research[key] = {'title': title, 'year': year, 'url': url, 'source_page': page}
for h in highlighted:
    k = re.sub(r'\W+', '', h['title'].lower())
    match = next((r for kk, r in research.items() if kk[:40] == k[:40]), None)
    if match: match['featured'] = True
    else: research[k] = {'title': ' '.join(h['title'].split()), 'year': None, 'url': h['url'], 'featured': True, 'source_page': 'policy-brief'}
for r in research.values():
    if r['year'] is None and 'S2666188824001977' in (r['url'] or ''):
        r['year'] = 2024   # Energy Nexus article id 2024; also linked from the EV policy brief
for r in research.values():
    if r['year'] is None: issues.append(f'Highlighted publication "{r["title"][:60]}…" has no year on the site.')
research_list = sorted(research.values(), key=lambda r: (-(r['year'] or 0), r['title']))
(OUT / 'research.json').write_text(json.dumps(research_list, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- news (press releases)
cards = {}
for page in ['news-and-article', 'news-and-article-1', 'news-and-article-2']:
    na = atoms(page)
    for a in na:
        if a.get('img') and a.get('href', '').startswith('https://ieef.or.id/press-release'):
            heading = next((x for x in na if x.get('tag') == 'H2' and abs(x['x'] - a['x']) < 60 and 0 < x['y'] - a['y'] < 340), None)
            summary = next((x for x in na if x.get('href', '').startswith('https://ieef.or.id/press-release') and x.get('t')
                            and abs(x['x'] - a['x']) < 60 and 0 < x['y'] - a['y'] < 480), None)
            if not summary: continue
            slug = summary['href'].rsplit('/', 1)[-1]   # the summary link is reliable; image links on page 2 all point to -13
            if slug in cards: continue
            hl_lines = [l.strip().strip('"“”').strip() for l in (heading['t'] if heading else '').split('\n') if l.strip()]
            raw_s = summary['t']
            s = re.sub(r'\s*\.{0,5}\s*Read more\s*$', '', raw_s).strip()
            s = re.sub(r'^[A-Z][A-Za-z ]+,\s+[A-Z][a-z]+ \d{1,2}(?:[–-]\d{1,2})?,\s+\d{4}\s+[—–-]\s+', '', s)
            cards[slug] = {'card_title': hl_lines[0] if hl_lines else None, 'tagline': hl_lines[1] if len(hl_lines) > 1 else None,
                           'summary': s, 'card_image': img(a), 'list_page': page, 'raw': raw_s}
news = []
for i in range(1, 17):
    slug = f'press-release-{i}'
    pa = atoms(slug)
    texts = [a for a in pa if a.get('t') and a['x'] < 880 and a.get('tag') != 'H1' or (a.get('t') and a.get('tag') == 'H1' and a['x'] < 880 and a['y'] < 300 and a['t'] != 'Press Release')]
    head = next(a for a in pa if a.get('t') and a['x'] < 880 and a['t'].strip() not in ('Press Release',) and a['y'] < 320)
    body_a = max((a for a in pa if a.get('t') and a['x'] < 880), key=lambda a: len(a['t']))
    hero = next((a for a in pa if a.get('img') and 100 < a['x'] < 300 and a['w'] > 500), None)
    lines = [l.strip() for l in head['t'].split('\n') if l.strip()]
    title = lines[0].rstrip(':')
    tagline = lines[1].strip('"“”') if len(lines) > 1 else None
    body = paras(body_a['t'])
    if body and body[0].lower() == 'press release': body = body[1:]
    date = find_date(body[0] if body else '') or find_date(cards.get(slug, {}).get('raw', ''))
    place = find_place(body[0] if body else '') or find_place(cards.get(slug, {}).get('raw', ''))
    if body and re.fullmatch(r'[A-Z][A-Za-z ,]+,?\s+[A-Z][a-z]+ \d{1,2}(?:[–-]\d{1,2})?,\s+\d{4}', body[0]): body = body[1:]
    src = None
    if body and body[-1].lower().startswith('source:'):
        src_line = body.pop(); mm = re.search(r'https?://\S+', src_line); src = {'label': src_line.split('—')[0].replace('Source:', '').strip(' —-'), 'url': mm.group(0) if mm else None}
    c = cards.get(slug, {})
    if not c: issues.append(f'`{slug}` exists but is not listed on any News page.')
    news.append({'image_local': f'migrated/news/{slug}.webp', 'slug': slug, 'date': date, 'place': place, 'title': title, 'tagline': tagline,
                 'card_title': c.get('card_title'), 'summary': c.get('summary'),
                 'image': img(hero) if hero else c.get('card_image'), 'body': body, 'source': src})
    if 'Institute for Economy, Energy, and Finance' in body_a['t'] or 'Indonesia Energy Economics Forum' in body_a['t']:
        issues.append(f'`{slug}` names the institute incorrectly ("Institute for Economy, Energy, and Finance" or "Indonesia Energy Economics Forum"). Kept as published; worth correcting.')
news.sort(key=lambda n: n['date'] or '', reverse=True)
(OUT / 'news.json').write_text(json.dumps(news, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- careers
careers = []
for slug, order in [('post-doctoral', 1), ('research-associate', 2), ('research-asisstant', 3), ('internship-program', 4)]:
    ca = atoms(slug)
    title = next(a['t'] for a in ca if a.get('tag') == 'H1')
    blocks = []
    for a in ca:
        if a.get('t') and a.get('tag') != 'H1' and a['t'] not in ('Apply', 'Contact Us'):
            # split long single blocks at section headings so every role parses the same way
            blocks += [b.strip() for b in re.split(r'\n\s*\n(?=(?:Kualifikasi|Tanggung Jawab|Sebagai Research Associate|Periode))', a['t'])]
    intro = '\n\n'.join(b for b in blocks if not re.match(r'(Kualifikasi|Tanggung Jawab|Sebagai Research Associate|Periode)', b))
    def section(*prefixes):
        b = next((b for b in blocks if b.startswith(prefixes)), '')
        lines = [l.strip(' •\t') for l in re.split(r'\n+', b)][1:]
        return [l.rstrip('.').strip() + '.' for l in lines if l and not l.endswith(':')]
    extra = [b for b in blocks if b.startswith('Periode')]
    apply = next((a['href'] for a in ca if a.get('t') == 'Apply'), None)
    careers.append({'slug': slug, 'sort': order, 'title': title, 'intro': intro.strip(),
                    'qualifications': section('Kualifikasi'), 'responsibilities': section('Tanggung Jawab', 'Sebagai Research Associate'),
                    'notes': [l.strip() for b in extra for l in b.split('\n') if l.strip() and 's.id/' not in l],
                    'apply_url': apply, 'language': 'id',
                    'poster_local': f"migrated/careers/{'research-assistant' if slug == 'research-asisstant' else slug}.webp"})
issues.append('Career pages are written in Bahasa Indonesia only; English versions will be translated for the EN side.')
issues.append('Career URL `/research-asisstant` is misspelled on the old site. The new site uses `/career/research-assistant` and redirects the old address.')
(OUT / 'careers.json').write_text(json.dumps(careers, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- partners
NAMES = {
    'logo-itpln': 'Institut Teknologi PLN', 'university-of-dundee': 'University of Dundee', 'logo-high-res': 'SBM ITB',
    'logoupimerah': 'Universitas Pendidikan Indonesia', 'images-1': 'Universitas Padjadjaran', 'chatgpt_image_sep_2': 'Robert Gordon University Aberdeen',
    'esdm': 'Kementerian ESDM', 'universitas_gadjah_mada': 'Universitas Gadjah Mada', 'logo-ui': 'Universitas Indonesia',
    'pln-puslitbang': 'PLN Puslitbang', 'logo_pln': 'PLN', 'logo-bi': 'Bank Indonesia', 'logo_ptba': 'Bukit Asam',
    '4-pertamina-gas-negara': 'Pertamina Gas Negara', 'pageheadertitleimage': 'PLN Research Institute Journal', 'pertamina_logo': 'Pertamina',
    'pgn-': 'PGN', 'hutama-karya': 'Hutama Karya', 'logo-kpmg': 'KPMG', 'iindobara': 'Indobara',
    'logo_mckinsey': 'McKinsey & Company', '4cd37682-logo-freeport': 'Freeport Indonesia', 'adb_logo': 'Asian Development Bank',
    'asean-center-energy': 'ASEAN Centre for Energy', 'lapi-itb': 'LAPI ITB', 'logo_bcg': 'Boston Consulting Group',
    'logo-pyc': 'Purnomo Yusgiantoro Center', 'iaee': 'IAEE', 'iesr': 'IESR', 'the-asahi-glass-foundation': 'The Asahi Glass Foundation',
}
partners = []
for a in [x for x in atoms('home') if x['s'] == 3 and x.get('img')]:
    file = a['img'].split('/')[-1]
    key = next((k for k in NAMES if file.startswith(k)), None)
    LOCAL = {'university-of-dundee': 'university-of-dundee', 'universitas_gadjah_mada': 'ugm', 'logo-freeport': 'logo-freeport',
             '4cd37682-logo-freeport': 'logo-freeport', 'chatgpt_image_sep_2': 'chatgpt_image_sep_2', 'pageheadertitleimage': 'pageheadertitleimage',
             'logo_pln': 'logo_pln', 'pertamina_logo': 'pertamina_logo', 'logo_mckinsey': 'logo_mckinsey', 'logo_bcg': 'logo_bcg',
             'adb_logo': 'adb_logo', 'logo_ptba': 'logo_ptba', '4-pertamina-gas-negara': '4-pertamina-gas-negara',
             'hutama-karya': 'hutama-karya', 'logo-kpmg': 'logo-kpmg', 'the-asahi-glass-foundation': 'the-asahi-glass-foundation', 'pgn-': 'pgn'}
    local = LOCAL.get(key, key)
    partners.append({'name': NAMES.get(key) if key else None, 'logo': img(a), 'file': file, 'logo_local': f'migrated/partners/{local}.webp'})
for i, p in enumerate(sorted(partners, key=lambda p: (p['name'] is None, p['name'] or ''))): p['sort'] = i + 1
unnamed = [p['file'] for p in partners if not p['name']]
if unnamed: issues.append(f'{len(unnamed)} partner logos need a name confirmed from the image: ' + ', '.join(f'`{u}`' for u in unnamed))
(OUT / 'partners.json').write_text(json.dumps(partners, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- skipped pages
issues.append('Not migrated (template leftovers or duplicates): the two "Driving Sustainable Development…" pages (Hostinger sample text and stock photo), '
              '"IEEF and SBM ITB Strengthen Financial Literacy in Mertak Village" (duplicate of press release 3), and 8 shop sample pages.')
issues.append('Footer: Facebook and Twitter icons link to facebook.com / twitter.com home pages, not IEEF accounts. Dropped until real accounts are provided.')
issues.append('Contact page has no actual contact form or phone number on the old site.')
issues.append('The PLN Puslitbang logo on the old site is very low resolution; a better file would help.')

(HERE / 'issues.md').write_text('# Issues found on the old site\n\n' + '\n'.join(f'- {i}' for i in issues) + '\n')
print(f'people {len(people)} | briefs {len(briefs)} | research {len(research_list)} | news {len(news)} | careers {len(careers)} | partners {len(partners)} | expertise {len(expertise)}')
print(f'issues {len(issues)}')
