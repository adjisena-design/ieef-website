# IEEF website

Rebuild of [ieef.or.id](https://ieef.or.id) for the Institute for Energy, Economics & Finance, using the approved **Plan B** design (painted landscape + glass).

- **Stack:** [Astro](https://astro.build) (static HTML, free and open source) · Plus Jakarta Sans · Supabase for content and the team console (from step 2)
- **Languages:** English at `/`, Bahasa Indonesia at `/id/` with an EN/ID toggle on every page
- **Hosting:** Cloudflare Workers (free tier), password-protected preview until launch

## Run locally

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # outputs static site to dist/
```

## Deploy (Cloudflare Workers)

The site deploys as a Cloudflare Worker with static assets (`wrangler.jsonc`). Every push to `main` rebuilds automatically.

| Setting (Worker → Settings → Build) | Value |
|---|---|
| Build command | `npm run build` |
| Deploy command | `npx wrangler deploy` |
| Root directory | `/` |

| Variable (Worker → Settings → Variables and Secrets) | When |
|---|---|
| `PREVIEW_PASSWORD` (type: Secret) | Preview: the team password. Any username works. |
| `PUBLIC_INDEXABLE=true` (build variable) | Launch only, together with deleting `PREVIEW_PASSWORD` |

`worker/index.js` checks the password on every request, then serves the built files from `dist/`. `keep_vars` in `wrangler.jsonc` keeps dashboard variables across deploys.

Test locally: `npm run build && npx wrangler dev --var PREVIEW_PASSWORD:test`

## Project layout

```
src/
  styles/tokens.css     design tokens: brand colours, type scale, glass surfaces
  styles/global.css     base styles, .glass / .glass-dark / .card
  i18n/ui.ts            interface strings (EN/ID), nav, dashboard links, URL helpers
  layouts/Base.astro    page shell: meta, hreflang, noindex for preview, nav, footer
  components/           Nav, Footer, Button, Icon, Sparkline, ComingSoon
  components/home/      homepage
  data/home.ts          homepage content (moves to Supabase in step 2)
  assets/art/           original painted artwork (generated for IEEF)
  assets/brand/         IEEF logo (colour + white)
worker/index.js         preview password gate + static file server
wrangler.jsonc          Cloudflare deploy config
```

URLs keep the current site's slugs (`/about-us`, `/policy-brief`, `/research-publication`, `/news-and-article`, `/career`, `/contact-us`, `/dashboard`) so existing links keep working.

## Design rules (Plan B)

- Brand colours come from the logo and do not change: navy `#083868`, teal `#189080`, mint `#78C0B8`, sky `#5898C0`.
- Painted art carries heroes, section breaks and publication covers. Glass sits only behind text and data: paper glass on light art, navy glass on dark art.
- Warm `#EC9A4C` is reserved for the primary call to action and the sun.
- Policy-brief series colours: energy & finance teal, social policy dawn `#B4602A`, regional economy dusk `#2D4AA0`.
- Art ships as WebP at several widths (AVIF tested larger on the grainy texture).

## Roadmap

| Step | Scope | Status |
|---|---|---|
| 1 | Foundation: repo, design system, layout, nav/footer, EN/ID routing, homepage, preview pipeline | Done |
| 2 | Content export from the old site into Supabase (text, PDFs, team photos, partner logos); database and storage setup | Next |
| 3 | About Us and 14 team profiles | |
| 4 | Publications: policy briefs (10 new cover thumbnails), research list with year/topic filters | |
| 5 | News & Article (16 press releases, 3 articles), Career (4 roles), Contact (form saved to Supabase) | |
| 6 | Team console: login for a small team to add news, briefs and photos from the browser | |
| 7 | Bahasa Indonesia review, performance, SEO, redirects, accessibility | |
| 8 | Team review on the preview link, launch checklist, domain switch (on approval) | |

Old Hostinger template pages (`/wool-sweater-…`, `/face-serum-…` and similar) are intentionally not rebuilt.
