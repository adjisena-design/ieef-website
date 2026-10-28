// Fixed homepage copy. Lists (news, briefs, research, partners) come from src/lib/content.ts.
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





export const partnersTitle = { en: 'Our network & collaboration', id: 'Jejaring & kolaborasi kami' } as L;

