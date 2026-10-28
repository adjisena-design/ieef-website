// Copy for News & Article, Career, Contact and Dashboard pages (EN / ID).
import type { Lang } from '../i18n/ui';
type L = Record<Lang, string>;

export const news = {
  title: { en: 'News & Article', id: 'Berita & Artikel' } as L,
  lede: {
    en: 'Press releases, media appearances and activities from IEEF and SBM ITB researchers.',
    id: 'Siaran pers, liputan media, dan kegiatan para peneliti IEEF dan SBM ITB.',
  } as L,
  latest: { en: 'Latest', id: 'Terbaru' } as L,
  headline: { en: 'Headline', id: 'Sorotan' } as L,
  all: { en: 'All', id: 'Semua' } as L,
  year: { en: 'Year', id: 'Tahun' } as L,
  back: { en: 'All news', id: 'Semua berita' } as L,
  source: { en: 'Source', id: 'Sumber' } as L,
  watch: { en: 'Watch on YouTube', id: 'Tonton di YouTube' } as L,
  more: { en: 'More news', id: 'Berita lainnya' } as L,
  share: { en: 'Share', id: 'Bagikan' } as L,
  copy: { en: 'Copy link', id: 'Salin tautan' } as L,
  copied: { en: 'Link copied', id: 'Tautan disalin' } as L,
  englishOnly: {
    en: '',
    id: 'Artikel ini saat ini hanya tersedia dalam Bahasa Inggris.',
  } as L,
  read: { en: 'Read article', id: 'Baca artikel' } as L,
};

export const career = {
  title: { en: 'Career', id: 'Karier' } as L,
  lede: {
    en: 'Join a research team working on energy economics, finance and public policy for a fair energy transition in Indonesia.',
    id: 'Bergabunglah dengan tim riset yang bekerja di bidang ekonomi energi, keuangan, dan kebijakan publik untuk transisi energi yang adil di Indonesia.',
  } as L,
  open: { en: 'Open', id: 'Dibuka' } as L,
  closed: { en: 'Closed', id: 'Ditutup' } as L,
  openings: { en: 'Open positions', id: 'Posisi terbuka' } as L,
  view: { en: 'View role', id: 'Lihat posisi' } as L,
  apply: { en: 'Apply now', id: 'Lamar sekarang' } as L,
  back: { en: 'All positions', id: 'Semua posisi' } as L,
  qualifications: { en: 'Qualifications', id: 'Kualifikasi' } as L,
  responsibilities: { en: 'Responsibilities', id: 'Tanggung jawab' } as L,
  notes: { en: 'Good to know', id: 'Informasi tambahan' } as L,
  poster: { en: 'Recruitment poster', id: 'Poster rekrutmen' } as L,
  why: { en: 'Why IEEF', id: 'Mengapa IEEF' } as L,
  perks: [
    { en: 'Work on live policy questions with national and international partners.', id: 'Terlibat dalam isu kebijakan nyata bersama mitra nasional dan internasional.' },
    { en: 'Publish policy briefs and peer-reviewed research with senior researchers.', id: 'Menerbitkan policy brief dan riset bereputasi bersama peneliti senior.' },
    { en: 'Based at SBM ITB in Bandung, in a multidisciplinary team.', id: 'Berbasis di SBM ITB, Bandung, dalam tim multidisiplin.' },
  ] as L[],
  noRoles: {
    en: 'There are no open positions right now. Send your CV to ieef@ieef.or.id and we will keep it on file.',
    id: 'Saat ini belum ada posisi terbuka. Kirimkan CV Anda ke ieef@ieef.or.id dan kami akan menyimpannya.',
  } as L,
  questions: { en: 'Questions about a role?', id: 'Ada pertanyaan tentang posisi ini?' } as L,
  contact: { en: 'Contact us', id: 'Hubungi kami' } as L,
};

export const contact = {
  title: { en: 'Contact us', id: 'Hubungi kami' } as L,
  lede: {
    en: 'Research collaboration, consulting, training or media requests: write to us and the team will reply by email.',
    id: 'Kolaborasi riset, konsultasi, pelatihan, atau permintaan media: kirimkan pesan dan tim kami akan membalas melalui email.',
  } as L,
  formTitle: { en: 'Send a message', id: 'Kirim pesan' } as L,
  name: { en: 'Full name', id: 'Nama lengkap' } as L,
  email: { en: 'Email', id: 'Email' } as L,
  organization: { en: 'Organisation', id: 'Organisasi' } as L,
  optional: { en: 'optional', id: 'opsional' } as L,
  subject: { en: 'Topic', id: 'Topik' } as L,
  subjects: [
    { en: 'Research collaboration', id: 'Kolaborasi riset' },
    { en: 'Consulting', id: 'Konsultasi' },
    { en: 'Training', id: 'Pelatihan' },
    { en: 'Media and interviews', id: 'Media dan wawancara' },
    { en: 'Career', id: 'Karier' },
    { en: 'Other', id: 'Lainnya' },
  ] as L[],
  message: { en: 'Message', id: 'Pesan' } as L,
  send: { en: 'Send message', id: 'Kirim pesan' } as L,
  sending: { en: 'Sending...', id: 'Mengirim...' } as L,
  thanks: { en: 'Thank you. Your message has been received and the team will reply by email.', id: 'Terima kasih. Pesan Anda telah diterima dan tim kami akan membalas melalui email.' } as L,
  error: { en: 'Sorry, the message could not be sent. Please try again or email ieef@ieef.or.id.', id: 'Maaf, pesan tidak dapat dikirim. Silakan coba lagi atau kirim email ke ieef@ieef.or.id.' } as L,
  invalid: { en: 'Please fill in your name, a valid email and a message of at least 5 characters.', id: 'Mohon isi nama, email yang valid, dan pesan minimal 5 karakter.' } as L,
  privacy: { en: 'We only use your details to reply to this message.', id: 'Data Anda hanya digunakan untuk membalas pesan ini.' } as L,
  reach: { en: 'Reach us directly', id: 'Hubungi langsung' } as L,
  address: { en: 'Address', id: 'Alamat' } as L,
  addressText: 'School of Business and Management, Institut Teknologi Bandung, Jl. Ganesa, Lb. Siliwangi, Coblong, Bandung, Jawa Barat',
  map: { en: 'Open in Google Maps', id: 'Buka di Google Maps' } as L,
  mapUrl: 'https://www.google.com/maps/search/?api=1&query=SBM+ITB+Jl.+Ganesa+Bandung',
  follow: { en: 'Follow', id: 'Ikuti' } as L,
};

export const dashboard = {
  title: { en: 'Dashboards', id: 'Dasbor' } as L,
  lede: {
    en: 'Interactive data tools built from IEEF research. Each dashboard opens on its own site.',
    id: 'Alat data interaktif yang dibangun dari riset IEEF. Setiap dasbor terbuka di situsnya sendiri.',
  } as L,
  open: { en: 'Open dashboard', id: 'Buka dasbor' } as L,
  restricted: { en: 'Access by password', id: 'Akses dengan kata sandi' } as L,
  restrictedNote: {
    en: 'Some dashboards are shared with partners and need a password. Contact us for access.',
    id: 'Beberapa dasbor dibagikan kepada mitra dan memerlukan kata sandi. Hubungi kami untuk mendapatkan akses.',
  } as L,
  request: { en: 'Request access', id: 'Minta akses' } as L,
  // per-dashboard descriptions (keyed by DASHBOARDS slug)
  info: {
    'commodity-export': {
      restricted: false,
      desc: {
        en: 'A policy study on transforming Indonesia\'s commodity exports, from raw materials towards higher-value downstream products.',
        id: 'Kajian kebijakan tentang transformasi ekspor komoditas Indonesia, dari bahan mentah menuju produk hilir bernilai tambah tinggi.',
      },
    },
    jabar: {
      restricted: false,
      desc: {
        en: 'Quality growth in West Java: inequality, informal work, priority sectors and a 2026-2030 innovation roadmap built on BPS data. Prepared for an FGD at Lemhannas RI.',
        id: 'Pertumbuhan berkualitas di Jawa Barat: ketimpangan, pekerja informal, sektor prioritas, dan peta jalan inovasi 2026-2030 berbasis data BPS. Disusun untuk FGD di Lemhannas RI.',
      },
    },
    'fasilitas-ekstra': {
      restricted: true,
      desc: {
        en: 'FASTRA feasibility console: compares NPV, IRR, payback and profitability of energy projects across segments and contract schemes, with sensitivity analysis.',
        id: 'Konsol kelayakan FASTRA: membandingkan NPV, IRR, payback, dan profitabilitas proyek energi lintas segmen dan skema kontrak, dilengkapi analisis sensitivitas.',
      },
    },
    'mof-performance': {
      restricted: true,
      desc: {
        en: 'Tracks the performance of Indonesia\'s Minister of Finance across fiscal and economic indicators.',
        id: 'Memantau kinerja Menteri Keuangan Indonesia melalui indikator fiskal dan ekonomi.',
      },
    },
  } as Record<string, { restricted: boolean; desc: L }>,
};
