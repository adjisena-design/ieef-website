// Resolve an image value from the database:
//   "repo:migrated/people/x.webp"  -> optimised file in src/assets (built by Astro)
//   "people/abc.jpg"               -> file in the public Supabase "media" bucket (console uploads)
import type { ImageMetadata } from 'astro';

const repo = import.meta.glob<{ default: ImageMetadata }>('../assets/**/*.{webp,png,jpg,jpeg}', { eager: true });
const SUPABASE = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;

export function media(value: string | null | undefined): ImageMetadata | string | null {
  if (!value) return null;
  if (value.startsWith('repo:')) {
    const hit = repo[`../assets/${value.slice(5)}`];
    if (!hit) throw new Error(`Missing repo image: ${value}`);
    return hit.default;
  }
  if (/^https?:\/\//.test(value)) return value;
  return SUPABASE ? `${SUPABASE}/storage/v1/object/public/media/${value}` : null;
}
