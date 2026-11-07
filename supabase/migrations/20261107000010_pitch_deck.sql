-- Pitch deck: the organization-profile deck shown in its own section on the home page (above "Our network &
-- collaboration"), viewable on the site and downloadable as a PDF.
-- Every uploaded deck is kept as a version. One version is live (featured = true); when none is marked live, the
-- newest published version is shown. Marking a version live switches the previous one off (one_live_deck trigger).
-- pdf holds a path in the public "media" bucket (console uploads) or a site path starting with "/" (the first deck,
-- shipped in public/media/pitch-deck/).

create table public.pitch_decks (
  id           uuid primary key default gen_random_uuid(),
  title        text not null,                      -- version name shown in the console, e.g. "Organization profile, November 2026"
  released_on  date not null default current_date,
  pdf          text not null,
  pages        int check (pages is null or pages between 1 and 300),
  note         text,                               -- internal note, never shown on the website
  featured     boolean not null default false,     -- live on the website
  published    boolean not null default true,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  updated_by   uuid references auth.users (id) on delete set null
);
create trigger pitch_decks_touch before update on public.pitch_decks for each row execute function public.touch_updated();

alter table public.pitch_decks enable row level security;
create policy "public reads published" on public.pitch_decks for select to anon, authenticated using (published or (select private.is_editor()));
create policy "editors insert" on public.pitch_decks for insert to authenticated with check ((select private.is_editor()));
create policy "editors update" on public.pitch_decks for update to authenticated using ((select private.is_editor())) with check ((select private.is_editor()));
create policy "admins delete" on public.pitch_decks for delete to authenticated using ((select private.is_admin()));

create trigger pitch_decks_log after insert or update or delete on public.pitch_decks for each row execute function cms.log_change();

-- one live deck at a time
create or replace function public.one_live_deck() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if new.featured and (tg_op = 'INSERT' or not coalesce(old.featured, false)) then
    update public.pitch_decks set featured = false where featured and id <> new.id;
  end if;
  return new;
end $$;
revoke all on function public.one_live_deck() from public, anon, authenticated;
create trigger pitch_decks_one_live after insert or update of featured on public.pitch_decks for each row when (new.featured) execute function public.one_live_deck();

-- decks are PDFs up to 50 MB (the free-plan maximum); other uploads stay limited to 20 MB in the console
update storage.buckets set file_size_limit = 52428800 where id = 'media';

-- drafts and review accept the new content type
do $$
declare c text;
begin
  select conname into c from pg_constraint
   where conrelid = 'cms.drafts'::regclass and contype = 'c' and pg_get_constraintdef(oid) like '%entity%';
  if c is not null then execute format('alter table cms.drafts drop constraint %I', c); end if;
end $$;
alter table cms.drafts add constraint drafts_entity_check
  check (entity in ('people', 'publications', 'news', 'careers', 'partners', 'pitch_decks'));

create or replace function cms.apply(p_entity text, p_row uuid, p_data jsonb) returns uuid
language plpgsql volatile security definer set search_path = '' as $$
declare cols text[]; list text; v_id uuid;
begin
  if p_entity not in ('people', 'publications', 'news', 'careers', 'partners', 'pitch_decks') then raise exception 'Unknown content type.'; end if;
  select array_agg(k) into cols from jsonb_object_keys(p_data) k where k = any (cms.editable_columns(p_entity));
  if cols is null then raise exception 'Nothing to save.'; end if;
  select string_agg(format('%I', c), ', ') into list from unnest(cols) c;
  if p_row is null then
    execute format('insert into public.%I (%s) select %s from jsonb_populate_record(null::public.%I, $1) returning id', p_entity, list, list, p_entity)
      into v_id using p_data;
  else
    execute format('update public.%I set (%s) = (select %s from jsonb_populate_record(null::public.%I, $1)) where id = $2 returning id', p_entity, list, list, p_entity)
      into v_id using p_data, p_row;
    if v_id is null then raise exception 'The original item no longer exists.'; end if;
  end if;
  return v_id;
end $$;

create or replace function public.console_draft_submit(p_entity text, p_row uuid, p_data jsonb, p_note text default null, p_draft uuid default null) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor', 'contributor']); d cms.drafts;
begin
  if p_entity not in ('people', 'publications', 'news', 'careers', 'partners', 'pitch_decks') then raise exception 'Unknown content type.'; end if;
  if p_draft is not null then
    update cms.drafts set data = p_data, note = p_note, created_at = now()
     where id = p_draft and created_by = st.id and status = 'pending' returning * into d;
    if d.id is null then raise exception 'This draft can no longer be changed.'; end if;
  else
    insert into cms.drafts (entity, row_id, data, note, created_by) values (p_entity, p_row, p_data, p_note, st.id) returning * into d;
  end if;
  insert into cms.log (staff_id, action, entity, entity_id, detail)
  values (st.id, 'draft_submitted', p_entity, coalesce(p_row::text, d.id::text),
          jsonb_build_object('label', coalesce(p_data->>'title_en', p_data->>'title', p_data->>'name', p_data->>'title_id')));
  return jsonb_build_object('ok', true, 'id', d.id);
end $$;

-- the Publish card counts deck changes as unpublished changes too
create or replace function public.console_publish_status() returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor', 'contributor']); last cms.publishes;
begin
  select * into last from cms.publishes order by at desc limit 1;
  return jsonb_build_object(
    'configured', exists (select 1 from cms.settings where key = 'deploy_hook_url' and value like 'https://%'),
    'abort_configured', exists (select 1 from cms.settings where key = 'cf_api_token' and length(value) > 20),
    'last_at', last.at, 'last_by', (select name from cms.staff where id = last.staff_id),
    'cancelled_at', last.cancelled_at, 'cancelled_by', (select name from cms.staff where id = last.cancelled_by),
    'last_response', (select jsonb_build_object('status', r.status_code, 'error', r.error_msg)
                        from net._http_response r where r.id = last.request_id),
    'pending_changes', (select count(*) from cms.log l
                         where l.entity in ('people', 'publications', 'news', 'careers', 'partners', 'pitch_decks')
                           and l.action in ('insert', 'update', 'delete')
                           and l.at > coalesce((select max(at) from cms.publishes where cancelled_at is null), '-infinity'::timestamptz)),
    'pending_drafts', (select count(*) from cms.drafts where status = 'pending'));
end $$;

-- the first deck (November 2026), shipped with the site
insert into public.pitch_decks (title, released_on, pdf, pages, featured, note)
values ('Organization profile, November 2026', '2026-11-07', '/media/pitch-deck/ieef-organization-profile-2026-11.pdf', 34, true,
        'First deck in the new design, rebuilt from the 2026 Canva deck.');
