-- Abort a rebuild started from the console. Cancelling goes through the cancel-build edge function
-- (supabase/functions/cancel-build), which checks the caller's code, reads the Cloudflare API token with the
-- service role, and calls PUT /accounts/{id}/builds/builds/{uuid}/cancel.
alter table cms.publishes add column if not exists cancelled_at timestamptz,
  add column if not exists cancelled_by uuid references cms.staff (id) on delete set null,
  add column if not exists cancel_result jsonb;
insert into cms.settings (key, value) values ('cf_account_id', '44eaf7d2c52d1f7b4d9edbb1f834a6d5') on conflict (key) do nothing;

-- console_publish_status / console_publish: aborted rebuilds no longer count as published and do not block a new publish
-- console_abort_info(): editor+; latest publish within 30 min, not aborted; returns build_uuid from the deploy hook response
-- console_abort_log(p_publish, p_result): editor+; marks the publish aborted and logs it
-- console_set_cf_token(p_token): owner only; stores the Cloudflare API token in cms.settings
-- console_cf_credentials(): service_role only (edge function); never executable by browsers
-- Full definitions as applied: see migration "console_abort_publish" in the Supabase project history.
