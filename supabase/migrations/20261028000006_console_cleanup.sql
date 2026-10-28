-- pg_net lives in the extensions schema (its functions stay in schema net); the old email-based editors table is replaced by access codes
drop extension if exists pg_net;
create extension pg_net with schema extensions;
drop table if exists public.editors;
drop type if exists public.editor_role;
