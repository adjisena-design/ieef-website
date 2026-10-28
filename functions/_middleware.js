// Password gate for the team preview (Cloudflare Pages Function).
// Active only when the PREVIEW_PASSWORD environment variable is set in Cloudflare.
// Remove that variable (or this file) at public launch.
export async function onRequest({ request, env, next }) {
  const password = env.PREVIEW_PASSWORD;
  if (!password) return next();

  const header = request.headers.get('Authorization') || '';
  const [scheme, encoded] = header.split(' ');
  if (scheme === 'Basic' && encoded) {
    const [, pass] = atob(encoded).split(':');
    if (pass === password) return next();
  }
  return new Response('IEEF website preview — team access only.', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="IEEF preview", charset="UTF-8"' },
  });
}
