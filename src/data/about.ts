// About Us copy. English is from the original site; Bahasa Indonesia is a translation for review in step 7.
import type { Lang } from '../i18n/ui';
type L = Record<Lang, string>;

export const hero = {
  eyebrow: { en: 'About IEEF', id: 'Tentang IEEF' } as L,
  title: {
    en: 'An independent think tank for a <em>fair</em> energy transition',
    id: 'Lembaga kajian independen untuk transisi energi yang <em>adil</em>',
  } as L,
  lede: {
    en: 'IEEF is an independent non-profit think tank in energy, economics and finance. We deliver research, policy advocacy and public education so that economic and financial insight contributes directly to Indonesia’s sustainable development and energy transition.',
    id: 'IEEF adalah lembaga kajian nirlaba independen di bidang energi, ekonomi, dan keuangan. Kami menghadirkan riset, advokasi kebijakan, dan edukasi publik agar wawasan ekonomi dan keuangan berkontribusi langsung pada pembangunan berkelanjutan dan transisi energi Indonesia.',
  } as L,
};

export const platform = {
  en: 'As a platform for collaboration, IEEF connects government, state-owned enterprises, the private sector, academia and society, turning knowledge into action.',
  id: 'Sebagai wadah kolaborasi, IEEF menghubungkan pemerintah, BUMN, sektor swasta, akademisi, dan masyarakat untuk mengubah pengetahuan menjadi aksi.',
} as L;

export const vision = {
  label: { en: 'Our vision', id: 'Visi kami' } as L,
  text: {
    en: 'To become a national and regional reference institution in research, policy, and financing of a fair and sustainable energy transition.',
    id: 'Menjadi lembaga rujukan nasional dan regional dalam riset, kebijakan, dan pembiayaan transisi energi yang adil dan berkelanjutan.',
  } as L,
};

export const mission = {
  label: { en: 'Our mission', id: 'Misi kami' } as L,
  items: [
    { en: 'Integrating energy, economic, and financial research into public policy.', id: 'Mengintegrasikan riset energi, ekonomi, dan keuangan ke dalam kebijakan publik.' },
    { en: 'Providing financing solutions for transition projects and policies.', id: 'Menyediakan solusi pembiayaan bagi proyek dan kebijakan transisi.' },
    { en: 'Strengthening institutional capacity and governance for energy transition.', id: 'Memperkuat kapasitas kelembagaan dan tata kelola transisi energi.' },
    { en: 'Becoming a strategic partner for the government, state-owned enterprises, and international organizations.', id: 'Menjadi mitra strategis bagi pemerintah, BUMN, dan organisasi internasional.' },
  ] as L[],
};

export const expertiseHead = {
  eyebrow: { en: 'Our expertise', id: 'Keahlian kami' } as L,
  title: { en: 'Fourteen fields, one transition', id: 'Empat belas bidang, satu transisi' } as L,
  lede: {
    en: 'Our research spans the economics, finance, policy and technology that shape how Indonesia’s energy system changes.',
    id: 'Riset kami mencakup ekonomi, keuangan, kebijakan, dan teknologi yang membentuk perubahan sistem energi Indonesia.',
  } as L,
};

export const expertise: { title: L; body: L }[] = [
  { title: { en: 'Energy Economics and Finance', id: 'Ekonomi dan Keuangan Energi' },
    body: { en: 'Economic and financial analysis of energy systems, investment feasibility, electricity pricing, and project evaluation.', id: 'Analisis ekonomi dan keuangan sistem energi, kelayakan investasi, penetapan harga listrik, dan evaluasi proyek.' } },
  { title: { en: 'Sustainable Finance and Green Investment', id: 'Keuangan Berkelanjutan dan Investasi Hijau' },
    body: { en: 'Mobilization of capital through ESG principles, green bonds, blended finance, and sustainable investment strategies.', id: 'Mobilisasi modal melalui prinsip ESG, obligasi hijau, blended finance, dan strategi investasi berkelanjutan.' } },
  { title: { en: 'Electricity Market Structure and Regulation', id: 'Struktur dan Regulasi Pasar Listrik' },
    body: { en: 'Design, restructuring, pricing mechanisms, and competition analysis for efficient and transparent power markets.', id: 'Desain, restrukturisasi, mekanisme harga, dan analisis persaingan untuk pasar listrik yang efisien dan transparan.' } },
  { title: { en: 'Risk Management and Energy Systems', id: 'Manajemen Risiko dan Sistem Energi' },
    body: { en: 'Risk quantification, uncertainty modeling, and resilience frameworks for energy infrastructure and projects.', id: 'Kuantifikasi risiko, pemodelan ketidakpastian, dan kerangka ketahanan untuk infrastruktur dan proyek energi.' } },
  { title: { en: 'Energy Policy and Governance', id: 'Kebijakan dan Tata Kelola Energi' },
    body: { en: 'Formulation, analysis, and evaluation of policies and regulations to guide energy transition and long-term planning.', id: 'Perumusan, analisis, dan evaluasi kebijakan serta regulasi untuk mengarahkan transisi energi dan perencanaan jangka panjang.' } },
  { title: { en: 'Macroeconomics and Public Policy in Energy', id: 'Makroekonomi dan Kebijakan Publik Energi' },
    body: { en: 'Study of subsidies, tariffs, and fiscal instruments shaping energy access, affordability, and welfare.', id: 'Kajian subsidi, tarif, dan instrumen fiskal yang memengaruhi akses, keterjangkauan, dan kesejahteraan energi.' } },
  { title: { en: 'Renewable Energy Transition & Sustainability', id: 'Transisi Energi Terbarukan & Keberlanjutan' },
    body: { en: 'Integration of solar, hydro, wind, hydrogen, and other renewable sources, including techno-economic and sustainability assessments.', id: 'Integrasi energi surya, air, angin, hidrogen, dan sumber terbarukan lain, termasuk kajian tekno-ekonomi dan keberlanjutan.' } },
  { title: { en: 'Climate Change and Energy Resilience', id: 'Perubahan Iklim dan Ketahanan Energi' },
    body: { en: 'Assessment of climate risks, adaptation strategies, and resilience planning for energy systems.', id: 'Penilaian risiko iklim, strategi adaptasi, dan perencanaan ketahanan sistem energi.' } },
  { title: { en: 'Carbon Pricing & Environmental Economics', id: 'Harga Karbon & Ekonomi Lingkungan' },
    body: { en: 'Application of carbon markets, carbon taxes, and renewable energy certificates to accelerate decarbonization.', id: 'Penerapan pasar karbon, pajak karbon, dan sertifikat energi terbarukan untuk mempercepat dekarbonisasi.' } },
  { title: { en: 'Technology and Innovation in Energy', id: 'Teknologi dan Inovasi Energi' },
    body: { en: 'Evaluation of disruptive technologies, digital solutions, and innovation ecosystems driving energy transition.', id: 'Evaluasi teknologi disruptif, solusi digital, dan ekosistem inovasi yang mendorong transisi energi.' } },
  { title: { en: 'Electric Vehicles and Emerging Technologies', id: 'Kendaraan Listrik dan Teknologi Baru' },
    body: { en: 'Analysis of EV adoption, charging networks, hydrogen mobility, and innovation pathways.', id: 'Analisis adopsi kendaraan listrik, jaringan pengisian daya, mobilitas hidrogen, dan jalur inovasi.' } },
  { title: { en: 'Energy Law and Regulation', id: 'Hukum dan Regulasi Energi' },
    body: { en: 'Legal frameworks for energy markets, environmental compliance, and governance of energy resources.', id: 'Kerangka hukum pasar energi, kepatuhan lingkungan, dan tata kelola sumber daya energi.' } },
  { title: { en: 'Consumer Behaviour and Technology Adoption', id: 'Perilaku Konsumen dan Adopsi Teknologi' },
    body: { en: 'Understanding behavioral, social, and cultural factors that influence acceptance of clean energy technologies.', id: 'Memahami faktor perilaku, sosial, dan budaya yang memengaruhi penerimaan teknologi energi bersih.' } },
  { title: { en: 'Capacity Building and Knowledge Transfer', id: 'Peningkatan Kapasitas dan Alih Pengetahuan' },
    body: { en: 'Design of training, education, and institutional strengthening programs to build expertise in energy economics and policy.', id: 'Perancangan pelatihan, pendidikan, dan program penguatan kelembagaan untuk membangun keahlian di bidang ekonomi dan kebijakan energi.' } },
];

export const team = {
  eyebrow: { en: 'Our people', id: 'Tim kami' } as L,
  title: { en: 'Leadership, fellows and research team', id: 'Pimpinan, fellow, dan tim riset' } as L,
  leadership: { en: 'Executive Director', id: 'Direktur Eksekutif' } as L,
  researchers: { en: 'Experts and researchers', id: 'Pakar dan peneliti' } as L,
  viewProfile: { en: 'View profile', id: 'Lihat profil' } as L,
};

export const cta = {
  title: { en: 'Work with us', id: 'Bekerja bersama kami' } as L,
  body: {
    en: 'We welcome researchers, partners and institutions who share our commitment to a fair and sustainable energy future.',
    id: 'Kami terbuka bagi peneliti, mitra, dan lembaga yang memiliki komitmen yang sama terhadap masa depan energi yang adil dan berkelanjutan.',
  } as L,
  careers: { en: 'See open roles', id: 'Lihat lowongan' } as L,
  contact: { en: 'Contact us', id: 'Hubungi kami' } as L,
};

export const profile = {
  back: { en: 'All team members', id: 'Semua anggota tim' } as L,
  others: { en: 'More from the team', id: 'Anggota tim lainnya' } as L,
  bioNote: { en: '', id: 'Profil ini saat ini tersedia dalam bahasa Inggris.' } as L,
  social: { en: 'Profile', id: 'Profil' } as L,
};
