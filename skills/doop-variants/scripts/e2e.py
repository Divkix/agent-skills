"""Local prototype click test + frame crawl for a synced Doop canvas.

Runs inside omp's Python eval (needs the Doop bridge `call(name, args)` and `read`) and drives its own headless
agent-browser session:

    h = e2e.Harness('~/GitHub/app', call, read)   # reads <app>/.doop/config.json and journeys.json
    await h.load()                  # frames + variant maps from doop_sync
    await h.export()                # /tmp/doop-e2e/<app>/frames/<id>.html: frame + token CSS + player.js
    h.serve()                       # local no-cache HTTP server on a free port
    rep = h.journeys()              # every journey x light/dark/phone/phone-dark: (variant, name, ok, clicks, why)
    bad = h.crawl_all()             # covered/small targets, missing scroll targets, overflow at 390, unwired links
    h.close()                       # stop the server, close the browser session, delete the export

journeys.json: {"M": {key: light master id}, "JOURNEYS": {name: [start key, [[target, expected], ...]]},
"ONLY": {name: [variants]}}. target is a visible label, ["sel", css] or ["opt", css] (skipped when absent on the
current frame), or "GOTO" (jump straight to `expected`). expected is a key of M, "OTHER:<key>" for the other theme
of the same form factor, or null (stay). Selector ids written as master ids are remapped per variant.
"""
import asyncio, functools, http.server, json, pathlib, re, shutil, subprocess, threading, time

import doop_sync as ds

VARIANTS = ('light', 'dark', 'phone', 'phone-dark')
PLAYER = pathlib.Path(__file__).with_name('player.js')


class _NoCache(http.server.SimpleHTTPRequestHandler):
    # a re-export keeps the same URLs; without this the browser renders the stale copy
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass


FIND_JS = r'''
(() => {
  const want = %s, sel = %s;
  const ov = document.querySelector('#doop-overlay iframe');
  const doc = ov ? ov.contentDocument : document;
  const off = ov ? ov.getBoundingClientRect() : {left:0, top:0};
  const wired = [...doc.querySelectorAll(sel || '[data-doop-action],[data-doop-interactions]')];
  // frames never use the popover API: any [popover] is browser-extension UI (autofill) drawn over the page
  doc.querySelectorAll('[popover]').forEach(p => { try { p.hidePopover(); } catch {} });
  // first non-empty line box: a wrapped inline link's bounding-box centre can fall between its lines,
  // and an inline <a> around a block card reports empty fragments before and after the card
  const pt = e => { const r = [...e.getClientRects()].find(q => q.width > 1 && q.height > 1) || e.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
  const norm = s => (s||'').replace(/\s+/g,' ').trim().toLowerCase();
  const label = e => norm(e.innerText) || norm(e.getAttribute('aria-label'));
  const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity !== 0
      && !(e.closest('details:not([open])') && !e.closest('summary')); };
  const cands = wired.filter(e => vis(e) && (want === null || label(e) === norm(want) || label(e).startsWith(norm(want))));
  if (!cands.length) return JSON.stringify({error: 'not found', want, labels: wired.filter(vis).map(label).slice(0, 60)});
  const hidden = e => { e.scrollIntoView({block: 'center', inline: 'center', behavior: 'instant'});
    const t = doc.elementFromPoint(...pt(e)); return !(t && (t === e || e.contains(t))); };
  const score = e => (want !== null && label(e) !== norm(want) ? 1 : 0) + (hidden(e) ? 2 : 0);
  const el = cands.map(e => [score(e), e]).sort((a, b) => a[0] - b[0])[0][1];
  el.scrollIntoView({block: 'center', inline: 'center', behavior: 'instant'});
  const r = el.getBoundingClientRect();
  const [x, y] = pt(el);
  const top = doc.elementFromPoint(x, y);
  const covered = !(top && (top === el || el.contains(top)));
  return JSON.stringify({x: x + off.left, y: y + off.top, w: r.width, h: r.height, action: el.dataset.doopAction || el.dataset.doopInteractions,
    covered, coveredBy: covered && top ? (top.tagName + '.' + top.className).slice(0, 80) : null, label: label(el).slice(0, 60)});
})()'''

CRAWL_JS = r'''
(() => {
  const skip = %s;
  const norm = s => (s||'').replace(/\s+/g,' ').trim().slice(0, 50);
  const label = e => norm(e.innerText) || norm(e.getAttribute('aria-label')) || e.tagName;
  const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && +cs.opacity !== 0 && !e.closest('[hidden],[aria-hidden=true]')
      && !(e.closest('details:not([open])') && !e.closest('summary')); };
  const acts = e => { try { return e.dataset.doopInteractions ? JSON.parse(e.dataset.doopInteractions) : [{on: e.dataset.doopOn, action: e.dataset.doopAction}]; } catch { return [{on: 'BAD', action: 'BAD JSON'}]; } };
  document.querySelectorAll('[popover]').forEach(p => { try { p.hidePopover(); } catch {} });
  const pt = e => { const r = [...e.getClientRects()].find(q => q.width > 1 && q.height > 1) || e.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
  const wired = [...document.querySelectorAll('[data-doop-action],[data-doop-interactions]')].map(e => {
    const v = vis(e); let covered = null;
    if (v) { e.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'});
      const t = document.elementFromPoint(...pt(e)); covered = !(t && (t === e || e.contains(t) || t.contains(e)));
      if (covered) covered = (t ? t.tagName + '.' + String(t.className).slice(0, 40) : 'offscreen'); }
    return {label: label(e), acts: acts(e), visible: v, covered,
      missingScroll: acts(e).filter(a => String(a.action).startsWith('scroll-to:') && !document.querySelector(a.action.slice(10))).map(a => a.action),
      small: v && (e.getBoundingClientRect().height < 24)};
  });
  const unwired = [...document.querySelectorAll('a[href],button')].filter(e => vis(e) && !e.closest('[data-doop-action],[data-doop-interactions]')
    && !(e.getAttribute('href')||'').startsWith('mailto:') && !(skip && e.matches(skip))).map(e => e.tagName + ' ' + label(e) + ' ' + (e.getAttribute('href')||''));
  const overflowX = document.documentElement.scrollWidth > innerWidth + 1;
  return JSON.stringify({wired, unwired, overflowX, height: document.documentElement.scrollHeight});
})()'''


class Harness:
    def __init__(self, app, call, read, cdp=None):
        """cdp: attach to a running browser's DevTools port instead of a private headless one. Another focused tab in
        that browser can then swallow the mouse clicks."""
        self.call, self.read, self.cfg = call, read, ds.load(app)
        self.spec = json.loads((self.cfg['root'] / '.doop' / 'journeys.json').read_text())
        for start_steps in self.spec['JOURNEYS'].values():
            start_steps[1] = [(tuple(t) if isinstance(t, list) else t, exp) for t, exp in start_steps[1]]
        self.dir = pathlib.Path('/tmp/doop-e2e') / self.cfg['name']
        self.cdp, self.server = cdp, None
        session = 'doop-e2e-' + re.sub(r'[^A-Za-z0-9_-]', '-', self.cfg['name'])
        self.abargs = ['agent-browser', '--session', session] + (['--cdp', str(cdp), '--pin-tab'] if cdp else [])

    # ------------------------------------------------------------ canvas model
    async def load(self):
        self.frames = await ds.get_frames(self.cfg, self.call, self.read)
        self.masters, self.phone_only, *_ = ds.plan(self.frames)
        self.maps = ds.id_maps(self.masters, self.phone_only)
        self.maps['light'] = {f['id']: m['light']['id'] for m in self.masters.values() for f in m.values()}
        self.name = {f['id']: f['name'] for f in self.frames}
        self.menus = {v: {m[v]['id'] for m in self.phone_only.values() if v in m} for v in ('phone', 'phone-dark')}
        return len(self.frames)

    def vid(self, fid, v):
        return self.maps[v].get(fid, fid)

    async def export(self, conc=3):
        tag = f'<style data-doop-tokens>{await ds.tokens_css(self.cfg, self.call)}</style>'
        out = self.dir / 'frames'; out.mkdir(parents=True, exist_ok=True)
        (self.dir / 'player.js').write_text(PLAYER.read_text())
        (out / 'sizes.js').write_text('window.DOOP_SIZES=' + json.dumps({f['id']: [f['width'], f['height']] for f in self.frames}))
        sem = asyncio.Semaphore(conc)

        async def one(f):
            async with sem:
                h = await ds._get_html(self.call, self.read, f['id'], self.cfg['agent'])
                await asyncio.sleep(0.3)
            h = ds.HEAD_TAG.sub(lambda m: m.group(0) + tag, h, count=1) if ds.HEAD_TAG.search(h) else tag + h
            js = f'<script src="sizes.js"></script><script src="../player.js" data-frame="{f["id"]}"></script>'
            h = h.replace('</body>', js + '</body>', 1) if '</body>' in h else h + js
            (out / f"{f['id']}.html").write_text(h)

        await asyncio.gather(*(one(f) for f in self.frames))
        return len(self.frames)

    def serve(self):
        handler = functools.partial(_NoCache, directory=str(self.dir))
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f'http://127.0.0.1:{self.server.server_address[1]}/frames/'
        return self.base

    def close(self):
        # an attached browser is the user's own: close only this session's tab, never the browser
        self.ab(*(('tab', 'close') if self.cdp else ('close',)))
        if self.server:
            self.server.shutdown(); self.server.server_close(); self.server = None
        shutil.rmtree(self.dir, ignore_errors=True)

    # ------------------------------------------------------------ browser
    def ab(self, *args, timeout=30):
        r = subprocess.run([*self.abargs, *map(str, args)], capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()

    def ready(self):
        # player.js runs after Doop's render-blocking webfont stylesheet; a click before `load` hits no listener
        self.ab('wait', '--fn', "document.readyState === 'complete'")

    def open(self, fid, width):
        self.ab('set', 'viewport', width, 900)
        # on a just-launched browser the viewport change aborts the next navigation (net::ERR_ABORTED)
        for _ in range(2):
            if 'Navigation failed' not in self.ab('open', self.base + f'{fid}.html'):
                break
        self.ready()

    def find(self, text=None, sel=None):
        self.ready()
        out = self.ab('eval', FIND_JS % (json.dumps(text), json.dumps(sel)))
        try: return json.loads(json.loads(out))
        except Exception: return {'error': out[:300]}

    def click(self, text=None, sel=None):
        f = self.find(text, sel)
        if 'error' in f: return f
        self.ab('mouse', 'move', round(f['x']), round(f['y']))
        self.ab('mouse', 'down'); self.ab('mouse', 'up')
        time.sleep(0.6)
        return f

    def here(self):
        u = self.ab('get', 'url'); m = re.search(r'/frames/([^/]+)\.html', u)
        ov = self.ab('eval', "(document.querySelector('#doop-overlay iframe')||{}).src||''")
        om = re.search(r'/frames/([^/]+)\.html', ov)
        return (m.group(1) if m else u), (om.group(1) if om else None)

    # ------------------------------------------------------------ journeys
    def run(self, name, v):
        M, (start, steps) = self.spec['M'], self.spec['JOURNEYS'][name]
        other = ds.SIBLING[v]
        resolve = lambda k: self.vid(M[k[6:]], other) if k.startswith('OTHER:') else self.vid(M[k], v)
        remap = lambda s: s and re.sub(r'((?:navigate|overlay):)([A-Za-z0-9_-]+)', lambda m: m.group(1) + self.vid(m.group(2), v), s)
        self.open(resolve(start), ds.WIDTH[v])
        trail = [start]
        for target, exp in steps:
            if target == 'GOTO':
                self.ab('eval', f"location.href='{resolve(exp)}.html'"); time.sleep(0.6); trail.append('goto ' + exp); continue
            kind = target[0] if isinstance(target, tuple) else 'label'
            label, sel = (target, None) if kind == 'label' else (None, remap(target[1]))
            if kind == 'opt' and 'error' in self.find(sel=sel): continue
            f = self.click(label, sel)
            if 'error' in f and v.startswith('phone'):
                # a phone menu opens as an overlay or by navigating to the menu frame
                trig = ','.join(['[data-doop-action^="overlay:"]'] + [f'[data-doop-action="navigate:{m}"]' for m in sorted(self.menus[v])])
                f = self.click(sel=trig)
                if 'error' in f: return False, trail, f'no menu trigger for {target!r}'
                time.sleep(0.8)
                cur, ov = self.here()
                if (ov or cur) not in self.menus[v]: return False, trail, f'menu opened {ov or cur} ({self.name.get(ov or cur)}), not a {v} menu'
                f = self.click(label, sel)
            if 'error' in f: return False, trail, f'click {target!r}: {f}'
            if f.get('covered'): return False, trail, f"{target!r} covered by {f['coveredBy']}"
            if exp is None: trail.append('stay'); continue
            cur, ov = self.here()
            if cur != resolve(exp): return False, trail, f'{target!r} -> {self.name.get(cur, cur)} (overlay {ov}), expected {exp}'
            trail.append(exp)
        return True, trail, ''

    def journeys(self, variants=VARIANTS, names=None):
        rep = []
        for v in variants:
            for n in names or self.spec['JOURNEYS']:
                if v not in self.spec.get('ONLY', {}).get(n, variants): continue
                ok, trail, why = self.run(n, v)
                rep.append((v, n, ok, len(trail) - 1, why))
        return rep

    # ------------------------------------------------------------ crawl
    def crawl(self, fid, width, skip=None):
        self.open(fid, width)
        out = self.ab('eval', CRAWL_JS % json.dumps(skip), timeout=60)
        try: return json.loads(json.loads(out))
        except Exception: return {'error': out[:300]}

    def crawl_all(self, skip=None):
        """frame name -> problems (covered/small/missing scroll targets, overflow at 390) plus its unwired visible links.
        skip: CSS for visible links that are unwired on purpose; defaults to the config's crawl_skip."""
        skip = self.cfg['crawl_skip'] if skip is None else skip
        out = {}
        for f in self.frames:
            v = ds.split(f['name'])[1]
            r = self.crawl(f['id'], ds.WIDTH[v], skip)
            if 'error' in r: out[f['name']] = {'error': r['error']}; continue
            p = {'covered': [(w['label'], w['covered']) for w in r['wired'] if w['visible'] and w['covered']],
                 'small': [w['label'] for w in r['wired'] if w['small']],
                 'missingScroll': [a for w in r['wired'] for a in w['missingScroll']],
                 'overflowX': r['overflowX'] and ds.WIDTH[v] == 390,
                 'unwired': r['unwired']}
            out[f['name']] = {k: x for k, x in p.items() if x}
        return out

