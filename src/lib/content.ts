// Content access for every page. Reads Supabase at build time when PUBLIC_SUPABASE_URL and
// PUBLIC_SUPABASE_ANON_KEY are set (Cloudflare build); otherwise reads the snapshot in src/data/snapshot
// (local development, or before the database is connected).
import type { Lang } from '../i18n/ui';
import snapPeople from '../data/snapshot/people.json';
import snapPublications from '../data/snapshot/publications.json';
import snapNews from '../data/snapshot/news.json';
import snapCareers from '../data/snapshot/careers.json';
import snapPartners from '../data/snapshot/partners.json';

export type Person = {
  slug: string; name: string; group: 'leadership' | 'researcher';
  role_en: string | null; role_id: string | null; bio_en: string | null; bio_id: string | null;
  photo: string | null; social_url: string | null; sort: number; published: boolean;
};
export type Publication = {
  kind: 'policy_brief' | 'research'; slug: string; title: string;
  summary_en: string | null; summary_id: string | null; year: number | null; published_on: string | null;
  theme: 'energy' | 'social' | 'economy' | null; pdf_url: string | null; journal_url: string | null;
  cover: string | null; featured: boolean; sort: number; published: boolean;
};
export type News = {
  slug: string; date: string; place: string | null;
  title_en: string | null; title_id: string | null; tagline_en: string | null; tagline_id: string | null;
  summary_en: string | null; summary_id: string | null; body_en: string | null; body_id: string | null;
  image: string | null; source_label: string | null; source_url: string | null; published: boolean;
};
export type Career = {
  slug: string; title_en: string | null; title_id: string | null; intro_en: string | null; intro_id: string | null;
  qualifications_en: string[]; qualifications_id: string[]; responsibilities_en: string[]; responsibilities_id: string[];
  notes_en: string[]; notes_id: string[]; apply_url: string | null; poster: string | null;
  is_open: boolean; sort: number; published: boolean;
};
export type Partner = { name: string; logo: string | null; website_url: string | null; sort: number; published: boolean };

const URL_ = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;
const KEY = import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string | undefined;
export const source: 'supabase' | 'snapshot' = URL_ && KEY ? 'supabase' : 'snapshot';

const cache = new Map<string, Promise<unknown[]>>();
function table<T>(name: string, order: string, snapshot: unknown[]): Promise<T[]> {
  if (!cache.has(name)) {
    cache.set(name, (async () => {
      if (source === 'snapshot') return (snapshot as T[]).filter((r: any) => r.published !== false);
      const res = await fetch(`${URL_}/rest/v1/${name}?select=*&published=is.true&order=${order}`, {
        headers: { apikey: KEY!, Authorization: `Bearer ${KEY}` },
      });
      if (!res.ok) throw new Error(`Supabase ${name}: ${res.status} ${await res.text()}`);
      return res.json();
    })());
  }
  return cache.get(name) as Promise<T[]>;
}

export const getPeople = () => table<Person>('people', 'sort.asc', snapPeople);
export const getPublications = () => table<Publication>('publications', 'sort.asc', snapPublications);
export const getNews = async () =>
  (await table<News>('news', 'date.desc', snapNews)).slice().sort((a, b) => b.date.localeCompare(a.date));
export const getCareers = () => table<Career>('careers', 'sort.asc', snapCareers);
export const getPartners = () => table<Partner>('partners', 'sort.asc', snapPartners);

export async function getBriefs() {
  return (await getPublications()).filter((p) => p.kind === 'policy_brief').sort((a, b) => a.sort - b.sort);
}
export async function getResearch() {
  return (await getPublications()).filter((p) => p.kind === 'research')
    .sort((a, b) => (b.year ?? 0) - (a.year ?? 0) || a.sort - b.sort);
}

/** Pick the field for the current language, falling back to the other language. */
export function pick<T extends Record<string, any>>(row: T, field: string, lang: Lang): any {
  const own = row[`${field}_${lang}`];
  const other = row[`${field}_${lang === 'en' ? 'id' : 'en'}`];
  const empty = (v: unknown) => v == null || v === '' || (Array.isArray(v) && v.length === 0);
  return empty(own) ? other : own;
}

/** Split stored text into paragraphs. */
export const paragraphs = (text: string | null | undefined) =>
  (text ?? '').split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);

export function formatDate(iso: string | null, lang: Lang, style: 'short' | 'long' = 'short') {
  if (!iso) return '';
  return new Date(iso + 'T00:00:00').toLocaleDateString(lang === 'id' ? 'id-ID' : 'en-GB',
    { day: 'numeric', month: style === 'short' ? 'short' : 'long', year: 'numeric' });
}
