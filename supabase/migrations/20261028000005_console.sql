-- =====================================================================
--  Team console: access codes (like the Jabar Open panitia console)
--   owner       : everything, manages admin codes; cannot be revoked
--   admin       : everything, manages editor / contributor codes, deletes content
--   editor      : creates and edits content, reads messages, approves drafts, publishes
--   contributor : submits drafts and suggested edits for review
--  A browser gets an anonymous Supabase session; entering a code links that session
--  to a staff row for 12 hours. Content tables keep using RLS through private.is_editor().
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;
create extension if not exists pg_net;
create schema if not exists cms;
revoke all on schema cms from public, anon, authenticated;

create table cms.staff (
  id            uuid primary key default gen_random_uuid(),
  name          text not null check (char_length(name) between 2 and 80),
  role          text not null check (role in ('owner', 'admin', 'editor', 'contributor')),
  code_hash     text not null unique,
  code_hint     text,
  active        boolean not null default true,
  note          text,
  created_at    timestamptz not null default now(),
  created_by    uuid references cms.staff (id) on delete set null,
  last_login_at timestamptz
);
create unique index staff_one_owner on cms.staff ((true)) where role = 'owner';

create table cms.sessions (
  uid        uuid primary key,
  staff_id   uuid not null references cms.staff (id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null
);

create table cms.login_attempts (
  id bigserial primary key, uid uuid, at timestamptz not null default now(), ok boolean not null
);

create table cms.log (
  id        bigserial primary key,
  at        timestamptz not null default now(),
  staff_id  uuid references cms.staff (id) on delete set null,
  action    text not null,
  entity    text,
  entity_id text,
  detail    jsonb not null default '{}'::jsonb
);
create index log_at_idx on cms.log (at desc);

create table cms.drafts (
  id          uuid primary key default gen_random_uuid(),
  entity      text not null check (entity in ('people', 'publications', 'news', 'careers', 'partners')),
  row_id      uuid,                                  -- null = new item
  data        jsonb not null,
  status      text not null default 'pending' check (status in ('pending', 'approved', 'rejected', 'withdrawn')),
  note        text,
  created_by  uuid references cms.staff (id) on delete set null,
  created_at  timestamptz not null default now(),
  reviewed_by uuid references cms.staff (id) on delete set null,
  reviewed_at timestamptz,
  review_note text
);

create table cms.settings (key text primary key, value text);

create table cms.publishes (
  id         bigserial primary key,
  at         timestamptz not null default now(),
  staff_id   uuid references cms.staff (id) on delete set null,
  request_id bigint,
  note       text
);

-- ---------------------------------------------------------------- helpers (not exposed)
create or replace function cms.rand_code(n int) returns text
language plpgsql volatile set search_path = '' as $$
declare a text := '23456789ABCDEFGHJKMNPQRSTUVWXYZ'; b bytea := extensions.gen_random_bytes(n); r text := ''; i int;
begin
  for i in 0..n - 1 loop r := r || substr(a, (get_byte(b, i) % length(a)) + 1, 1); end loop;
  return r;
end $$;
create or replace function cms.new_code() returns text language sql volatile set search_path = '' as
  $$ select 'IEEF-' || cms.rand_code(4) || '-' || cms.rand_code(4) $$;
create or replace function cms.norm(t text) returns text language sql immutable set search_path = '' as
  $$ select regexp_replace(upper(coalesce(t, '')), '[^A-Z0-9]', '', 'g') $$;
create or replace function cms.hash(t text) returns text language sql immutable set search_path = '' as
  $$ select encode(extensions.digest(cms.norm(t), 'sha256'), 'hex') $$;

create or replace function cms.current_staff() returns cms.staff
language sql stable security definer set search_path = '' as $$
  select s.* from cms.staff s join cms.sessions ss on ss.staff_id = s.id
   where ss.uid = auth.uid() and ss.expires_at > now() and s.active limit 1
$$;

create or replace function cms.require(p_roles text[]) returns cms.staff
language plpgsql stable security definer set search_path = '' as $$
declare st cms.staff;
begin
  select * into st from cms.current_staff();
  if st.id is null then
    raise exception 'Your session has ended. Enter your access code again.' using hint = 'ERR_SESSION', errcode = '28000';
  end if;
  if not (st.role = any (p_roles)) then
    raise exception 'Your access code does not allow this action.' using hint = 'ERR_FORBIDDEN', errcode = '42501';
  end if;
  return st;
end $$;

create or replace function cms.staff_json(s cms.staff) returns jsonb language sql stable set search_path = '' as $$
  select jsonb_build_object('id', s.id, 'name', s.name, 'role', s.role, 'code_hint', s.code_hint, 'active', s.active,
    'note', s.note, 'created_at', s.created_at, 'last_login_at', s.last_login_at,
    'created_by_name', (select name from cms.staff c where c.id = s.created_by))
$$;

create or replace function cms.write_log(p_action text, p_entity text, p_id text, p_detail jsonb default '{}'::jsonb)
returns void language sql volatile security definer set search_path = '' as $$
  insert into cms.log (staff_id, action, entity, entity_id, detail)
  values ((select id from cms.current_staff()), p_action, p_entity, p_id, coalesce(p_detail, '{}'::jsonb))
$$;

-- RLS helpers now follow the access-code session (functions keep their oid, so policies keep working)
create or replace function private.is_editor() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from cms.staff s join cms.sessions ss on ss.staff_id = s.id
                  where ss.uid = (select auth.uid()) and ss.expires_at > now() and s.active
                    and s.role in ('owner', 'admin', 'editor'))
$$;
create or replace function private.is_admin() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from cms.staff s join cms.sessions ss on ss.staff_id = s.id
                  where ss.uid = (select auth.uid()) and ss.expires_at > now() and s.active
                    and s.role in ('owner', 'admin'))
$$;
create or replace function private.is_staff() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from cms.staff s join cms.sessions ss on ss.staff_id = s.id
                  where ss.uid = (select auth.uid()) and ss.expires_at > now() and s.active)
$$;
revoke execute on function private.is_staff() from public;
grant execute on function private.is_staff() to anon, authenticated;

-- deleting content is for admins; editors unpublish instead
do $$
declare t text;
begin
  foreach t in array array['people', 'publications', 'news', 'careers', 'partners'] loop
    execute format('drop policy if exists "editors delete" on public.%I', t);
    execute format('create policy "admins delete" on public.%I for delete to authenticated using ((select private.is_admin()))', t);
  end loop;
end $$;

-- every content change lands in the activity log with the code holder's name
create or replace function cms.log_change() returns trigger
language plpgsql security definer set search_path = '' as $$
declare r jsonb := to_jsonb(coalesce(new, old));
begin
  insert into cms.log (staff_id, action, entity, entity_id, detail)
  values ((select id from cms.current_staff()), lower(tg_op), tg_table_name, r->>'id',
          jsonb_build_object('label', coalesce(r->>'title_en', r->>'title', r->>'name', r->>'title_id', r->>'slug'),
                             'published', r->'published'));
  return null;
end $$;
do $$
declare t text;
begin
  foreach t in array array['people', 'publications', 'news', 'careers', 'partners'] loop
    execute format('create trigger %I after insert or update or delete on public.%I for each row execute function cms.log_change()', t || '_log', t);
  end loop;
end $$;

-- storage: any signed-in code holder may upload to the public media bucket (contributors too, for drafts)
drop policy if exists "editors upload media" on storage.objects;
create policy "staff upload media" on storage.objects for insert to authenticated
  with check (bucket_id = 'media' and (select private.is_staff()));
drop policy if exists "editors list media" on storage.objects;
create policy "staff list media" on storage.objects for select to authenticated
  using (bucket_id = 'media' and (select private.is_staff()));

-- ---------------------------------------------------------------- sign in / out
create or replace function public.console_login(p_code text) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare v_uid uuid := auth.uid(); st cms.staff; v_fail int;
begin
  if v_uid is null then raise exception 'Browser session not ready. Reload the page.' using hint = 'ERR_SESSION'; end if;
  select count(*) into v_fail from cms.login_attempts where uid = v_uid and not ok and at > now() - interval '15 minutes';
  if v_fail >= 8 then
    return jsonb_build_object('ok', false, 'message', 'Too many wrong attempts. Wait 15 minutes and try again.');
  end if;
  select * into st from cms.staff where code_hash = cms.hash(p_code) and active;
  if st.id is null then
    insert into cms.login_attempts (uid, ok) values (v_uid, false);
    return jsonb_build_object('ok', false, 'message', 'This access code is not recognised or has been revoked.');
  end if;
  insert into cms.login_attempts (uid, ok) values (v_uid, true);
  insert into cms.sessions (uid, staff_id, expires_at) values (v_uid, st.id, now() + interval '12 hours')
  on conflict (uid) do update set staff_id = excluded.staff_id, created_at = now(), expires_at = excluded.expires_at;
  update cms.staff set last_login_at = now() where id = st.id;
  insert into cms.log (staff_id, action, entity, entity_id) values (st.id, 'sign_in', 'staff', st.id::text);
  return jsonb_build_object('ok', true, 'staff', cms.staff_json(st));
end $$;

create or replace function public.console_me() returns jsonb
language sql stable security definer set search_path = '' as $$
  select case when s.id is null then null else cms.staff_json(s) end from cms.current_staff() s
$$;

create or replace function public.console_logout() returns jsonb
language sql volatile security definer set search_path = '' as $$
  delete from cms.sessions where uid = auth.uid();
  select jsonb_build_object('ok', true);
$$;

-- ---------------------------------------------------------------- access codes
create or replace function public.console_staff_list() returns jsonb
language plpgsql stable security definer set search_path = '' as $$
begin
  perform cms.require(array['owner', 'admin']);
  return (select coalesce(jsonb_agg(cms.staff_json(s) order by array_position(array['owner', 'admin', 'editor', 'contributor'], s.role),
          not s.active, s.name), '[]'::jsonb) from cms.staff s);
end $$;

create or replace function public.console_staff_create(p jsonb) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin']); v_role text := p->>'role'; v_code text; x cms.staff;
begin
  if v_role not in ('admin', 'editor', 'contributor') then raise exception 'Unknown role.'; end if;
  if v_role = 'admin' and st.role <> 'owner' then raise exception 'Only the owner can create admin codes.'; end if;
  if char_length(trim(coalesce(p->>'name', ''))) < 2 then raise exception 'Enter the name of the person who will hold this code.'; end if;
  v_code := cms.new_code();
  insert into cms.staff (name, role, code_hash, code_hint, note, created_by)
  values (trim(p->>'name'), v_role, cms.hash(v_code), right(v_code, 4), nullif(trim(coalesce(p->>'note', '')), ''), st.id)
  returning * into x;
  insert into cms.log (staff_id, action, entity, entity_id, detail) values (st.id, 'code_created', 'staff', x.id::text, jsonb_build_object('label', x.name, 'role', x.role));
  return jsonb_build_object('staff', cms.staff_json(x), 'code', v_code);
end $$;

create or replace function public.console_staff_update(p_id uuid, p jsonb) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin']); x cms.staff; v_role text;
begin
  select * into x from cms.staff where id = p_id for update;
  if x.id is null then raise exception 'Code not found.'; end if;
  if x.role = 'owner' and (p ? 'active' or p ? 'role') then raise exception 'The owner code cannot be revoked or changed.'; end if;
  if x.role = 'owner' and st.role <> 'owner' then raise exception 'Only the owner can edit the owner code.'; end if;
  if x.role = 'admin' and st.role <> 'owner' then raise exception 'Only the owner can change admin codes.'; end if;
  v_role := coalesce(p->>'role', x.role);
  if v_role not in ('owner', 'admin', 'editor', 'contributor') or (v_role = 'owner' and x.role <> 'owner') then raise exception 'Unknown role.'; end if;
  if v_role = 'admin' and x.role <> 'admin' and st.role <> 'owner' then raise exception 'Only the owner can give admin access.'; end if;
  update cms.staff set
    name = coalesce(nullif(trim(p->>'name'), ''), name),
    role = v_role,
    active = coalesce((p->>'active')::boolean, active),
    note = case when p ? 'note' then nullif(trim(p->>'note'), '') else note end
  where id = x.id;
  if coalesce((p->>'active')::boolean, true) = false then delete from cms.sessions where staff_id = x.id; end if;
  insert into cms.log (staff_id, action, entity, entity_id, detail)
  values (st.id, case when (p->>'active') = 'false' then 'code_revoked' when (p->>'active') = 'true' then 'code_reinstated' else 'code_edited' end,
          'staff', x.id::text, p || jsonb_build_object('label', x.name));
  return public.console_staff_list();
end $$;

create or replace function public.console_staff_new_code(p_id uuid) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin']); x cms.staff; v_code text;
begin
  select * into x from cms.staff where id = p_id for update;
  if x.id is null then raise exception 'Code not found.'; end if;
  if x.role in ('owner', 'admin') and st.role <> 'owner' and x.id <> st.id then raise exception 'Only the owner can replace this code.'; end if;
  v_code := cms.new_code();
  update cms.staff set code_hash = cms.hash(v_code), code_hint = right(v_code, 4) where id = x.id returning * into x;
  delete from cms.sessions where staff_id = x.id and uid <> auth.uid();
  insert into cms.log (staff_id, action, entity, entity_id, detail) values (st.id, 'code_replaced', 'staff', x.id::text, jsonb_build_object('label', x.name));
  return jsonb_build_object('staff', cms.staff_json(x), 'code', v_code);
end $$;

create or replace function public.console_staff_delete(p_id uuid) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin']); x cms.staff;
begin
  select * into x from cms.staff where id = p_id for update;
  if x.id is null then raise exception 'Code not found.'; end if;
  if x.role = 'owner' or x.id = st.id then raise exception 'This code cannot be deleted.'; end if;
  if x.role = 'admin' and st.role <> 'owner' then raise exception 'Only the owner can delete admin codes.'; end if;
  if x.active then raise exception 'Revoke the code first, then delete it.'; end if;
  delete from cms.staff where id = x.id;
  insert into cms.log (staff_id, action, entity, entity_id, detail) values (st.id, 'code_deleted', 'staff', x.id::text, jsonb_build_object('label', x.name));
  return public.console_staff_list();
end $$;

-- ---------------------------------------------------------------- drafts (contributors) and review
create or replace function cms.editable_columns(p_entity text) returns text[]
language sql stable set search_path = '' as $$
  select array_agg(column_name::text) from information_schema.columns
   where table_schema = 'public' and table_name = p_entity
     and column_name not in ('id', 'created_at', 'updated_at', 'updated_by', 'legacy_slug')
$$;

create or replace function cms.apply(p_entity text, p_row uuid, p_data jsonb) returns uuid
language plpgsql volatile security definer set search_path = '' as $$
declare cols text[]; list text; v_id uuid;
begin
  if p_entity not in ('people', 'publications', 'news', 'careers', 'partners') then raise exception 'Unknown content type.'; end if;
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
  if p_entity not in ('people', 'publications', 'news', 'careers', 'partners') then raise exception 'Unknown content type.'; end if;
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

create or replace function public.console_drafts(p_status text default 'pending') returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor', 'contributor']);
begin
  return (select coalesce(jsonb_agg(jsonb_build_object('id', d.id, 'entity', d.entity, 'row_id', d.row_id, 'data', d.data,
      'status', d.status, 'note', d.note, 'created_at', d.created_at, 'review_note', d.review_note, 'reviewed_at', d.reviewed_at,
      'created_by', d.created_by, 'created_by_name', (select name from cms.staff where id = d.created_by),
      'reviewed_by_name', (select name from cms.staff where id = d.reviewed_by)) order by d.created_at desc), '[]'::jsonb)
    from cms.drafts d
    where (p_status = 'all' or d.status = p_status)
      and (st.role <> 'contributor' or d.created_by = st.id));
end $$;

create or replace function public.console_draft_review(p_id uuid, p_decision text, p_note text default null, p_data jsonb default null) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor']); d cms.drafts; v_id uuid;
begin
  select * into d from cms.drafts where id = p_id for update;
  if d.id is null or d.status <> 'pending' then raise exception 'This draft has already been handled.'; end if;
  if p_decision = 'approve' then
    v_id := cms.apply(d.entity, d.row_id, coalesce(p_data, d.data));
  elsif p_decision <> 'reject' then raise exception 'Unknown decision.';
  end if;
  update cms.drafts set status = case when p_decision = 'approve' then 'approved' else 'rejected' end,
    reviewed_by = st.id, reviewed_at = now(), review_note = p_note, data = coalesce(p_data, data) where id = d.id;
  insert into cms.log (staff_id, action, entity, entity_id, detail)
  values (st.id, 'draft_' || p_decision || 'd', d.entity, coalesce(v_id, d.row_id)::text,
          jsonb_build_object('label', coalesce(d.data->>'title_en', d.data->>'title', d.data->>'name', d.data->>'title_id')));
  return jsonb_build_object('ok', true, 'id', v_id);
end $$;

create or replace function public.console_draft_withdraw(p_id uuid) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor', 'contributor']);
begin
  update cms.drafts set status = 'withdrawn' where id = p_id and created_by = st.id and status = 'pending';
  return jsonb_build_object('ok', true);
end $$;

-- ---------------------------------------------------------------- publish (rebuild the website)
create or replace function public.console_publish_status() returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor', 'contributor']); last cms.publishes;
begin
  select * into last from cms.publishes order by at desc limit 1;
  return jsonb_build_object(
    'configured', exists (select 1 from cms.settings where key = 'deploy_hook_url' and value like 'https://%'),
    'last_at', last.at, 'last_by', (select name from cms.staff where id = last.staff_id),
    'last_response', (select jsonb_build_object('status', r.status_code, 'error', r.error_msg)
                        from net._http_response r where r.id = last.request_id),
    'pending_changes', (select count(*) from cms.log l
                         where l.entity in ('people', 'publications', 'news', 'careers', 'partners')
                           and l.action in ('insert', 'update', 'delete') and l.at > coalesce(last.at, '-infinity'::timestamptz)),
    'pending_drafts', (select count(*) from cms.drafts where status = 'pending'));
end $$;

create or replace function public.console_publish(p_note text default null) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner', 'admin', 'editor']); v_url text; v_req bigint; last timestamptz;
begin
  select value into v_url from cms.settings where key = 'deploy_hook_url';
  if v_url is null or v_url not like 'https://api.cloudflare.com/%' then raise exception 'Publishing is not set up yet. Ask the owner to add the deploy hook.'; end if;
  select max(at) into last from cms.publishes;
  if last > now() - interval '2 minutes' then raise exception 'A rebuild was started less than 2 minutes ago. It already includes your changes.'; end if;
  select net.http_post(url := v_url, body := '{}'::jsonb, headers := '{"Content-Type": "application/json"}'::jsonb) into v_req;
  insert into cms.publishes (staff_id, request_id, note) values (st.id, v_req, p_note);
  insert into cms.log (staff_id, action, entity, detail) values (st.id, 'publish', 'site', jsonb_build_object('note', p_note));
  return jsonb_build_object('ok', true, 'at', now());
end $$;

-- owner only: store the Cloudflare deploy hook
create or replace function public.console_set_deploy_hook(p_url text) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare st cms.staff := cms.require(array['owner']);
begin
  if p_url !~ '^https://api\.cloudflare\.com/client/v4/workers/builds/deploy_hooks/[A-Za-z0-9-]+$' then
    raise exception 'That does not look like a Cloudflare deploy hook URL.';
  end if;
  insert into cms.settings (key, value) values ('deploy_hook_url', p_url) on conflict (key) do update set value = excluded.value;
  insert into cms.log (staff_id, action, entity) values (st.id, 'deploy_hook_set', 'site');
  return jsonb_build_object('ok', true);
end $$;

-- ---------------------------------------------------------------- activity log and overview
create or replace function public.console_activity(p_limit int default 100) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
begin
  perform cms.require(array['owner', 'admin', 'editor']);
  return (select coalesce(jsonb_agg(jsonb_build_object('at', l.at, 'action', l.action, 'entity', l.entity, 'entity_id', l.entity_id,
      'detail', l.detail, 'staff', (select name from cms.staff where id = l.staff_id)) order by l.at desc), '[]'::jsonb)
    from (select * from cms.log order by at desc limit least(greatest(p_limit, 1), 500)) l);
end $$;

-- ---------------------------------------------------------------- execute rights
revoke all on all functions in schema cms from public, anon, authenticated;
do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'console\_%' loop
    execute format('revoke all on function %s from public, anon', f);
    execute format('grant execute on function %s to authenticated', f);
  end loop;
end $$;
