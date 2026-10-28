// Preview builds block crawlers; the production build (PUBLIC_INDEXABLE=true) allows them and lists the sitemap.
import type { APIRoute } from 'astro';
export const GET: APIRoute = ({ site }) => {
  const indexable = import.meta.env.PUBLIC_INDEXABLE === 'true';
  const body = indexable
    ? `User-agent: *\nAllow: /\nDisallow: /console\nDisallow: /_import/\n\nSitemap: ${new URL('/sitemap.xml', site)}\n`
    : 'User-agent: *\nDisallow: /\n';
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
