-- Move the access-check helpers out of the public API (no /rest/v1/rpc/ endpoint for them).
-- Policies reference functions by id, so they keep working after the move.
create schema if not exists private;
grant usage on schema private to anon, authenticated;
alter function public.is_editor() set schema private;
alter function public.is_admin() set schema private;
revoke execute on function private.is_editor(), private.is_admin() from public;
grant execute on function private.is_editor(), private.is_admin() to anon, authenticated;

-- the http extension was only needed for the one-time content import
drop extension if exists http;
