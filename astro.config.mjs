// @ts-check
import { defineConfig } from 'astro/config';

// Static site. English at "/", Bahasa Indonesia at "/id/".
export default defineConfig({
  site: 'https://ieef.or.id',
  output: 'static',
  trailingSlash: 'ignore',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'id'],
    routing: { prefixDefaultLocale: false },
  },
  // console uploads live in Supabase Storage; allow Astro to optimise them at build time
  image: { responsiveStyles: true, remotePatterns: [{ protocol: 'https', hostname: '**.supabase.co' }] },
});
