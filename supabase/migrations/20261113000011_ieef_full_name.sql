-- Official name, per IEEF: "Institute for Energy, Economics, and Finance" (comma after Economics, "and" not "&").
update public.people set
  bio_en = regexp_replace(bio_en, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g'),
  bio_id = regexp_replace(bio_id, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g')
where bio_en ~ 'Energy, Economics (&|and) Finance' or bio_id ~ 'Energy, Economics (&|and) Finance';

update public.news set
  summary_en = regexp_replace(summary_en, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g'),
  summary_id = regexp_replace(summary_id, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g'),
  body_en = regexp_replace(body_en, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g'),
  body_id = regexp_replace(body_id, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g')
where concat(summary_en, summary_id, body_en, body_id) ~ 'Energy, Economics (&|and) Finance';

update public.careers set
  intro_en = regexp_replace(intro_en, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g'),
  intro_id = regexp_replace(intro_id, 'Energy, Economics (&|and) Finance', 'Energy, Economics, and Finance', 'g')
where concat(intro_en, intro_id) ~ 'Energy, Economics (&|and) Finance';
