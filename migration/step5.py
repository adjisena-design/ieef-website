"""Step 5 content changes: readable news slugs (old slug kept in legacy_slug for redirects) and English career text.
Writes supabase/migrations/20261028000004_step5.sql and updates the local snapshot."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP = ROOT / 'src/data/snapshot'

NEWS_SLUGS = {
    'press-release-16': '2027-state-budget-6-percent-growth-target',
    'press-release-15': 'economy-grows-5-29-percent-q2-2026',
    'press-release-14': 'financial-market-pressure-real-sector',
    'press-release-13': 'lower-unemployment-formal-productive-jobs',
    'press-release-12': 'growth-with-real-benefits-lemhannas-fgd',
    'press-release-11': 'growth-that-benefits-the-public-kompas-tv',
    'press-release-10': 'reclicks-grant-asean-electricity-market',
    'press-release-9': 'sbm-itb-economist-on-kompas-tv',
    'press-release-8': 'itb-67th-dies-natalis-research-recognition',
    'press-release-7': 'komdigi-ieef-sbm-itb-green-technology-industry',
    'press-release-6': 'csis-research-partnership-workshop',
    'press-release-5': 'geo-dipa-geothermal-governance-leadership',
    'press-release-4': 'from-npv-to-enpv-energy-project-feasibility',
    'press-release-3': 'financial-literacy-mertak-village-lombok',
    'press-release-2': 'asahi-glass-foundation-grant-seminar-2025',
    'press-release-1': 'pyc-international-energy-conference-2025',
}

TOOLS = ('Familiar with Canva, Microsoft Office, social media and analytical tools for economics, energy and finance such as '
         'Excel, Stata, SPSS, EViews, R, Python, Power BI, Tableau, Bloomberg, Trading Economics, World Bank Data, IEA Statistics '
         'or other data platforms.')
METHODS = ('Input-Output Analysis, Real Option Valuation, Project Valuation, Techno-Economic Modelling, Monte Carlo Simulation, '
           'LCOE Analysis, Optimization Modelling or Data Analytics')
LANG = 'Good written and verbal communication in Bahasa Indonesia and English.'

CAREERS_EN = {
    'post-doctoral': dict(
        title='Postdoctoral Researcher',
        intro='The Postdoctoral Researcher is an advanced research position that leads, develops and strengthens IEEF\'s research '
              'agenda in energy economics, finance and public policy.',
        qualifications=[
            'Based in Bandung.',
            'PhD in Economics, Finance, Management, Energy, Public Policy or a related field.',
            'Previous project and research experience is an advantage.',
            f'Able to carry out economic and financial analysis of energy projects using at least one of: {METHODS}.',
            TOOLS, LANG,
            'Thorough, proactive, with strong academic leadership and the ability to work in a multidisciplinary research team.'],
        responsibilities=[
            'Lead and carry out research and projects in energy economics, finance and public policy, from concept to reporting.',
            'Develop economic and energy policy models that support IEEF\'s strategic recommendations to national and international partners.',
            'Contribute to policy briefs, research reports, working papers and scientific publications such as journal articles and conference papers.',
            'Supervise or mentor research assistants, interns and junior researchers.',
            'Represent IEEF in academic and energy policy forums, including discussions, seminars, FGDs, workshops, conferences and external collaborations.',
            'Support the development of research proposals, concept notes, methodological frameworks and collaboration with strategic partners.'],
        notes=[]),
    'research-associate': dict(
        title='Research Associate',
        intro='SBM ITB and the Institute for Energy, Economics & Finance (IEEF) invite academics and researchers to contribute to '
              'strategic research in Energy Economics and Finance.\n\nThis position reports directly to Ir. Dzikri Firmansyah Hakam, '
              'S.T., Pg.Dip., M.Sc., Ph.D., CFP®, and is intended for candidates with a strong academic background and a record of '
              'internationally reputable publications.',
        qualifications=[
            'PhD in a relevant field.',
            'At least one Q1 publication as first author in the last five years.',
            'Expertise in Energy Economics and Finance.',
            'Able to work independently and to targets.'],
        responsibilities=[
            'Conduct research in energy economics and finance.',
            'Contribute to scientific publications and policy briefs.',
            'Take part in research discussions and strategic collaborations.',
            'Deliver measurable research output targets.'],
        notes=[
            'Period: April to November 2026.',
            'Open until the position is filled.',
            'Join us and help drive research that matters for Indonesia\'s energy transition.']),
    'research-assistant': dict(
        title='Research Assistant',
        intro='The Research Assistant supports research, analysis and study preparation in economics, energy, finance and public '
              'policy. The role suits candidates who want to learn more about strategic issues such as the energy transition, '
              'sustainable finance, energy sector investment, policy analysis and data-driven research. Research Assistants work '
              'with senior researchers and a multidisciplinary team on data collection, analysis, report writing and research and '
              'institutional communication materials.',
        qualifications=[
            'Based in Bandung.',
            'Bachelor\'s or master\'s graduate, or final-year student, in Economics, Finance, Management, Energy, Public Policy, '
            'Industrial Engineering, Statistics or a related field.',
            'Previous project and research experience is an advantage.',
            f'Able to carry out analysis under senior supervision using one of: {METHODS}.',
            TOOLS, LANG,
            'Thorough, proactive and able to work in a multidisciplinary research team.'],
        responsibilities=[
            'Carry out research and projects in energy economics, finance and public policy, including data collection, analysis and reporting.',
            'Conduct economic and financial analysis in the energy sector.',
            'Contribute to presentations, policy briefs and scientific publications with the research team.',
            'Take part in IEEF internal activities such as workshops, research discussions and multidisciplinary collaboration.'],
        notes=[]),
    'internship-program': dict(
        title='Internship',
        intro='IEEF offers students with a strong interest in learning and growing the chance to take part directly in research on '
              'economics, energy, finance and public policy. The internship is for candidates who want to understand strategic '
              'issues such as the energy transition, sustainable finance, economic policy, data analysis and evidence-based policy research.',
        qualifications=[
            'Based in Bandung.',
            'Current undergraduate student in at least the 4th semester, or current master\'s student.',
            'Strong interest in research, economics, energy, finance and public policy.',
            'Willing to learn and take part in academic and policy research.',
            'Able to analyse data, search the literature and write academic texts.',
            'Familiar with Microsoft Office or Google Workspace, Canva, social media and analytical tools for economics, energy and finance.',
            LANG,
            'Thorough, proactive, responsible and able to work in a multidisciplinary team.',
            'Curious about national and global strategic issues, especially the energy transition, economic development and sustainable finance.'],
        responsibilities=[
            'Support the research team in collecting, processing and analysing quantitative and qualitative data.',
            'Help prepare literature reviews, policy briefs, research reports and academic publications.',
            'Carry out desk research on economics, energy, finance, sustainable development and public policy.',
            'Help with data visualisation, charts, tables and research presentation materials.',
            'Help coordinate project activities, including document preparation, minutes and technical administrative support.',
            'Support activity and project reports and research communication materials.',
            'Contribute to internal discussions to strengthen the quality of analysis and policy recommendations.'],
        notes=[]),
}

def q(s): return "'" + s.replace("'", "''") + "'"
def arr(xs): return 'array[' + ', '.join(q(x) for x in xs) + ']::text[]' if xs else "'{}'::text[]"

sql = ['-- Step 5: readable news slugs (legacy slug kept for redirects) and English career text',
       'alter table public.news add column if not exists legacy_slug text unique;']
for old, new in NEWS_SLUGS.items():
    sql.append(f"update public.news set legacy_slug = {q(old)}, slug = {q(new)} where slug = {q(old)};")
for slug, c in CAREERS_EN.items():
    sql.append(f"update public.careers set title_en = {q(c['title'])}, intro_en = {q(c['intro'])}, "
               f"qualifications_en = {arr(c['qualifications'])}, responsibilities_en = {arr(c['responsibilities'])}, "
               f"notes_en = {arr(c['notes'])} where slug = {q(slug)};")
out = ROOT / 'supabase/migrations/20261028000004_step5.sql'
out.write_text('\n'.join(sql) + '\n')

news = json.loads((SNAP / 'news.json').read_text())
for n in news:
    if n['slug'] in NEWS_SLUGS:
        n['legacy_slug'] = n['slug']; n['slug'] = NEWS_SLUGS[n['slug']]
(SNAP / 'news.json').write_text(json.dumps(news, ensure_ascii=False, indent=1))
careers = json.loads((SNAP / 'careers.json').read_text())
for c in careers:
    e = CAREERS_EN.get(c['slug'])
    if e:
        c.update(title_en=e['title'], intro_en=e['intro'], qualifications_en=e['qualifications'],
                 responsibilities_en=e['responsibilities'], notes_en=e['notes'])
(SNAP / 'careers.json').write_text(json.dumps(careers, ensure_ascii=False, indent=1))
print('wrote', out, len(sql), 'statements')
