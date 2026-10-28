-- Painted cover scene for policy briefs (picked in the console; empty = theme default).
alter table public.publications add column cover_scene text
  check (cover_scene in ('solar', 'school', 'city', 'port', 'offshore-wind', 'grid', 'rec-singapore', 'ev-road', 'ev-city', 'hydro-village'));

update public.publications p set cover_scene = v.scene from (values
  ('mapping-the-missing-link', 'solar'),
  ('mapping-the-evidence-before-scaling-the-program', 'school'),
  ('when-growth-is-not-enough', 'city'),
  ('making-strategic-exports-work-for-indonesia', 'port'),
  ('bridging-the-research-divide', 'offshore-wind'),
  ('strengthening-indonesias-path-to-8-growth', 'grid'),
  ('from-fragmentation-to-credibility', 'rec-singapore'),
  ('understanding-indonesias-electric-vehicle-adoption-gap', 'ev-road'),
  ('electric-vehicle-adoption-in-indonesia', 'ev-city'),
  ('mega-conversion-lpg-to-induction-stove', 'hydro-village')
) as v(slug, scene) where p.slug = v.slug;
