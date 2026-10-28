// Sitemap of every public page in both languages, with hreflang pairs.
import type { APIRoute } from 'astro';
import { getNews, getCareers, getPeople } from '../lib/content';

export const GET: APIRoute = async ({ site }) => {
  const [news, careers, people] = await Promise.all([getNews(), getCareers(), getPeople()]);
  const pages: { path: string; lastmod?: string }[] = [
    ...['/', '/about-us', '/publication', '/policy-brief', '/research-publication', '/dashboard', '/news-and-article', '/career', '/contact-us'].map((path) => ({ path })),
    ...news.map((n) => ({ path: `/news/${n.slug}`, lastmod: n.date })),
    ...careers.map((c) => ({ path: `/career/${c.slug}` })),
    ...people.map((p) => ({ path: `/team/${p.slug}` })),
  ];
  const url = (p: string) => new URL(p, site).toString();
  const idPath = (p: string) => (p === '/' ? '/id' : `/id${p}`);
  const entry = (loc: string, p: string, lastmod?: string) => `  <url>
    <loc>${loc}</loc>${lastmod ? `\n    <lastmod>${lastmod}</lastmod>` : ''}
    <xhtml:link rel="alternate" hreflang="en" href="${url(p)}"/>
    <xhtml:link rel="alternate" hreflang="id" href="${url(idPath(p))}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${url(p)}"/>
  </url>`;
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${pages.flatMap(({ path, lastmod }) => [entry(url(path), path, lastmod), entry(url(idPath(path)), path, lastmod)]).join('\n')}
</urlset>`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
