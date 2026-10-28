// Publications copy, theme labels and research topics (EN/ID).
import type { Lang } from '../i18n/ui';
type L = Record<Lang, string>;

export const THEMES = {
  energy: { label: { en: 'Energy & finance', id: 'Energi & keuangan' } as L, color: '#189080' },
  social: { label: { en: 'Social policy', id: 'Kebijakan sosial' } as L, color: '#b4602a' },
  economy: { label: { en: 'Economy & growth', id: 'Ekonomi & pertumbuhan' } as L, color: '#2d4aa0' },
} as const;
export type Theme = keyof typeof THEMES;

// Topic tags for research, matched on title keywords at build time.
export const TOPICS: { key: string; label: L; match: RegExp }[] = [
  { key: 'transition', label: { en: 'Energy transition & renewables', id: 'Transisi energi & terbarukan' },
    match: /renewable|solar|photovoltaic|\bpv\b|wind|hydrogen|geothermal|biomass|wood pellet|energy transition|net zero|ndc|nuclear|offshore|lpg|induction|power generation|post-mining|clean energy/i },
  { key: 'power', label: { en: 'Electricity & power markets', id: 'Kelistrikan & pasar listrik' },
    match: /electricity|power sector|power plant|power generation|grid|market power|interconnection|rooftop/i },
  { key: 'finance', label: { en: 'Finance & investment', id: 'Keuangan & investasi' },
    match: /financ|investment|valuation|real option|cash flow|bank|fintech|lending|stock|esg|real estate|profitability/i },
  { key: 'climate', label: { en: 'Carbon & climate', id: 'Karbon & iklim' },
    match: /carbon|ccs|emission|climate|green|decarboni|environment/i },
  { key: 'mobility', label: { en: 'Electric vehicles', id: 'Kendaraan listrik' },
    match: /electric vehicle|\bev\b|charging/i },
  { key: 'economy', label: { en: 'Economy & policy', id: 'Ekonomi & kebijakan' },
    match: /econom|gdp|policy|export|digital|consumer|urban|cities|growth|import|coal|nickel|mining|lifestyle/i },
];
export const topicsFor = (title: string) => TOPICS.filter((t) => t.match.test(title)).map((t) => t.key);

export const ui = {
  hubEyebrow: { en: 'Publication', id: 'Publikasi' } as L,
  hubTitle: { en: 'Research that turns evidence into <em>policy</em>', id: 'Riset yang mengubah bukti menjadi <em>kebijakan</em>' } as L,
  hubLede: {
    en: 'Our publications reflect IEEF’s commitment to advancing knowledge and shaping a fair, sustainable energy future. They provide evidence-based insights for decision-makers, industry leaders and the wider public.',
    id: 'Publikasi kami mencerminkan komitmen IEEF untuk memajukan pengetahuan dan membentuk masa depan energi yang adil dan berkelanjutan. Publikasi ini menghadirkan wawasan berbasis bukti bagi pengambil keputusan, pelaku industri, dan masyarakat luas.',
  } as L,
  briefsTitle: { en: 'Policy briefs', id: 'Policy brief' } as L,
  briefsLede: {
    en: 'Our policy briefs translate research findings into concise, practical and evidence-based recommendations, helping policymakers, industry leaders and stakeholders understand key issues, weigh policy options and make informed decisions for a fair and sustainable energy transition.',
    id: 'Policy brief kami menerjemahkan temuan riset menjadi rekomendasi yang ringkas, praktis, dan berbasis bukti, membantu pembuat kebijakan, pelaku industri, dan pemangku kepentingan memahami isu utama, menimbang pilihan kebijakan, dan mengambil keputusan untuk transisi energi yang adil dan berkelanjutan.',
  } as L,
  researchTitle: { en: 'Research publications', id: 'Publikasi riset' } as L,
  researchLede: {
    en: 'Peer-reviewed studies by IEEF researchers and collaborators in international and national journals.',
    id: 'Kajian terulas sejawat oleh peneliti IEEF dan kolaborator di jurnal internasional dan nasional.',
  } as L,
  latestBriefs: { en: 'Latest policy briefs', id: 'Policy brief terbaru' } as L,
  latestResearch: { en: 'Latest research', id: 'Riset terbaru' } as L,
  viewAllBriefs: { en: 'All policy briefs', id: 'Semua policy brief' } as L,
  viewAllResearch: { en: 'All research publications', id: 'Semua publikasi riset' } as L,
  briefs: { en: 'policy briefs', id: 'policy brief' } as L,
  papers: { en: 'research papers', id: 'makalah riset' } as L,
  all: { en: 'All', id: 'Semua' } as L,
  download: { en: 'Download PDF', id: 'Unduh PDF' } as L,
  journal: { en: 'Journal article', id: 'Artikel jurnal' } as L,
  read: { en: 'Read article', id: 'Baca artikel' } as L,
  policyBrief: { en: 'Policy brief', id: 'Policy brief' } as L,
  highlighted: { en: 'Highlighted publications', id: 'Publikasi unggulan' } as L,
  search: { en: 'Search by title or keyword', id: 'Cari judul atau kata kunci' } as L,
  year: { en: 'Year', id: 'Tahun' } as L,
  topic: { en: 'Topic', id: 'Topik' } as L,
  anyYear: { en: 'All years', id: 'Semua tahun' } as L,
  showing: { en: 'Showing', id: 'Menampilkan' } as L,
  of: { en: 'of', id: 'dari' } as L,
  none: { en: 'No publications match these filters.', id: 'Tidak ada publikasi yang sesuai dengan filter ini.' } as L,
  reset: { en: 'Clear filters', id: 'Hapus filter' } as L,
  noYear: { en: 'Year not listed', id: 'Tahun tidak tercantum' } as L,
};
