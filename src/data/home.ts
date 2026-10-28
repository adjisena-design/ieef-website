// Homepage content for step 1. In step 2 the lists (briefs, research, news, partners)
// move to Supabase so the team can update them from the console.
import type { Lang } from '../i18n/ui';

type L = Record<Lang, string>;

export const hero = {
  eyebrow: { en: 'Institute for Energy, Economics & Finance', id: 'Institute for Energy, Economics & Finance' } as L,
  // <em> wraps the accent word (rendered italic teal)
  title: {
    en: 'Empowering <em>sustainable</em> growth with economic &amp; financial insight',
    id: 'Mendorong pertumbuhan <em>berkelanjutan</em> dengan wawasan ekonomi &amp; keuangan',
  } as L,
  sub: {
    en: 'An independent think tank delivering research, consulting, publications and training for a fair energy transition and sustainable economic growth in Indonesia.',
    id: 'Lembaga kajian independen yang menghadirkan riset, konsultasi, publikasi, dan pelatihan untuk transisi energi yang adil serta pertumbuhan ekonomi berkelanjutan di Indonesia.',
  } as L,
};

// TODO(step 2): confirm counts from the exported content.
export const stats = [
  { value: '40+', label: { en: 'Publications', id: 'Publikasi' } as L },
  { value: '4', label: { en: 'Live dashboards', id: 'Dasbor interaktif' } as L },
  { value: '30+', label: { en: 'Partners', id: 'Mitra' } as L },
];

export const about = {
  eyebrow: { en: 'What defines us', id: 'Siapa kami' } as L,
  title: { en: 'Economics and policy specialists for a fair transition', id: 'Spesialis ekonomi dan kebijakan untuk transisi yang adil' } as L,
  body: {
    en: "IEEF is an independent non-profit think tank in energy, economics and finance. We deliver research, policy advocacy and public education so that economic and financial insight contributes directly to Indonesia's sustainable development and energy transition.",
    id: 'IEEF adalah lembaga kajian nirlaba independen di bidang energi, ekonomi, dan keuangan. Kami menghadirkan riset, advokasi kebijakan, dan edukasi publik agar wawasan ekonomi dan keuangan berkontribusi langsung pada pembangunan berkelanjutan dan transisi energi Indonesia.',
  } as L,
  chip: { en: 'Research · Advisory · Training · Advocacy', id: 'Riset · Konsultasi · Pelatihan · Advokasi' } as L,
};

export const services = [
  { icon: 'chart', title: { en: 'Research & Publications', id: 'Riset & Publikasi' },
    body: { en: 'Peer-reviewed studies and policy briefs on energy transition, growth and public finance.', id: 'Kajian terulas sejawat dan policy brief tentang transisi energi, pertumbuhan, dan keuangan publik.' } },
  { icon: 'chat', title: { en: 'Consultation', id: 'Konsultasi' },
    body: { en: 'Evidence-based advisory for government, SOEs and the private sector.', id: 'Pendampingan berbasis bukti bagi pemerintah, BUMN, dan sektor swasta.' } },
  { icon: 'cap', title: { en: 'Workshop & Training', id: 'Workshop & Pelatihan' },
    body: { en: 'Capacity building in energy economics, modelling and financial analysis.', id: 'Peningkatan kapasitas di bidang ekonomi energi, pemodelan, dan analisis keuangan.' } },
  { icon: 'megaphone', title: { en: 'Advocacy', id: 'Advokasi' },
    body: { en: 'Turning research into public dialogue and actionable policy.', id: 'Mengubah hasil riset menjadi dialog publik dan kebijakan yang dapat dijalankan.' } },
] as const;

export const dashboardsSection = {
  eyebrow: { en: 'Data, in the open', id: 'Data terbuka' } as L,
  title: { en: 'Live policy dashboards', id: 'Dasbor kebijakan interaktif' } as L,
  body: {
    en: 'Interactive tools that track exports, regional growth and public finance, updated as new data lands.',
    id: 'Perangkat interaktif untuk memantau ekspor, pertumbuhan daerah, dan keuangan publik, diperbarui seiring data terbaru.',
  } as L,
};

// Decorative sparklines only (not real data) — one per dashboard, same order as DASHBOARDS.
export const sparks = [
  [12, 14, 13, 17, 19, 18, 23, 26, 25, 30],
  [20, 21, 19, 22, 24, 23, 25, 27, 28, 29],
  [30, 26, 27, 22, 24, 20, 21, 18, 19, 16],
  [15, 18, 17, 21, 20, 24, 22, 26, 29, 28],
];

export const pubsSection = {
  eyebrow: { en: 'Latest thinking', id: 'Pemikiran terbaru' } as L,
  title: { en: 'Publications & policy briefs', id: 'Publikasi & policy brief' } as L,
  featuredLabel: { en: 'Featured policy brief', id: 'Policy brief pilihan' } as L,
  researchLabel: { en: 'Research publications', id: 'Publikasi riset' } as L,
};

// Publication titles stay in their original language.
export const featuredBrief = {
  title: 'Strengthening Indonesia’s Path to 8% Growth: Leveraging Multiplier Effects from Energy Infrastructure Investment',
  summary: {
    en: 'How public investment in energy infrastructure multiplies into wider economic activity, and what that means for reaching 8% growth.',
    id: 'Bagaimana investasi publik di infrastruktur energi berlipat ganda menjadi aktivitas ekonomi yang lebih luas, dan artinya bagi target pertumbuhan 8%.',
  } as L,
  href: '/policy-brief',
};

export const briefs = [
  'From Fragmentation to Credibility: Indonesia’s REC Market in Comparison with Singapore',
  'When Growth Is Not Enough: Building Inclusive and Quality Growth in West Java',
];

export const research = [
  { year: 2024, title: 'Switching from LPG to electricity in Indonesia: a study in the Java Bali grid' },
  { year: 2024, title: 'The Effect of GDP and Exchange Rate on Import of Photovoltaic Cells in Indonesia' },
  { year: 2023, title: 'Long-Term Scenarios of Indonesia Power Sector to Achieve Nationally Determined Contribution (NDC) 2060' },
];

export const news = {
  date: '2026-09-30',
  title: { en: 'Indonesia’s 2027 State Budget on Kompas Bisnis', id: 'APBN 2027 Indonesia di Kompas Bisnis' } as L,
  summary: { en: 'Spending quality, not size, should define the 2027 State Budget.', id: 'Kualitas belanja, bukan besarnya, yang seharusnya menentukan APBN 2027.' } as L,
  href: '/news-and-article',
};

export const partnersTitle = { en: 'Our network & collaboration', id: 'Jejaring & kolaborasi kami' } as L;

// TODO(step 2): replace with logos exported from the current site.
export const partners = ['Bank Indonesia', 'Asian Development Bank', 'Kementerian ESDM', 'PLN', 'PLN Puslitbang', 'Pertamina', 'PGN',
  'Bukit Asam', 'Freeport Indonesia', 'Hutama Karya', 'Indobara', 'KPMG', 'McKinsey & Company', 'BCG', 'ASEAN Centre for Energy',
  'IESR', 'IAEE', 'Universitas Indonesia', 'UGM', 'UPI', 'ITPLN', 'University of Dundee', 'LAPI ITB', 'Asahi Glass Foundation'];
