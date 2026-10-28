// Interface strings for both languages. Page content lives in src/data (and later in Supabase).
export const languages = { en: 'EN', id: 'ID' } as const;
export type Lang = keyof typeof languages;
export const defaultLang: Lang = 'en';

export const ui = {
  en: {
    'site.name': 'IEEF',
    'site.full': 'Institute for Energy, Economics & Finance',
    'site.tagline': 'Empowering sustainable growth with economic and financial insight.',
    'nav.home': 'Home',
    'nav.about': 'About Us',
    'nav.publication': 'Publication',
    'nav.policyBrief': 'Policy Brief',
    'nav.research': 'Research Publication',
    'nav.dashboard': 'Dashboard',
    'nav.news': 'News & Article',
    'nav.career': 'Career',
    'nav.contact': 'Contact us',
    'nav.menu': 'Menu',
    'nav.close': 'Close menu',
    'nav.skip': 'Skip to content',
    'lang.switch': 'Ganti ke Bahasa Indonesia',
    'cta.exploreResearch': 'Explore research',
    'cta.openDashboards': 'Open dashboards',
    'cta.openDashboard': 'Open dashboard',
    'cta.viewAllPubs': 'View all publications',
    'cta.readBrief': 'Read the brief',
    'cta.readArticle': 'Read article',
    'cta.aboutIeef': 'About IEEF',
    'footer.explore': 'Explore',
    'footer.dashboards': 'Dashboards',
    'footer.contact': 'Contact',
    'footer.rights': 'All rights reserved.',
    'footer.address': 'Jl. Ganesa, Lb. Siliwangi, Coblong, Bandung, Jawa Barat',
  },
  id: {
    'site.name': 'IEEF',
    'site.full': 'Institute for Energy, Economics & Finance',
    'site.tagline': 'Mendorong pertumbuhan berkelanjutan melalui wawasan ekonomi dan keuangan.',
    'nav.home': 'Beranda',
    'nav.about': 'Tentang Kami',
    'nav.publication': 'Publikasi',
    'nav.policyBrief': 'Policy Brief',
    'nav.research': 'Publikasi Riset',
    'nav.dashboard': 'Dasbor',
    'nav.news': 'Berita & Artikel',
    'nav.career': 'Karier',
    'nav.contact': 'Hubungi kami',
    'nav.menu': 'Menu',
    'nav.close': 'Tutup menu',
    'nav.skip': 'Lewati ke konten',
    'lang.switch': 'Switch to English',
    'cta.exploreResearch': 'Jelajahi riset',
    'cta.openDashboards': 'Buka dasbor',
    'cta.openDashboard': 'Buka dasbor',
    'cta.viewAllPubs': 'Lihat semua publikasi',
    'cta.readBrief': 'Baca policy brief',
    'cta.readArticle': 'Baca artikel',
    'cta.aboutIeef': 'Tentang IEEF',
    'footer.explore': 'Jelajahi',
    'footer.dashboards': 'Dasbor',
    'footer.contact': 'Kontak',
    'footer.rights': 'Hak cipta dilindungi.',
    'footer.address': 'Jl. Ganesa, Lb. Siliwangi, Coblong, Bandung, Jawa Barat',
  },
} as const;

export type UIKey = keyof (typeof ui)['en'];

export function t(lang: Lang, key: UIKey): string {
  return ui[lang][key] ?? ui[defaultLang][key];
}

/** Language from a URL path: "/id/..." is Indonesian, everything else English. */
export function getLang(url: URL): Lang {
  return url.pathname === '/id' || url.pathname.startsWith('/id/') ? 'id' : 'en';
}

/** Localised href for an English path, e.g. href('id', '/about-us') -> '/id/about-us'. */
export function href(lang: Lang, path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  if (lang === 'en') return clean;
  return clean === '/' ? '/id' : `/id${clean}`;
}

/** The same page in the other language. */
export function alternate(url: URL): { lang: Lang; path: string } {
  const lang = getLang(url);
  const base = lang === 'id' ? url.pathname.replace(/^\/id(?=\/|$)/, '') || '/' : url.pathname;
  const other: Lang = lang === 'en' ? 'id' : 'en';
  return { lang: other, path: href(other, base) };
}

/** Main navigation. Paths keep the current site's slugs so old links keep working. */
export const NAV: { key: UIKey; path: string; children?: { key: UIKey; path: string }[] }[] = [
  { key: 'nav.home', path: '/' },
  { key: 'nav.about', path: '/about-us' },
  {
    key: 'nav.publication', path: '/publication',
    children: [
      { key: 'nav.policyBrief', path: '/policy-brief' },
      { key: 'nav.research', path: '/research-publication' },
    ],
  },
  { key: 'nav.dashboard', path: '/dashboard' },
  { key: 'nav.news', path: '/news-and-article' },
  { key: 'nav.career', path: '/career' },
];

/** External dashboards (separate apps on their own subdomains — linked, not rebuilt). */
export const DASHBOARDS = [
  { slug: 'commodity-export', url: 'https://transformasi-ekspor-komoditas.ieef.or.id/',
    title: { en: 'Commodity Export Transformation', id: 'Transformasi Ekspor Komoditas' },
    tag: { en: 'Trade', id: 'Perdagangan' } },
  { slug: 'jabar', url: 'https://penguatan-ekonomi-jabar.ieef.or.id/',
    title: { en: 'Strengthening the West Java Economy', id: 'Penguatan Ekonomi Jabar' },
    tag: { en: 'Regional', id: 'Regional' } },
  { slug: 'fasilitas-ekstra', url: 'https://fasilitas-ekstra.ieef.or.id/',
    title: { en: 'Fasilitas Ekstra Console', id: 'Fasilitas Ekstra Console' },
    tag: { en: 'Fiscal', id: 'Fiskal' } },
  { slug: 'mof-performance', url: 'https://indonesia-minister-of-finance-performance.ieef.or.id/',
    title: { en: 'Minister of Finance Performance', id: 'Kinerja Menteri Keuangan' },
    tag: { en: 'Public finance', id: 'Keuangan publik' } },
] as const;
