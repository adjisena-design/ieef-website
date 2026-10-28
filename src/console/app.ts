// IEEF team console: access-code sign-in, content editing, review, messages, codes, publishing.
import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { ENTITIES, slugify, type Entity, type Field } from './schema';

const root = document.getElementById('console')!;
const URL_ = root.dataset.url!;
const KEY = root.dataset.key!;
const SITE = root.dataset.site || '';
const THUMBS: Record<string, string> = JSON.parse(root.dataset.thumbs || '{}');
const sb: SupabaseClient = createClient(URL_, KEY, { auth: { persistSession: true, storageKey: 'ieef-console', autoRefreshToken: true } });

type Role = 'owner' | 'admin' | 'editor' | 'contributor';
type Staff = { id: string; name: string; role: Role; code_hint: string; active: boolean; note?: string; created_at?: string; last_login_at?: string; created_by_name?: string };
type Row = Record<string, any>;
let me: Staff | null = null;
let current = 'overview';
let pollTimer: number | undefined;

const ROLE_LABEL: Record<Role, string> = { owner: 'Owner', admin: 'Admin', editor: 'Editor', contributor: 'Contributor' };
const ROLE_HELP: Record<string, string> = {
  admin: 'Everything, including managing editor and contributor codes and deleting content.',
  editor: 'Creates and edits content, reads messages, approves drafts and publishes.',
  contributor: 'Writes drafts and suggested edits. An editor or admin reviews them before they go live.',
};
const can = {
  edit: () => !!me && ['owner', 'admin', 'editor'].includes(me.role),
  admin: () => !!me && ['owner', 'admin'].includes(me.role),
  owner: () => me?.role === 'owner',
};

// ---------------------------------------------------------------- DOM helpers
type Child = Node | string | number | null | undefined | false;
function h<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, any> = {}, ...children: (Child | Child[])[]): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === 'value') (el as any).value = v;
    else if (k === 'checked') (el as any).checked = !!v;
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  for (const c of children.flat()) if (c != null && c !== false) el.append(c instanceof Node ? c : String(c));
  return el;
}
const clear = (el: Element) => { while (el.firstChild) el.firstChild.remove(); };
const fmtTime = (iso?: string | null) => iso ? new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '';
const ago = (iso?: string | null) => {
  if (!iso) return '';
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  return fmtTime(iso);
};
const mediaUrl = (v?: string | null) => {
  if (!v) return null;
  if (v.startsWith('repo:')) return THUMBS[v] ?? null;
  if (/^https?:\/\//.test(v)) return v;
  return `${URL_}/storage/v1/object/public/media/${v}`;
};

function toast(msg: string, kind: 'ok' | 'err' | 'info' = 'ok') {
  const t = h('div', { class: `toast ${kind}`, role: 'status' }, msg);
  document.getElementById('toasts')!.append(t);
  setTimeout(() => t.classList.add('out'), kind === 'err' ? 6000 : 3500);
  setTimeout(() => t.remove(), kind === 'err' ? 6500 : 4000);
}

function modal(title: string, body: Node, actions: { label: string; kind?: string; onClick?: () => any }[]) {
  const back = h('div', { class: 'modal-back' });
  const close = () => back.remove();
  const box = h('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true', 'aria-label': title },
    h('h3', {}, title), body,
    h('div', { class: 'modal-actions' }, actions.map((a) => h('button', {
      class: `btn ${a.kind ?? 'ghost'}`, type: 'button',
      onClick: async () => { const r = await a.onClick?.(); if (r !== false) close(); },
    }, a.label))));
  back.append(box);
  back.addEventListener('click', (e) => { if (e.target === back) close(); });
  document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc); } });
  document.body.append(back);
  (box.querySelector('input, textarea, button') as HTMLElement | null)?.focus();
  return close;
}
const confirmBox = (title: string, text: string, label: string, kind = 'danger') =>
  new Promise<boolean>((res) => modal(title, h('p', {}, text), [
    { label: 'Cancel', onClick: () => res(false) }, { label, kind, onClick: () => res(true) }]));

// ---------------------------------------------------------------- API
async function rpc<T = any>(fn: string, args: Record<string, any> = {}): Promise<T> {
  const { data, error } = await sb.rpc(fn, args);
  if (error) {
    if (error.hint === 'ERR_SESSION' || error.code === '28000') { me = null; renderLogin(error.message); }
    throw new Error(error.message);
  }
  return data as T;
}
async function ensureSession() {
  const { data } = await sb.auth.getSession();
  if (data.session) return;
  const res = await sb.auth.signInAnonymously();
  if (res.error) throw new Error('Could not start a secure session: ' + res.error.message);
}
const tableErr = (e: any) => {
  const m = String(e?.message ?? e);
  if (/duplicate key.*slug/i.test(m)) return 'Another item already uses this web address. Change the web address.';
  if (/row-level security/i.test(m)) return 'Your access code does not allow this change, or your session ended. Sign in again.';
  if (/news_has_title/.test(m)) return 'Enter a title in at least one language.';
  if (/brief_has_theme/.test(m)) return 'Choose a theme for the policy brief.';
  return m;
};

// ---------------------------------------------------------------- boot and sign-in
async function boot() {
  try {
    await ensureSession();
    me = await rpc<Staff | null>('console_me');
  } catch (e) { me = null; }
  if (me) renderShell(); else renderLogin();
}

function renderLogin(message?: string) {
  if (pollTimer) clearInterval(pollTimer);
  clear(root);
  const input = h('input', { id: 'code', name: 'code', autocomplete: 'off', autocapitalize: 'characters', spellcheck: 'false', placeholder: 'IEEF-XXXX-XXXX', required: true, 'aria-describedby': 'login-msg' });
  const msg = h('p', { id: 'login-msg', class: 'login-msg', role: 'alert' }, message ?? '');
  const btn = h('button', { class: 'btn primary wide', type: 'submit' }, 'Enter console');
  const form = h('form', { class: 'login card', onSubmit: async (e: Event) => {
    e.preventDefault();
    msg.textContent = ''; btn.disabled = true; btn.textContent = 'Checking...';
    try {
      await ensureSession();
      const r = await rpc<{ ok: boolean; message?: string; staff?: Staff }>('console_login', { p_code: input.value });
      if (!r.ok) { msg.textContent = r.message ?? 'Access code not recognised.'; return; }
      me = r.staff!; current = 'overview'; renderShell();
    } catch (err: any) { msg.textContent = err.message; }
    finally { btn.disabled = false; btn.textContent = 'Enter console'; }
  } },
    h('img', { src: '/favicon.svg', alt: '', class: 'login-logo', width: 56, height: 56 }),
    h('h1', {}, 'IEEF team console'),
    h('p', { class: 'muted' }, 'Enter the access code you received from an IEEF admin.'),
    h('label', { for: 'code' }, 'Access code'), input, btn, msg,
    h('p', { class: 'small muted' }, 'Lost your code? Ask an admin to issue a new one. Codes sign you in for 12 hours on this browser.'));
  root.append(h('div', { class: 'login-wrap' }, form));
  input.focus();
}

// ---------------------------------------------------------------- shell
const NAV = () => [
  { id: 'overview', label: 'Overview' },
  ...ENTITIES.map((e) => ({ id: e.key, label: e.label })),
  { id: 'review', label: can.edit() ? 'Review drafts' : 'My drafts' },
  ...(can.edit() ? [{ id: 'messages', label: 'Messages' }] : []),
  ...(can.edit() ? [{ id: 'activity', label: 'Activity' }] : []),
  ...(can.admin() ? [{ id: 'codes', label: 'Access codes' }] : []),
];

function renderShell() {
  clear(root);
  const nav = h('nav', { class: 'side', 'aria-label': 'Console' },
    h('a', { class: 'brand', href: '/', target: '_blank', rel: 'noopener' }, h('img', { src: '/favicon.svg', alt: '', width: 30, height: 30 }), h('span', {}, 'IEEF ', h('b', {}, 'Console'))),
    h('ul', {}, NAV().map((n) => h('li', {}, h('button', { type: 'button', class: n.id === current ? 'on' : '', 'data-view': n.id, onClick: () => go(n.id) }, n.label, h('span', { class: 'count', 'data-count': n.id }))))),
    h('div', { class: 'me' },
      h('div', {}, h('b', {}, me!.name), h('span', { class: `role r-${me!.role}` }, ROLE_LABEL[me!.role])),
      h('button', { type: 'button', class: 'link', onClick: async () => { await rpc('console_logout').catch(() => {}); me = null; renderLogin('Signed out.'); } }, 'Sign out')));
  const menu = h('button', { type: 'button', class: 'menu-btn', 'aria-label': 'Menu', onClick: () => document.body.classList.toggle('nav-open') }, 'Menu');
  const main = h('main', { id: 'view', tabindex: '-1' });
  root.append(h('div', { class: 'shell' }, h('header', { class: 'topbar' }, menu, h('b', {}, 'IEEF Console')), nav, main));
  go(current);
  refreshCounts();
}

async function refreshCounts() {
  const set = (id: string, n: number | null) => { const el = root.querySelector(`[data-count="${id}"]`); if (el) el.textContent = n ? String(n) : ''; };
  try {
    const drafts = await rpc<any[]>('console_drafts', { p_status: 'pending' });
    set('review', drafts.length);
    if (can.edit()) {
      const { count } = await sb.from('contact_messages').select('id', { count: 'exact', head: true }).eq('status', 'new');
      set('messages', count ?? 0);
    }
  } catch { /* counts are optional */ }
}

function go(view: string) {
  current = view;
  document.body.classList.remove('nav-open');
  root.querySelectorAll('.side button[data-view]').forEach((b) => b.classList.toggle('on', (b as HTMLElement).dataset.view === view));
  if (pollTimer) clearInterval(pollTimer);
  const main = document.getElementById('view')!;
  clear(main);
  main.append(h('p', { class: 'muted loading' }, 'Loading...'));
  const entity = ENTITIES.find((e) => e.key === view);
  const done = (p: Promise<void>) => p.catch((e) => { clear(main); main.append(h('p', { class: 'error' }, e.message)); });
  if (entity) return done(renderEntity(main, entity));
  if (view === 'review') return done(renderReview(main));
  if (view === 'messages') return done(renderMessages(main));
  if (view === 'activity') return done(renderActivity(main));
  if (view === 'codes') return done(renderCodes(main));
  return done(renderOverview(main));
}

const pageHead = (title: string, lede?: string, ...actions: Child[]) =>
  h('div', { class: 'page-head' }, h('div', {}, h('h1', {}, title), lede ? h('p', { class: 'muted' }, lede) : null), h('div', { class: 'actions' }, actions));

// ---------------------------------------------------------------- overview + publish
async function renderOverview(main: HTMLElement) {
  const [status, ...counts] = await Promise.all([
    rpc<any>('console_publish_status'),
    ...ENTITIES.map((e) => sb.from(e.key).select('id', { count: 'exact', head: true }).then((r) => r.count ?? 0)),
  ]);
  clear(main);
  main.append(pageHead(`Hello, ${me!.name.split(' ')[0]}`, `You are signed in as ${ROLE_LABEL[me!.role]}. ${ROLE_HELP[me!.role] ?? 'Full access.'}`));
  const pub = h('section', { class: 'card publish' });
  main.append(pub);
  renderPublish(pub, status);
  main.append(h('div', { class: 'stats' }, ENTITIES.map((e, i) =>
    h('button', { type: 'button', class: 'stat card', onClick: () => go(e.key) }, h('b', {}, counts[i] as number), h('span', {}, e.label)))));
  if (can.owner()) main.append(renderHookSettings(status.configured, status.abort_configured));
  main.append(h('section', { class: 'card help' },
    h('h2', {}, 'How it works'),
    h('ol', {},
      h('li', {}, 'Edit or add items in the sections on the left. Saving stores them in the database straight away.'),
      h('li', {}, can.edit() ? 'Press Publish when you are done. The website rebuilds with all saved changes and is live in about 10 minutes.' : 'Your drafts go to an editor for review. Once approved and published, they appear on the website.'),
      h('li', {}, 'Turn off "Show on website" to hide an item without deleting it.'))));
  pollTimer = window.setInterval(async () => {
    if (current !== 'overview') return;
    try { renderPublish(pub, await rpc('console_publish_status')); } catch { /* ignore */ }
  }, 30000);
}

function renderPublish(box: HTMLElement, s: any) {
  clear(box);
  const BUILD_MIN = 10;
  const since = s.last_at ? (Date.now() - new Date(s.last_at).getTime()) / 60000 : Infinity;
  const cancelled = !!s.cancelled_at;
  const building = since < BUILD_MIN + 2 && !cancelled;
  const failed = s.last_response && s.last_response.status && s.last_response.status >= 300;
  box.append(h('div', { class: 'pub-text' },
    h('h2', {}, 'Publish to the website'),
    building
      ? h('p', {}, failed ? `The rebuild request was refused (HTTP ${s.last_response.status}). Ask the owner to check the deploy hook.`
          : `Rebuild started ${ago(s.last_at)} by ${s.last_by ?? 'someone'}. The site is usually live about ${Math.max(1, Math.ceil(BUILD_MIN - since))} min from now.`)
      : h('p', {}, s.pending_changes > 0
          ? `${s.pending_changes} saved change${s.pending_changes === 1 ? '' : 's'} not yet on the website.`
          : 'The website is up to date with the database.',
        cancelled && since < 60 ? h('span', { class: 'muted' }, ` Last rebuild was aborted ${ago(s.cancelled_at)}${s.cancelled_by ? ' by ' + s.cancelled_by : ''}.`)
          : s.last_at ? h('span', { class: 'muted' }, ` Last published ${ago(s.last_at)}${s.last_by ? ' by ' + s.last_by : ''}.`) : null),
    s.pending_drafts > 0 ? h('p', { class: 'muted' }, `${s.pending_drafts} draft${s.pending_drafts === 1 ? '' : 's'} waiting for review.`) : null,
    building && !failed ? h('div', { class: 'bar' }, h('i', { style: `width:${Math.min(100, (since / BUILD_MIN) * 100)}%` })) : null));
  if (!can.edit()) return;
  const btn = h('button', { type: 'button', class: 'btn primary', disabled: !s.configured || (building && since < 2) }, building ? 'Publish again' : 'Publish now');
  btn.addEventListener('click', async () => {
    const ok = await confirmBox('Publish to the website?',
      `The website rebuilds with everything saved in the console${s.pending_changes ? ` (${s.pending_changes} change${s.pending_changes === 1 ? '' : 's'} not yet live)` : ''}. It takes about 10 minutes, and you can abort it while it runs.`,
      'Publish', 'primary');
    if (!ok) return;
    btn.disabled = true; btn.textContent = 'Starting...';
    try { await rpc('console_publish'); toast('Rebuild started. The website updates in about 10 minutes.'); renderPublish(box, await rpc('console_publish_status')); }
    catch (e: any) { toast(e.message, 'err'); btn.disabled = false; btn.textContent = 'Publish now'; }
  });
  const acts = h('div', { class: 'pub-actions' }, btn);
  if (building && !failed) {
    const abort = h('button', { type: 'button', class: 'btn danger-ghost' }, 'Abort');
    abort.addEventListener('click', async () => {
      if (!s.abort_configured) return toast('Abort is not set up yet. The owner needs to add a Cloudflare API token in Website settings below.', 'err');
      if (!(await confirmBox('Abort this rebuild?', 'The website stays exactly as it is now. Saved changes remain in the console and go live the next time someone publishes.', 'Abort rebuild'))) return;
      abort.disabled = true; abort.textContent = 'Aborting...';
      const { data, error } = await sb.functions.invoke('cancel-build', { method: 'POST' });
      if (error) {
        let msg = error.message;
        try { msg = (await (error as any).context?.json())?.error ?? msg; } catch { /* keep message */ }
        toast(msg, 'err'); abort.disabled = false; abort.textContent = 'Abort'; return;
      }
      if (data?.ok) toast('Rebuild aborted. The website was not changed.');
      renderPublish(box, await rpc('console_publish_status'));
    });
    acts.append(abort);
  }
  if (!s.configured) acts.append(h('span', { class: 'small muted' }, 'Publishing is not set up yet.'));
  acts.append(h('a', { class: 'link', href: SITE || '/', target: '_blank', rel: 'noopener' }, 'Open website'));
  box.append(acts);
}

function renderHookSettings(configured: boolean, abortConfigured: boolean) {
  const input = h('input', { type: 'url', placeholder: 'https://api.cloudflare.com/client/v4/workers/builds/deploy_hooks/...', autocomplete: 'off', 'aria-label': 'Deploy hook URL' });
  const token = h('input', { type: 'password', placeholder: 'Cloudflare API token', autocomplete: 'off', 'aria-label': 'Cloudflare API token' });
  return h('section', { class: 'card' },
    h('h2', {}, 'Website settings (owner only)'),
    h('p', { class: 'muted' }, configured ? 'Deploy hook: set. Paste a new one only if you replace it.' : 'Paste the Cloudflare deploy hook URL to enable the Publish button.'),
    h('div', { class: 'inline-form' }, input, h('button', { type: 'button', class: 'btn', onClick: async () => {
      try { await rpc('console_set_deploy_hook', { p_url: input.value.trim() }); toast('Deploy hook saved.'); go('overview'); }
      catch (e: any) { toast(e.message, 'err'); }
    } }, 'Save')),
    h('p', { class: 'muted', style: 'margin-top:18px' }, abortConfigured
      ? 'Abort button: set up. Paste a new token only if you replace it.'
      : 'To enable the Abort button, create a Cloudflare API token with the permission "Workers Builds Configuration: Edit" for the IEEF account and paste it here. It is stored in the database and never shown again.'),
    h('div', { class: 'inline-form' }, token, h('button', { type: 'button', class: 'btn', onClick: async () => {
      try { await rpc('console_set_cf_token', { p_token: (token as HTMLInputElement).value.trim() }); toast('Cloudflare token saved. Abort is ready.'); go('overview'); }
      catch (e: any) { toast(e.message, 'err'); }
    } }, 'Save token')));
}

// ---------------------------------------------------------------- content lists
const tabState: Record<string, number> = {};
async function renderEntity(main: HTMLElement, ent: Entity) {
  let q = sb.from(ent.key).select('*');
  for (const o of ent.order) q = q.order(o.column, { ascending: o.ascending, nullsFirst: false });
  const { data, error } = await q;
  if (error) throw new Error(tableErr(error));
  const rows = (data ?? []) as Row[];
  clear(main);
  const tab = tabState[ent.key] ?? 0;
  const tabDef = ent.tabs?.[tab];
  const newBtn = h('button', { type: 'button', class: 'btn primary', onClick: () => openEditor(ent, null, tabDef?.defaults) }, `New ${ent.singular}`);
  main.append(pageHead(ent.label, can.edit() ? undefined : 'Your changes are sent as drafts for an editor to review.', newBtn));
  if (ent.tabs) {
    main.append(h('div', { class: 'tabs', role: 'tablist' }, ent.tabs.map((t, i) =>
      h('button', { type: 'button', role: 'tab', 'aria-selected': String(i === tab), class: i === tab ? 'on' : '', onClick: () => { tabState[ent.key] = i; go(ent.key); } },
        t.label, h('span', { class: 'count' }, rows.filter(t.filter).length)))));
  }
  const search = h('input', { type: 'search', class: 'search', placeholder: `Search ${ent.label.toLowerCase()}...`, 'aria-label': 'Search' });
  main.append(search);
  const list = h('ul', { class: 'rows' });
  main.append(list);
  const shown = tabDef ? rows.filter(tabDef.filter) : rows;
  const draw = () => {
    clear(list);
    const term = search.value.trim().toLowerCase();
    const items = shown.filter((r) => !term || JSON.stringify([ent.title(r), ent.subtitle(r), r.slug]).toLowerCase().includes(term));
    if (!items.length) list.append(h('li', { class: 'empty muted' }, 'Nothing here yet.'));
    for (const r of items) {
      const thumbVal = r.image ?? r.photo ?? r.logo ?? r.poster ?? r.cover;
      const thumb = mediaUrl(thumbVal);
      const isHeadline = r.featured && (ent.key === 'news' || r.kind === 'policy_brief');
      const autoHeadline = ent.key === 'news' && !rows.some((x) => x.featured) && r === rows[0];
      list.append(h('li', { class: 'row-wrap' }, h('button', { type: 'button', class: 'row', onClick: () => openEditor(ent, r) },
        h('span', { class: 'thumb' }, thumb ? h('img', { src: thumb, alt: '', loading: 'lazy' }) : thumbVal ? h('span', { class: 'tag' }, 'orig') : null),
        h('span', { class: 'row-text' }, h('b', {}, ent.title(r) || '(untitled)'), h('span', { class: 'muted' }, ent.subtitle(r))),
        r.published === false ? h('span', { class: 'pill off' }, 'Hidden') : h('span', { class: 'pill on' }, 'On site'),
        isHeadline ? h('span', { class: 'pill warm' }, 'Headline') : r.featured ? h('span', { class: 'pill warm' }, 'Highlight')
          : autoHeadline ? h('span', { class: 'pill soft', title: 'Newest article; shown as headline because none is pinned' }, 'Headline (newest)') : null),
        headlineButton(ent, r, () => go(ent.key))));
    }
  };
  search.addEventListener('input', draw);
  draw();
}

// one-click headline / highlight controls on list rows (editors and above)
function headlineButton(ent: Entity, r: Row, refresh: () => void) {
  if (!can.edit() || !('featured' in r) || (ent.key !== 'news' && ent.key !== 'publications')) return null;
  const exclusive = ent.key === 'news' || r.kind === 'policy_brief';
  const label = r.featured ? (exclusive ? (ent.key === 'news' ? 'Unpin' : 'Remove headline') : 'Remove highlight') : (exclusive ? 'Make headline' : 'Highlight');
  return h('button', { type: 'button', class: `btn small ${r.featured ? 'ghost' : ''} row-act`, onClick: async () => {
    if (r.published === false && !r.featured) return toast('Turn on "Show on website" for this item first.', 'err');
    const { error } = await sb.from(ent.key).update({ featured: !r.featured }).eq('id', r.id);
    if (error) return toast(tableErr(error), 'err');
    toast(r.featured
      ? (ent.key === 'news' ? 'Unpinned. The newest article becomes the headline. Press Publish to update the website.' : 'Removed. Press Publish to update the website.')
      : (exclusive ? 'New headline set; the previous one was unpinned. Press Publish to update the website.' : 'Highlighted. Press Publish to update the website.'));
    refresh();
  } }, label);
}

// ---------------------------------------------------------------- editor drawer
function fieldInput(f: Field, row: Row, onChange: () => void): HTMLElement {
  const id = `f-${f.key}`;
  const v = row[f.key];
  const set = (val: any) => { row[f.key] = val; onChange(); };
  let control: HTMLElement;
  switch (f.type) {
    case 'textarea': case 'longtext':
      control = h('textarea', { id, rows: f.type === 'longtext' ? 14 : 3, value: v ?? '', onInput: (e: any) => set(e.target.value) }); break;
    case 'list':
      control = h('textarea', { id, rows: 6, value: (v ?? []).join('\n'), onInput: (e: any) => set(e.target.value.split('\n').map((s: string) => s.trim()).filter(Boolean)) }); break;
    case 'number':
      control = h('input', { id, type: 'number', value: v ?? '', onInput: (e: any) => set(e.target.value === '' ? null : Number(e.target.value)) }); break;
    case 'date':
      control = h('input', { id, type: 'date', value: v ?? '', onInput: (e: any) => set(e.target.value || null) }); break;
    case 'bool':
      control = h('label', { class: 'switch' }, h('input', { id, type: 'checkbox', checked: !!v, onChange: (e: any) => set(e.target.checked) }), h('span', {}, v ? 'Yes' : 'No'));
      control.querySelector('input')!.addEventListener('change', (e: any) => { control.querySelector('span')!.textContent = e.target.checked ? 'Yes' : 'No'; });
      break;
    case 'select':
      control = h('select', { id, onChange: (e: any) => set(e.target.value || null) }, f.options!.map((o) => h('option', { value: o.value, selected: (v ?? '') === o.value }, o.label))); break;
    case 'image': case 'pdf': control = uploadControl(f, row, set); break;
    case 'slug':
      control = h('div', { class: 'slug' }, h('input', { id, value: v ?? '', pattern: '[a-z0-9-]+', onInput: (e: any) => { row.__slugTouched = true; set(e.target.value); } }),
        h('button', { type: 'button', class: 'link', onClick: () => {
          const src = (f.from ?? []).map((k) => row[k]).find(Boolean) ?? '';
          const s = slugify(String(src)); row.__slugTouched = true; set(s); (control.querySelector('input') as HTMLInputElement).value = s;
        } }, 'Make from title'));
      break;
    default:
      control = h('input', { id, type: f.type === 'url' ? 'url' : 'text', value: v ?? '', onInput: (e: any) => set(e.target.value) });
  }
  return h('div', { class: `field t-${f.type}`, 'data-key': f.key },
    h('label', { for: id }, f.label, f.required ? h('span', { class: 'req', 'aria-hidden': 'true' }, ' *') : null),
    control, f.help ? h('p', { class: 'help' }, f.help) : null);
}

function uploadControl(f: Field, row: Row, set: (v: any) => void) {
  const wrap = h('div', { class: 'upload' });
  const draw = () => {
    clear(wrap);
    const v = row[f.key] as string | null;
    const url = mediaUrl(v);
    if (f.type === 'image') {
      wrap.append(h('div', { class: 'preview' }, url ? h('img', { src: url, alt: '' }) : v ? h('span', { class: 'muted small' }, 'Image from the original site') : h('span', { class: 'muted small' }, 'No image')));
    } else {
      wrap.append(h('input', { type: 'url', value: v ?? '', placeholder: 'https://drive.google.com/...', onInput: (e: any) => { row[f.key] = e.target.value || null; } }));
      if (url) wrap.append(h('a', { class: 'link small', href: url, target: '_blank', rel: 'noopener' }, 'Open current file'));
    }
    const file = h('input', { type: 'file', accept: f.type === 'image' ? 'image/jpeg,image/png,image/webp,image/avif' : 'application/pdf', class: 'sr-only', id: `up-${f.key}` });
    const status = h('span', { class: 'small muted' });
    file.addEventListener('change', async () => {
      const fl = file.files?.[0];
      if (!fl) return;
      if (fl.size > 20 * 1024 * 1024) { toast('File is larger than 20 MB. Please compress it first.', 'err'); return; }
      if (f.type === 'image' && fl.size > 4 * 1024 * 1024) toast('Large image: it will be optimised on the website, but uploads are faster under 4 MB.', 'info');
      status.textContent = 'Uploading...';
      const ext = (fl.name.split('.').pop() || 'bin').toLowerCase().replace(/[^a-z0-9]/g, '');
      const base = slugify(fl.name.replace(/\.[^.]+$/, '')) || 'file';
      const path = `${f.folder ?? 'misc'}/${new Date().toISOString().slice(0, 10)}-${Math.random().toString(36).slice(2, 7)}-${base}.${ext}`;
      const { error } = await sb.storage.from('media').upload(path, fl, { contentType: fl.type, upsert: false });
      if (error) { status.textContent = ''; toast('Upload failed: ' + error.message, 'err'); return; }
      set(path); draw(); toast('Uploaded. Remember to save.', 'info');
    });
    wrap.append(h('div', { class: 'upload-actions' },
      h('label', { class: 'btn small', for: `up-${f.key}` }, v ? 'Replace file' : f.type === 'image' ? 'Upload image' : 'Upload PDF'), file,
      v ? h('button', { type: 'button', class: 'link small', onClick: () => { set(null); draw(); } }, 'Remove') : null, status));
  };
  draw();
  return wrap;
}

function openEditor(ent: Entity, original: Row | null, defaults: Row = {}, draft?: any) {
  const isNew = !original;
  const row: Row = draft ? { ...(original ?? {}), ...draft.data } : original ? structuredClone(original) : { ...ent.defaults, ...defaults };
  const contributor = !can.edit();
  const back = h('div', { class: 'drawer-back' });
  const form = h('form', { class: 'drawer', novalidate: true, 'aria-label': `${isNew ? 'New' : 'Edit'} ${ent.singular}` });
  const body = h('div', { class: 'drawer-body' });
  const close = () => { back.remove(); document.removeEventListener('keydown', onKey); };
  const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') close(); };
  document.addEventListener('keydown', onKey);

  const renderFields = () => {
    clear(body);
    const visible = ent.fields.filter((f) => !f.showIf || f.showIf(row));
    const done = new Set<string>();
    for (const f of visible) {
      if (done.has(f.key)) continue;
      if (f.pair) {
        const pair = visible.filter((x) => x.pair === f.pair);
        pair.forEach((x) => done.add(x.key));
        body.append(h('div', { class: 'pair' }, pair.map((x) => fieldInput(x, row, onChange))));
      } else { done.add(f.key); body.append(fieldInput(f, row, onChange)); }
    }
    if (contributor) body.append(h('div', { class: 'field' }, h('label', { for: 'f-note' }, 'Note for the reviewer'),
      h('textarea', { id: 'f-note', rows: 2, value: draft?.note ?? '', onInput: (e: any) => { row.__note = e.target.value; } })));
  };
  // auto web address for new items until the editor types one
  const onChange = () => {
    if (isNew && !row.__slugTouched) {
      const sf = ent.fields.find((f) => f.type === 'slug');
      const src = sf?.from?.map((k) => row[k]).find(Boolean);
      if (sf && src) { row[sf.key] = slugify(String(src)); const el = body.querySelector(`#f-${sf.key}`) as HTMLInputElement | null; if (el) el.value = row[sf.key]; }
    }
    if ((row.kind !== undefined) && (body.dataset.kind ?? '') !== String(row.kind)) { body.dataset.kind = String(row.kind); renderFields(); }
  };
  body.dataset.kind = String(row.kind ?? '');

  const saveBtn = h('button', { type: 'submit', class: 'btn primary' }, contributor ? (draft ? 'Update draft' : 'Send for review') : 'Save');
  const actions = h('div', { class: 'drawer-foot' }, saveBtn, h('button', { type: 'button', class: 'btn ghost', onClick: close }, 'Cancel'));
  if (!isNew && can.admin() && !draft) actions.append(h('button', { type: 'button', class: 'btn danger-ghost push', onClick: async () => {
    if (!(await confirmBox(`Delete this ${ent.singular}?`, 'This removes it from the database permanently. To hide it but keep it, turn off "Show on website" instead.', 'Delete'))) return;
    const { error } = await sb.from(ent.key).delete().eq('id', original!.id);
    if (error) return toast(tableErr(error), 'err');
    toast('Deleted. Press Publish to update the website.'); close(); go(ent.key);
  } }, 'Delete'));
  const path = !isNew && original?.published !== false ? ent.sitePath(original!) : null;

  form.append(
    h('div', { class: 'drawer-head' },
      h('div', {}, h('p', { class: 'eyebrow' }, isNew ? `New ${ent.singular}` : `Edit ${ent.singular}`), h('h2', {}, isNew ? 'Untitled' : ent.title(original!) || 'Untitled')),
      h('div', { class: 'head-actions' }, path ? h('a', { class: 'link small', href: (SITE || '') + path, target: '_blank', rel: 'noopener' }, 'View on site') : null,
        h('button', { type: 'button', class: 'x', 'aria-label': 'Close', onClick: close }, 'Close'))),
    body, actions);
  renderFields();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data: Row = {};
    for (const f of ent.fields) {
      if (f.showIf && !f.showIf(row)) { if (f.type !== 'select' && f.type !== 'bool') data[f.key] = row[f.key] ?? null; continue; }
      let v = row[f.key];
      if (typeof v === 'string') v = v.trim();
      if (v === '' && f.type !== 'list') v = null;
      if (f.type === 'list') v = Array.isArray(v) ? v : [];
      if (f.type === 'bool') v = !!v;
      data[f.key] = v;
    }
    const missing = ent.fields.filter((f) => f.required && (!f.showIf || f.showIf(row)) && (data[f.key] == null || data[f.key] === ''));
    body.querySelectorAll('.field.bad').forEach((x) => x.classList.remove('bad'));
    if (missing.length) {
      missing.forEach((f) => body.querySelector(`[data-key="${f.key}"]`)?.classList.add('bad'));
      return toast(`Please fill in: ${missing.map((f) => f.label).join(', ')}`, 'err');
    }
    if (data.slug && !/^[a-z0-9-]+$/.test(data.slug)) return toast('The web address may only contain lowercase letters, numbers and hyphens.', 'err');
    if (ent.key === 'news' && !data.title_en && !data.title_id) return toast('Enter a title in at least one language.', 'err');
    if (ent.key === 'careers' && !data.title_en && !data.title_id) return toast('Enter the role name in at least one language.', 'err');
    saveBtn.disabled = true;
    try {
      if (contributor) {
        await rpc('console_draft_submit', { p_entity: ent.key, p_row: original?.id ?? null, p_data: data, p_note: row.__note ?? null, p_draft: draft?.id ?? null });
        toast('Sent for review. An editor will check it before it goes live.');
      } else if (draft) {
        await rpc('console_draft_review', { p_id: draft.id, p_decision: 'approve', p_data: data, p_note: null });
        toast('Draft approved and saved. Press Publish to update the website.');
      } else {
        const res = isNew ? await sb.from(ent.key).insert(data) : await sb.from(ent.key).update(data).eq('id', original!.id);
        if (res.error) throw new Error(tableErr(res.error));
        toast('Saved. Press Publish on the Overview to update the website.');
      }
      close();
      go(draft ? 'review' : ent.key);
      refreshCounts();
    } catch (err: any) { toast(err.message, 'err'); }
    finally { saveBtn.disabled = false; }
  });
  back.append(form);
  back.addEventListener('mousedown', (e) => { if (e.target === back) close(); });
  document.body.append(back);
  (body.querySelector('input, textarea, select') as HTMLElement | null)?.focus();
}

// ---------------------------------------------------------------- review drafts
const entityOf = (k: string) => ENTITIES.find((e) => e.key === k)!;
async function renderReview(main: HTMLElement, status = 'pending') {
  const drafts = await rpc<any[]>('console_drafts', { p_status: status });
  clear(main);
  main.append(pageHead(can.edit() ? 'Review drafts' : 'My drafts',
    can.edit() ? 'Drafts and suggested edits from contributors. Approve to save them into the website content, then Publish.' : 'Drafts you sent. Editors approve or return them with a note.'));
  main.append(h('div', { class: 'tabs' }, [['pending', 'Waiting'], ['approved', 'Approved'], ['rejected', 'Returned'], ['all', 'All']].map(([k, l]) =>
    h('button', { type: 'button', class: k === status ? 'on' : '', onClick: () => renderReview(main, k) }, l))));
  const list = h('div', { class: 'drafts' });
  main.append(list);
  if (!drafts.length) list.append(h('p', { class: 'muted empty' }, 'No drafts here.'));
  for (const d of drafts) {
    const ent = entityOf(d.entity);
    let originalRow: Row | null = null;
    if (d.row_id) { const r = await sb.from(d.entity).select('*').eq('id', d.row_id).maybeSingle(); originalRow = r.data; }
    const changed = ent.fields.filter((f) => d.data[f.key] !== undefined && JSON.stringify(d.data[f.key] ?? null) !== JSON.stringify(originalRow?.[f.key] ?? null));
    const card = h('article', { class: 'card draft' },
      h('div', { class: 'draft-head' },
        h('div', {}, h('p', { class: 'eyebrow' }, `${ent.label} · ${d.row_id ? 'Suggested edit' : 'New item'}`), h('h3', {}, ent.title(d.data) || '(untitled)'),
          h('p', { class: 'small muted' }, `From ${d.created_by_name ?? 'unknown'}, ${ago(d.created_at)}`)),
        h('span', { class: `pill s-${d.status}` }, { pending: 'Waiting', approved: 'Approved', rejected: 'Returned', withdrawn: 'Withdrawn' }[d.status as string] ?? d.status)),
      d.note ? h('p', { class: 'note' }, h('b', {}, 'Note: '), d.note) : null,
      d.review_note ? h('p', { class: 'note warn' }, h('b', {}, `Reviewer (${d.reviewed_by_name ?? ''}): `), d.review_note) : null,
      h('details', {}, h('summary', {}, `${changed.length} field${changed.length === 1 ? '' : 's'} ${d.row_id ? 'changed' : 'filled in'}`),
        h('table', { class: 'diff' }, h('tbody', {}, changed.map((f) => h('tr', {},
          h('th', {}, f.label),
          d.row_id ? h('td', { class: 'old' }, show(originalRow?.[f.key])) : null,
          h('td', { class: 'new' }, show(d.data[f.key]))))))));
    if (d.status === 'pending') {
      const acts = h('div', { class: 'draft-actions' });
      if (can.edit()) {
        acts.append(
          h('button', { type: 'button', class: 'btn primary', onClick: async () => {
            try { await rpc('console_draft_review', { p_id: d.id, p_decision: 'approve' }); toast('Approved. Press Publish to update the website.'); renderReview(main, status); refreshCounts(); }
            catch (e: any) { toast(tableErr(e), 'err'); }
          } }, 'Approve'),
          h('button', { type: 'button', class: 'btn', onClick: () => openEditor(ent, originalRow, {}, d) }, 'Edit, then approve'),
          h('button', { type: 'button', class: 'btn ghost', onClick: () => {
            const note = h('textarea', { rows: 3, placeholder: 'What should the contributor change?' });
            modal('Return draft', h('div', {}, h('p', { class: 'muted' }, 'The contributor sees this note.'), note), [
              { label: 'Cancel' },
              { label: 'Return draft', kind: 'primary', onClick: async () => {
                try { await rpc('console_draft_review', { p_id: d.id, p_decision: 'reject', p_note: (note as HTMLTextAreaElement).value || null }); toast('Draft returned.'); renderReview(main, status); refreshCounts(); }
                catch (e: any) { toast(e.message, 'err'); return false; }
              } }]);
          } }, 'Return with note'));
      }
      if (d.created_by === me!.id) {
        if (!can.edit()) acts.append(h('button', { type: 'button', class: 'btn', onClick: () => openEditor(ent, originalRow, {}, d) }, 'Edit draft'));
        acts.append(h('button', { type: 'button', class: 'link', onClick: async () => { await rpc('console_draft_withdraw', { p_id: d.id }); renderReview(main, status); refreshCounts(); } }, 'Withdraw'));
      }
      card.append(acts);
    }
    list.append(card);
  }
}
function show(v: any): string {
  if (v == null || v === '') return '(empty)';
  if (Array.isArray(v)) return v.length ? v.map((x) => '• ' + x).join('\n') : '(empty)';
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  const s = String(v);
  return s.length > 600 ? s.slice(0, 600) + '...' : s;
}

// ---------------------------------------------------------------- messages
async function renderMessages(main: HTMLElement, status = 'new') {
  let q = sb.from('contact_messages').select('*').order('created_at', { ascending: false }).limit(300);
  if (status !== 'all') q = q.eq('status', status);
  const { data, error } = await q;
  if (error) throw new Error(tableErr(error));
  clear(main);
  main.append(pageHead('Messages', 'Sent through the Contact page. Reply from your own email; the sender\'s address is filled in for you.'));
  main.append(h('div', { class: 'tabs' }, [['new', 'New'], ['read', 'Read'], ['archived', 'Archived'], ['all', 'All']].map(([k, l]) =>
    h('button', { type: 'button', class: k === status ? 'on' : '', onClick: () => renderMessages(main, k) }, l))));
  const list = h('div', { class: 'msgs' });
  main.append(list);
  if (!data?.length) list.append(h('p', { class: 'muted empty' }, 'No messages here.'));
  const setStatus = async (id: string, s: string) => {
    const { error } = await sb.from('contact_messages').update({ status: s }).eq('id', id);
    if (error) toast(tableErr(error), 'err');
  };
  for (const m of data ?? []) {
    const subject = `Re: ${m.subject ?? 'Your message to IEEF'}`;
    const det = h('details', { class: `card msg ${m.status}` },
      h('summary', {}, h('span', { class: 'msg-from' }, h('b', {}, m.name), h('span', { class: 'muted' }, m.organization ? ` · ${m.organization}` : '')),
        h('span', { class: 'msg-sub' }, m.subject ?? ''), h('time', { class: 'muted small' }, ago(m.created_at))),
      h('div', { class: 'msg-body' },
        h('p', { class: 'small muted' }, `${m.email} · ${fmtTime(m.created_at)}`),
        h('p', { class: 'msg-text' }, m.message),
        h('div', { class: 'draft-actions' },
          h('a', { class: 'btn primary', href: `mailto:${encodeURIComponent(m.email)}?subject=${encodeURIComponent(subject)}` }, 'Reply by email'),
          m.status !== 'archived' ? h('button', { type: 'button', class: 'btn', onClick: async () => { await setStatus(m.id, 'archived'); renderMessages(main, status); refreshCounts(); } }, 'Archive') : null,
          m.status !== 'new' ? h('button', { type: 'button', class: 'btn ghost', onClick: async () => { await setStatus(m.id, 'new'); renderMessages(main, status); refreshCounts(); } }, 'Mark as new') : null,
          can.admin() ? h('button', { type: 'button', class: 'btn danger-ghost push', onClick: async () => {
            if (!(await confirmBox('Delete message?', 'It will be removed permanently.', 'Delete'))) return;
            const { error } = await sb.from('contact_messages').delete().eq('id', m.id);
            if (error) return toast(tableErr(error), 'err');
            renderMessages(main, status); refreshCounts();
          } }, 'Delete') : null)));
    det.addEventListener('toggle', async () => { if (det.open && m.status === 'new') { m.status = 'read'; det.classList.remove('new'); await setStatus(m.id, 'read'); refreshCounts(); } });
    list.append(det);
  }
}

// ---------------------------------------------------------------- activity
const ACTION: Record<string, string> = {
  insert: 'added', update: 'edited', delete: 'deleted', sign_in: 'signed in', publish: 'published the website',
  code_created: 'created an access code for', code_revoked: 'revoked the code of', code_reinstated: 'reinstated the code of',
  code_edited: 'edited the code of', code_replaced: 'issued a new code for', code_deleted: 'deleted the code of',
  draft_submitted: 'sent a draft:', draft_approved: 'approved a draft:', draft_rejected: 'returned a draft:', deploy_hook_set: 'updated the deploy hook', publish_cancelled: 'aborted the website rebuild', cf_token_set: 'updated the Cloudflare token',
};
async function renderActivity(main: HTMLElement) {
  const items = await rpc<any[]>('console_activity', { p_limit: 200 });
  clear(main);
  main.append(pageHead('Activity', 'Every change made through the console, newest first.'));
  main.append(h('ul', { class: 'activity card' }, items.map((a) => h('li', {},
    h('time', { class: 'muted small' }, fmtTime(a.at)),
    h('span', {}, h('b', {}, a.staff ?? 'System'), ` ${ACTION[a.action] ?? a.action} `,
      a.entity && !['staff', 'site'].includes(a.entity) ? h('span', { class: 'muted' }, `${entityOf(a.entity)?.singular ?? a.entity} `) : null,
      a.detail?.label ? h('i', {}, a.detail.label) : null)))));
}

// ---------------------------------------------------------------- access codes
async function renderCodes(main: HTMLElement) {
  const staff = await rpc<Staff[]>('console_staff_list');
  clear(main);
  const name = h('input', { placeholder: 'Name of the person', required: true, 'aria-label': 'Name' });
  const role = h('select', { 'aria-label': 'Role' }, (can.owner() ? ['editor', 'contributor', 'admin'] : ['editor', 'contributor']).map((r) => h('option', { value: r }, ROLE_LABEL[r as Role])));
  const note = h('input', { placeholder: 'Note (optional), e.g. Research team', 'aria-label': 'Note' });
  const roleHelp = h('p', { class: 'help' }, ROLE_HELP.editor);
  role.addEventListener('change', () => { roleHelp.textContent = ROLE_HELP[(role as HTMLSelectElement).value]; });
  main.append(pageHead('Access codes', 'Each person gets their own code. Codes are shown once when created; issue a new one if it is lost.'));
  main.append(h('form', { class: 'card new-code', onSubmit: async (e: Event) => {
    e.preventDefault();
    try {
      const r = await rpc<{ code: string; staff: Staff }>('console_staff_create', { p: { name: (name as HTMLInputElement).value, role: (role as HTMLSelectElement).value, note: (note as HTMLInputElement).value } });
      showCode(r.staff.name, r.code); renderCodes(main);
    } catch (err: any) { toast(err.message, 'err'); }
  } }, h('h2', {}, 'Create a code'), h('div', { class: 'inline-form' }, name, role, note, h('button', { class: 'btn primary', type: 'submit' }, 'Create code')), roleHelp));
  const table = h('table', { class: 'codes' }, h('thead', {}, h('tr', {}, ['Person', 'Role', 'Code ends with', 'Last sign-in', 'Status', ''].map((x) => h('th', {}, x)))));
  const tb = h('tbody');
  for (const s of staff) {
    const mine = s.id === me!.id;
    const locked = s.role === 'owner' || (s.role === 'admin' && !can.owner());
    const acts = h('td', { class: 'acts' });
    if (!locked || (mine && s.role !== 'owner')) {
      acts.append(h('button', { type: 'button', class: 'link', onClick: () => editStaff(s, main) }, 'Edit'));
    }
    if (!locked || mine || can.owner()) acts.append(h('button', { type: 'button', class: 'link', onClick: async () => {
      if (!(await confirmBox('Issue a new code?', `The current code for ${s.name} stops working immediately.`, 'Issue new code', 'primary'))) return;
      try { const r = await rpc<{ code: string }>('console_staff_new_code', { p_id: s.id }); showCode(s.name, r.code); renderCodes(main); } catch (e: any) { toast(e.message, 'err'); }
    } }, 'New code'));
    if (!locked && !mine) {
      acts.append(h('button', { type: 'button', class: 'link', onClick: async () => {
        try { await rpc('console_staff_update', { p_id: s.id, p: { active: !s.active } }); toast(s.active ? 'Code revoked.' : 'Code reinstated.'); renderCodes(main); } catch (e: any) { toast(e.message, 'err'); }
      } }, s.active ? 'Revoke' : 'Reinstate'));
      if (!s.active) acts.append(h('button', { type: 'button', class: 'link danger', onClick: async () => {
        if (!(await confirmBox('Delete this code?', `${s.name} disappears from the list. Their past activity stays in the log.`, 'Delete'))) return;
        try { await rpc('console_staff_delete', { p_id: s.id }); renderCodes(main); } catch (e: any) { toast(e.message, 'err'); }
      } }, 'Delete'));
    }
    tb.append(h('tr', { class: s.active ? '' : 'inactive' },
      h('td', {}, h('b', {}, s.name), mine ? h('span', { class: 'muted' }, ' (you)') : null, s.note ? h('div', { class: 'small muted' }, s.note) : null),
      h('td', {}, h('span', { class: `role r-${s.role}` }, ROLE_LABEL[s.role])),
      h('td', { class: 'mono' }, `...${s.code_hint}`),
      h('td', { class: 'small' }, s.last_login_at ? ago(s.last_login_at) : h('span', { class: 'muted' }, 'never')),
      h('td', {}, s.active ? h('span', { class: 'pill on' }, 'Active') : h('span', { class: 'pill off' }, 'Revoked')),
      acts));
  }
  table.append(tb);
  main.append(h('div', { class: 'card table-wrap' }, table));
}

function showCode(name: string, code: string) {
  const codeEl = h('div', { class: 'big-code mono' }, code);
  const copy = h('button', { type: 'button', class: 'btn', onClick: async () => { try { await navigator.clipboard.writeText(code); copy.textContent = 'Copied'; } catch { /* no clipboard */ } } }, 'Copy code');
  modal(`Access code for ${name}`, h('div', {}, codeEl, h('p', { class: 'muted' },
    'Send it to them privately (e.g. WhatsApp). This is the only time the code is shown. They sign in at this console address.'), copy),
    [{ label: 'Done', kind: 'primary' }]);
}

function editStaff(s: Staff, main: HTMLElement) {
  const name = h('input', { value: s.name, 'aria-label': 'Name' });
  const note = h('input', { value: s.note ?? '', 'aria-label': 'Note' });
  const roles: Role[] = can.owner() ? ['admin', 'editor', 'contributor'] : ['editor', 'contributor'];
  const role = s.role === 'owner' ? null : h('select', { 'aria-label': 'Role' }, roles.map((r) => h('option', { value: r, selected: r === s.role }, ROLE_LABEL[r])));
  modal(`Edit ${s.name}`, h('div', { class: 'stack' },
    h('label', {}, 'Name', name), role ? h('label', {}, 'Role', role) : null, h('label', {}, 'Note', note)), [
    { label: 'Cancel' },
    { label: 'Save', kind: 'primary', onClick: async () => {
      const p: Row = { name: (name as HTMLInputElement).value, note: (note as HTMLInputElement).value };
      if (role && (role as HTMLSelectElement).value !== s.role) p.role = (role as HTMLSelectElement).value;
      try { await rpc('console_staff_update', { p_id: s.id, p }); toast('Saved.'); renderCodes(main); }
      catch (e: any) { toast(e.message, 'err'); return false; }
    } }]);
}

boot();
