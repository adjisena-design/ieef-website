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
  image: { responsiveStyles: true },
});
