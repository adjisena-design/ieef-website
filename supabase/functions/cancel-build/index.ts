// Cancels the latest Cloudflare Workers build started from the console's Publish button.
// The caller must be signed in to the console with an owner, admin or editor code.
import { createClient } from 'npm:@supabase/supabase-js@2.76.1';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};
const reply = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return reply(405, { error: 'Method not allowed' });
  const url = Deno.env.get('SUPABASE_URL')!;
  const auth = req.headers.get('Authorization') ?? '';
  const asUser = createClient(url, Deno.env.get('SUPABASE_ANON_KEY')!, { global: { headers: { Authorization: auth } } });
  const asService = createClient(url, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);

  // role check + which build to cancel (raises for contributors or expired sessions)
  const info = await asUser.rpc('console_abort_info');
  if (info.error) return reply(403, { error: info.error.message });
  const creds = await asService.rpc('console_cf_credentials');
  const token = creds.data?.token as string | undefined;
  const account = creds.data?.account as string | undefined;
  if (!token || !account) return reply(400, { error: 'Abort is not set up yet. The owner needs to add a Cloudflare API token in Website settings.' });

  const res = await fetch(`https://api.cloudflare.com/client/v4/accounts/${account}/builds/builds/${info.data.build_uuid}/cancel`, {
    method: 'PUT', headers: { Authorization: `Bearer ${token}` },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok || body.success === false) {
    const msg = body?.errors?.[0]?.message ?? `Cloudflare answered ${res.status}`;
    return reply(409, { error: `Could not abort: ${msg}. The rebuild may already be finishing; it only republishes the same saved content.` });
  }
  await asUser.rpc('console_abort_log', { p_publish: info.data.publish_id, p_result: { status: res.status } });
  return reply(200, { ok: true });
});
