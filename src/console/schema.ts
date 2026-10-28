// Field definitions for each content type the console edits.
export type FieldType = 'text' | 'textarea' | 'longtext' | 'date' | 'number' | 'bool' | 'select' | 'image' | 'pdf' | 'url' | 'list' | 'slug';
export interface Field {
  key: string;
  label: string;
  type: FieldType;
  required?: boolean;
  help?: string;
  options?: { value: string; label: string }[];
  pair?: string;            // EN/ID fields shown side by side share a pair name
  from?: string[];          // slug: build from these fields
  showIf?: (row: Record<string, any>) => boolean;
  folder?: string;          // upload folder in the media bucket
}
export interface Entity {
  key: 'publications' | 'news' | 'careers' | 'people' | 'partners';
  label: string;
  singular: string;
  order: { column: string; ascending: boolean }[];
  title: (r: Record<string, any>) => string;
  subtitle: (r: Record<string, any>) => string;
  tabs?: { label: string; filter: (r: Record<string, any>) => boolean; defaults: Record<string, any> }[];
  defaults: Record<string, any>;
  fields: Field[];
  sitePath: (r: Record<string, any>) => string | null;
}

const SCENES = ['solar', 'offshore-wind', 'grid', 'ev-road', 'ev-city', 'hydro-village', 'rec-singapore', 'school', 'city', 'port'];
const sceneLabel: Record<string, string> = {
  solar: 'Solar farm', 'offshore-wind': 'Offshore wind', grid: 'Power grid and city', 'ev-road': 'Electric cars on a road',
  'ev-city': 'Electric cars in the city', 'hydro-village': 'Waterfall and village', 'rec-singapore': 'Solar and skyline across water',
  school: 'School and rice fields', city: 'West Java city', port: 'Port and container ship',
};
const published: Field = { key: 'published', label: 'Show on website', type: 'bool', help: 'Off = hidden from the public site (kept as a draft).' };
const sort: Field = { key: 'sort', label: 'Order', type: 'number', help: 'Lower numbers appear first.' };
const fmtDate = (d?: string | null) => (d ? new Date(d + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '');

export const ENTITIES: Entity[] = [
  {
    key: 'publications', label: 'Publications', singular: 'publication',
    order: [{ column: 'kind', ascending: true }, { column: 'year', ascending: false }, { column: 'sort', ascending: true }],
    title: (r) => r.title, subtitle: (r) => [r.kind === 'policy_brief' ? 'Policy brief' : 'Research', r.year].filter(Boolean).join(' · '),
    tabs: [
      { label: 'Policy briefs', filter: (r) => r.kind === 'policy_brief', defaults: { kind: 'policy_brief', theme: 'energy' } },
      { label: 'Research', filter: (r) => r.kind === 'research', defaults: { kind: 'research' } },
    ],
    defaults: { kind: 'policy_brief', theme: 'energy', published: true, featured: false, sort: 100, year: new Date().getFullYear() },
    sitePath: (r) => (r.kind === 'policy_brief' ? '/policy-brief' : '/research-publication'),
    fields: [
      { key: 'kind', label: 'Type', type: 'select', required: true, options: [{ value: 'policy_brief', label: 'Policy brief' }, { value: 'research', label: 'Research publication' }] },
      { key: 'title', label: 'Title', type: 'textarea', required: true, help: 'Keep it in the language it was published in. For briefs, "Main title: subtitle" puts the subtitle on its own line on the cover.' },
      { key: 'slug', label: 'Web address', type: 'slug', required: true, from: ['title'] },
      { key: 'summary_en', label: 'Summary (English)', type: 'textarea', pair: 'summary' },
      { key: 'summary_id', label: 'Summary (Bahasa Indonesia)', type: 'textarea', pair: 'summary' },
      { key: 'year', label: 'Year', type: 'number' },
      { key: 'published_on', label: 'Publication date', type: 'date', help: 'Optional. Shown on brief covers.' },
      { key: 'theme', label: 'Theme', type: 'select', showIf: (r) => r.kind === 'policy_brief', required: true,
        options: [{ value: 'energy', label: 'Energy' }, { value: 'social', label: 'Social' }, { value: 'economy', label: 'Economy' }] },
      { key: 'cover_scene', label: 'Cover painting', type: 'select', showIf: (r) => r.kind === 'policy_brief',
        options: [{ value: '', label: 'Automatic (by theme)' }, ...SCENES.map((s) => ({ value: s, label: sceneLabel[s] }))],
        help: 'The cover is generated from this painting plus the title. Upload a cover below only to replace it completely.' },
      { key: 'cover', label: 'Own cover image (optional)', type: 'image', folder: 'covers', showIf: (r) => r.kind === 'policy_brief' },
      { key: 'pdf_url', label: 'PDF', type: 'pdf', folder: 'pdf', help: 'Upload the PDF or paste a link (Google Drive etc.).' },
      { key: 'journal_url', label: 'Journal link', type: 'url', showIf: (r) => r.kind === 'research' },
      { key: 'featured', label: 'Highlight', type: 'bool', help: 'Featured on the home page and at the top of lists.' },
      sort, published,
    ],
  },
  {
    key: 'news', label: 'News & Article', singular: 'article',
    order: [{ column: 'date', ascending: false }],
    title: (r) => r.title_en || r.title_id, subtitle: (r) => [fmtDate(r.date), r.place].filter(Boolean).join(' · '),
    defaults: { published: true, date: new Date().toISOString().slice(0, 10), place: 'Bandung' },
    sitePath: (r) => `/news/${r.slug}`,
    fields: [
      { key: 'title_en', label: 'Title (English)', type: 'textarea', pair: 'title', help: 'At least one title is required.' },
      { key: 'title_id', label: 'Title (Bahasa Indonesia)', type: 'textarea', pair: 'title' },
      { key: 'slug', label: 'Web address', type: 'slug', required: true, from: ['title_en', 'title_id'] },
      { key: 'date', label: 'Date', type: 'date', required: true },
      { key: 'place', label: 'Place', type: 'text' },
      { key: 'image', label: 'Main photo', type: 'image', folder: 'news', help: 'Landscape works best (16:9 or 3:2).' },
      { key: 'tagline_en', label: 'Tagline (English)', type: 'text', pair: 'tagline' },
      { key: 'tagline_id', label: 'Tagline (Bahasa Indonesia)', type: 'text', pair: 'tagline' },
      { key: 'summary_en', label: 'Summary (English)', type: 'textarea', pair: 'summary', help: 'One or two sentences for cards and search results.' },
      { key: 'summary_id', label: 'Summary (Bahasa Indonesia)', type: 'textarea', pair: 'summary' },
      { key: 'body_en', label: 'Article (English)', type: 'longtext', pair: 'body', help: 'Leave an empty line between paragraphs. A YouTube link on its own line becomes a "Watch" button.' },
      { key: 'body_id', label: 'Article (Bahasa Indonesia)', type: 'longtext', pair: 'body' },
      { key: 'source_label', label: 'Source name', type: 'text', help: 'e.g. itb.ac.id, 20 August 2026' },
      { key: 'source_url', label: 'Source link', type: 'url' },
      published,
    ],
  },
  {
    key: 'careers', label: 'Career', singular: 'role',
    order: [{ column: 'sort', ascending: true }],
    title: (r) => r.title_en || r.title_id, subtitle: (r) => (r.is_open ? 'Open' : 'Closed'),
    defaults: { published: true, is_open: true, sort: 100, qualifications_en: [], qualifications_id: [], responsibilities_en: [], responsibilities_id: [], notes_en: [], notes_id: [] },
    sitePath: (r) => `/career/${r.slug}`,
    fields: [
      { key: 'title_en', label: 'Role (English)', type: 'text', pair: 'title' },
      { key: 'title_id', label: 'Role (Bahasa Indonesia)', type: 'text', pair: 'title' },
      { key: 'slug', label: 'Web address', type: 'slug', required: true, from: ['title_en', 'title_id'] },
      { key: 'is_open', label: 'Accepting applications', type: 'bool' },
      { key: 'apply_url', label: 'Application link', type: 'url', help: 'Google Form, s.id link, etc.' },
      { key: 'intro_en', label: 'Introduction (English)', type: 'textarea', pair: 'intro' },
      { key: 'intro_id', label: 'Introduction (Bahasa Indonesia)', type: 'textarea', pair: 'intro' },
      { key: 'responsibilities_en', label: 'Responsibilities (English)', type: 'list', pair: 'resp', help: 'One item per line.' },
      { key: 'responsibilities_id', label: 'Responsibilities (Bahasa Indonesia)', type: 'list', pair: 'resp' },
      { key: 'qualifications_en', label: 'Qualifications (English)', type: 'list', pair: 'qual' },
      { key: 'qualifications_id', label: 'Qualifications (Bahasa Indonesia)', type: 'list', pair: 'qual' },
      { key: 'notes_en', label: 'Good to know (English)', type: 'list', pair: 'notes' },
      { key: 'notes_id', label: 'Good to know (Bahasa Indonesia)', type: 'list', pair: 'notes' },
      { key: 'poster', label: 'Recruitment poster', type: 'image', folder: 'careers' },
      sort, published,
    ],
  },
  {
    key: 'people', label: 'Team', singular: 'person',
    order: [{ column: 'sort', ascending: true }],
    title: (r) => r.name, subtitle: (r) => [r.group === 'leadership' ? 'Leadership' : 'Researcher', r.role_en].filter(Boolean).join(' · '),
    defaults: { group: 'researcher', published: true, sort: 100 },
    sitePath: (r) => `/team/${r.slug}`,
    fields: [
      { key: 'name', label: 'Full name with titles', type: 'text', required: true },
      { key: 'slug', label: 'Web address', type: 'slug', required: true, from: ['name'] },
      { key: 'group', label: 'Group', type: 'select', options: [{ value: 'leadership', label: 'Leadership' }, { value: 'researcher', label: 'Researcher' }] },
      { key: 'role_en', label: 'Role (English)', type: 'text', pair: 'role', help: 'Title Case, e.g. Research Associate' },
      { key: 'role_id', label: 'Role (Bahasa Indonesia)', type: 'text', pair: 'role' },
      { key: 'photo', label: 'Portrait', type: 'image', folder: 'people', help: '4:5 portrait on the IEEF light-horizon background, head at the same size as the others. Send new photos to the web team if they still need the background.' },
      { key: 'bio_en', label: 'Biography (English)', type: 'longtext', pair: 'bio' },
      { key: 'bio_id', label: 'Biography (Bahasa Indonesia)', type: 'longtext', pair: 'bio' },
      { key: 'social_url', label: 'LinkedIn or other profile link', type: 'url' },
      sort, published,
    ],
  },
  {
    key: 'partners', label: 'Partners', singular: 'partner',
    order: [{ column: 'sort', ascending: true }],
    title: (r) => r.name, subtitle: (r) => r.website_url ?? '',
    defaults: { published: true, sort: 100 },
    sitePath: () => '/about-us',
    fields: [
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'logo', label: 'Logo', type: 'image', folder: 'partners', help: 'PNG or SVG with transparent background, trimmed to the logo.' },
      { key: 'website_url', label: 'Website', type: 'url' },
      sort, published,
    ],
  },
];

export const slugify = (s: string) =>
  s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80).replace(/-+$/, '');
