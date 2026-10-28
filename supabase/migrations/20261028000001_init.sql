-- IEEF website: content schema, team-console access and storage.
-- Bilingual text uses paired *_en / *_id columns. The site falls back to the other language when one is empty.
-- Image columns hold either "repo:<path>" (optimised file in src/assets) or a path in the public "media" bucket.

-- ---------------------------------------------------------------- types
create type public.person_group as enum ('leadership', 'researcher');
create type public.publication_kind as enum ('policy_brief', 'research');
create type public.brief_theme as enum ('energy', 'social', 'economy');
create type public.editor_role as enum ('admin', 'editor');
create type public.message_status as enum ('new', 'read', 'archived');

-- ---------------------------------------------------------------- console users
-- A person can sign in to the console only if an admin has added them here.
create table public.editors (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  email      text not null unique,
  name       text,
  role       public.editor_role not null default 'editor',
  created_at timestamptz not null default now()
);

create function public.is_editor() returns boolean
language sql stable security definer set search_path = ''
as $$ select exists (select 1 from public.editors where user_id = (select auth.uid())) $$;

create function public.is_admin() returns boolean
language sql stable security definer set search_path = ''
as $$ select exists (select 1 from public.editors where user_id = (select auth.uid()) and role = 'admin') $$;

-- ---------------------------------------------------------------- shared trigger
create function public.touch_updated() returns trigger
language plpgsql set search_path = ''
as $$
begin
  new.updated_at := now();
  new.updated_by := (select auth.uid());
  return new;
end $$;

-- ---------------------------------------------------------------- people (About Us + profile pages)
create table public.people (
  id          uuid primary key default gen_random_uuid(),
  slug        text not null unique check (slug ~ '^[a-z0-9-]+$'),
  name        text not null,
  "group"     public.person_group not null default 'researcher',
  role_en     text,
  role_id     text,
  bio_en      text,
  bio_id      text,
  photo       text,
  social_url  text,
  sort        int not null default 100,
  published   boolean not null default true,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  updated_by  uuid references auth.users (id) on delete set null
);

-- ---------------------------------------------------------------- publications (policy briefs + research)
create table public.publications (
  id            uuid primary key default gen_random_uuid(),
  kind          public.publication_kind not null,
  slug          text not null unique check (slug ~ '^[a-z0-9-]+$'),
  title         text not null,              -- kept in the language it was published in
  summary_en    text,
  summary_id    text,
  year          int check (year between 1990 and 2100),
  published_on  date,
  theme         public.brief_theme,         -- policy briefs: colour series of the generated cover
  pdf_url       text,                       -- Google Drive link or uploaded file in "media"
  journal_url   text,
  cover         text,                       -- optional uploaded thumbnail; empty = generated painted cover
  featured      boolean not null default false,
  sort          int not null default 100,
  published     boolean not null default true,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  updated_by    uuid references auth.users (id) on delete set null,
  constraint brief_has_theme check (kind <> 'policy_brief' or theme is not null)
);
create index publications_kind_idx on public.publications (kind, published, year desc, sort);

-- ---------------------------------------------------------------- news (press releases)
create table public.news (
  id            uuid primary key default gen_random_uuid(),
  slug          text not null unique check (slug ~ '^[a-z0-9-]+$'),
  date          date not null,
  place         text,
  title_en      text,
  title_id      text,
  tagline_en    text,
  tagline_id    text,
  summary_en    text,
  summary_id    text,
  body_en       text,                       -- paragraphs separated by a blank line
  body_id       text,
  image         text,
  source_label  text,
  source_url    text,
  published     boolean not null default true,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  updated_by    uuid references auth.users (id) on delete set null,
  constraint news_has_title check (coalesce(title_en, title_id) is not null)
);
create index news_date_idx on public.news (published, date desc);

-- ---------------------------------------------------------------- careers
create table public.careers (
  id                  uuid primary key default gen_random_uuid(),
  slug                text not null unique check (slug ~ '^[a-z0-9-]+$'),
  title_en            text,
  title_id            text,
  intro_en            text,
  intro_id            text,
  qualifications_en   text[] not null default '{}',
  qualifications_id   text[] not null default '{}',
  responsibilities_en text[] not null default '{}',
  responsibilities_id text[] not null default '{}',
  notes_en            text[] not null default '{}',
  notes_id            text[] not null default '{}',
  apply_url           text,
  poster              text,
  is_open             boolean not null default true,
  sort                int not null default 100,
  published           boolean not null default true,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),
  updated_by          uuid references auth.users (id) on delete set null
);

-- ---------------------------------------------------------------- partners
create table public.partners (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  logo         text,
  website_url  text,
  sort         int not null default 100,
  published    boolean not null default true,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  updated_by   uuid references auth.users (id) on delete set null
);

-- ---------------------------------------------------------------- contact form
create table public.contact_messages (
  id            uuid primary key default gen_random_uuid(),
  name          text not null check (char_length(name) between 1 and 120),
  email         text not null check (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$' and char_length(email) <= 200),
  organization  text check (char_length(organization) <= 200),
  subject       text check (char_length(subject) <= 200),
  message       text not null check (char_length(message) between 5 and 5000),
  status        public.message_status not null default 'new',
  created_at    timestamptz not null default now()
);

-- ---------------------------------------------------------------- triggers
create trigger people_touch before update on public.people for each row execute function public.touch_updated();
create trigger publications_touch before update on public.publications for each row execute function public.touch_updated();
create trigger news_touch before update on public.news for each row execute function public.touch_updated();
create trigger careers_touch before update on public.careers for each row execute function public.touch_updated();
create trigger partners_touch before update on public.partners for each row execute function public.touch_updated();

-- ---------------------------------------------------------------- row level security
alter table public.editors enable row level security;
alter table public.people enable row level security;
alter table public.publications enable row level security;
alter table public.news enable row level security;
alter table public.careers enable row level security;
alter table public.partners enable row level security;
alter table public.contact_messages enable row level security;

-- editors: each signed-in editor sees their own row; admins manage the list
create policy "editors read own or admin" on public.editors for select to authenticated
  using (user_id = (select auth.uid()) or (select public.is_admin()));
create policy "admins insert editors" on public.editors for insert to authenticated with check ((select public.is_admin()));
create policy "admins update editors" on public.editors for update to authenticated using ((select public.is_admin()));
create policy "admins delete editors" on public.editors for delete to authenticated using ((select public.is_admin()));

-- content tables: the public reads published rows; editors read and change everything
do $$
declare t text;
begin
  foreach t in array array['people', 'publications', 'news', 'careers', 'partners'] loop
    execute format('create policy "public reads published" on public.%I for select to anon, authenticated using (published or (select public.is_editor()))', t);
    execute format('create policy "editors insert" on public.%I for insert to authenticated with check ((select public.is_editor()))', t);
    execute format('create policy "editors update" on public.%I for update to authenticated using ((select public.is_editor())) with check ((select public.is_editor()))', t);
    execute format('create policy "editors delete" on public.%I for delete to authenticated using ((select public.is_editor()))', t);
  end loop;
end $$;

-- contact form: anyone may send; only editors read and triage
create policy "anyone sends a message" on public.contact_messages for insert to anon, authenticated with check (status = 'new');
create policy "editors read messages" on public.contact_messages for select to authenticated using ((select public.is_editor()));
create policy "editors update messages" on public.contact_messages for update to authenticated using ((select public.is_editor()));
create policy "admins delete messages" on public.contact_messages for delete to authenticated using ((select public.is_admin()));

-- ---------------------------------------------------------------- storage: one public bucket for console uploads
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('media', 'media', true, 20971520,
        array['image/jpeg', 'image/png', 'image/webp', 'image/avif', 'application/pdf'])
on conflict (id) do nothing;

-- public files are served by URL without a policy; listing is for editors only
create policy "editors list media" on storage.objects for select to authenticated
  using (bucket_id = 'media' and (select public.is_editor()));
create policy "editors upload media" on storage.objects for insert to authenticated
  with check (bucket_id = 'media' and (select public.is_editor()));
create policy "editors update media" on storage.objects for update to authenticated
  using (bucket_id = 'media' and (select public.is_editor()));
create policy "editors delete media" on storage.objects for delete to authenticated
  using (bucket_id = 'media' and (select public.is_editor()));
