// Cloudflare Worker in front of the static site (dist/).
// Team preview: if the PREVIEW_PASSWORD variable is set in Cloudflare, visitors must enter it.
// At public launch, delete PREVIEW_PASSWORD in Cloudflare (Settings -> Variables and Secrets).
export default {
  // Keep the free Supabase project awake: it pauses after 7 days without requests.
  async scheduled(_event, env, ctx) {
    if (!env.PUBLIC_SUPABASE_URL || !env.PUBLIC_SUPABASE_ANON_KEY) return;
    ctx.waitUntil(fetch(`${env.PUBLIC_SUPABASE_URL}/rest/v1/partners?select=name&limit=1`, {
      headers: { apikey: env.PUBLIC_SUPABASE_ANON_KEY },
    }));
  },

  async fetch(request, env) {
    const password = env.PREVIEW_PASSWORD;
    if (password && !isAuthorised(request, password)) {
      return new Response('IEEF website preview - team access only.', {
        status: 401,
        headers: { 'WWW-Authenticate': 'Basic realm="IEEF preview", charset="UTF-8"', 'Cache-Control': 'no-store' },
      });
    }
    return env.ASSETS.fetch(request);
  },
};

function isAuthorised(request, password) {
  const [scheme, encoded] = (request.headers.get('Authorization') || '').split(' ');
  if (scheme !== 'Basic' || !encoded) return false;
  try {
    const decoded = atob(encoded);
    return decoded.slice(decoded.indexOf(':') + 1) === password;
  } catch {
    return false;
  }
}
