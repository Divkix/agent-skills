"""Doop 4-variant sync: one hand-edited master per screen, generated dark, phone and phone-dark copies.

Per screen only the desktop light master (1440) is edited by hand; ` · dark`, ` · phone` and ` · phone · dark` are
generated from it. Phone-only screens (menus, drawers): `X · phone` is the hand-edited source, `X · phone · dark`
is generated. Frames pair by name: base = name minus the variant suffix. Frames named `Option <X> · …` are design
options waiting for a pick: get_frames skips them, so no sync, click test or build ever sees them.

Each app keeps its settings in its own repo at `.doop/config.json`. Doop sits behind the MCP portal, reachable only
through the omp harness, so this runs inside omp's Python eval:

    call = doop_sync.portal(tool)
    await doop_sync.main(['~/GitHub/app'], call, read)                         # dry run: report only
    await doop_sync.main(['~/GitHub/app', '--write'], call, read)              # apply
    await doop_sync.main(['~/GitHub/app', '--create', '--write'], call, read)  # also add missing copies

Flags: --write apply; --force overwrite copies someone edited by hand; --create add missing copies (blank, then
filled in the same run); --only id,id limit to the families containing these frame ids; --layout move frames to
the standard rows (masters y=0, dark row, phone row with phone dark at x+520).

Copies carry `<meta name="doop-sync" content="<digest>">`: the digest of their normalised content when last
synced. A copy whose current content no longer matches its digest was edited by hand (drift) and is skipped
unless --force. A master edit changes the wanted copy, not the copy, so it is never mistaken for drift.

`python3 doop_sync.py` runs the offline self-check.
"""
import asyncio, base64, gzip, hashlib, json, pathlib, re


def load(app):
    """The app's settings from <app>/.doop/config.json, plus `name` (the repo folder name) and `root`."""
    root = pathlib.Path(app).expanduser().resolve()
    cfg = json.loads((root / '.doop' / 'config.json').read_text())
    return {'pages': None, 'crawl_skip': None, **cfg, 'name': root.name, 'root': root}


SUFFIX = (('phone-dark', ' · phone · dark'), ('phone', ' · phone'), ('dark', ' · dark'))
DARK = {'dark', 'phone-dark'}
SIBLING = {'light': 'dark', 'dark': 'light', 'phone': 'phone-dark', 'phone-dark': 'phone'}
WIDTH = {'light': 1440, 'dark': 1440, 'phone': 390, 'phone-dark': 390}

HTML_TAG = re.compile(r'<html\b[^>]*>', re.I)
HEAD_TAG = re.compile(r'<head\b[^>]*>', re.I)
LINK = re.compile(r'((?:navigate|overlay):)([A-Za-z0-9_-]+)')
META = re.compile(r'<meta name="doop-sync" content="([^"]*)">')
FONTS = re.compile(r'<link\b[^>]*data-doop-webfonts[^>]*>')


# ---------------------------------------------------------------- pure transforms

def split(name):
    for v, s in SUFFIX:
        if name.endswith(s):
            return name[:-len(s)], v
    return name, 'light'


def set_theme(h, dark):
    def fix(m):
        t = re.sub(r'\s+data-doop-theme="[^"]*"', '', m.group(0))
        return t[:-1] + ' data-doop-theme="dark">' if dark else t
    return HTML_TAG.sub(fix, h, count=1)


def remap(h, ids):
    """Rewrite navigate:/overlay: targets (attributes and data-doop-interactions JSON alike). Unknown ids stay."""
    return LINK.sub(lambda m: m.group(1) + ids.get(m.group(2), m.group(2)), h)


def _toggle_re(lit):
    # (?<=\s): attribute inside a tag only, never a CSS attribute selector like [data-cf-theme="dark"]
    return re.compile(r'(?<=\s)' + re.escape(lit) + r'(?:="")?(?![\w-])'
                      r'(?:\s+data-doop-on="click"\s+data-doop-action="navigate:[A-Za-z0-9_-]+")?')


def wire(h, toggles, targets):
    """Set or clear the navigate wiring right after each theme marker. targets: role -> frame id or None."""
    for lit, role in toggles.items():
        t = targets.get(role)
        rep = lit + (f' data-doop-on="click" data-doop-action="navigate:{t}"' if t else '')
        h = _toggle_re(lit).sub(lambda _m: rep, h)
    return h


def norm(h, toggles):
    h = FONTS.sub('', META.sub('', h))
    return set_theme(wire(LINK.sub(r'\1X', h), toggles, {}), False)


def digest(h, toggles):
    return hashlib.sha1(norm(h, toggles).encode()).hexdigest()[:12]


def stamp(h, toggles):
    tag = f'<meta name="doop-sync" content="{digest(h, toggles)}">'
    h = META.sub('', h)
    return HEAD_TAG.sub(lambda m: m.group(0) + tag, h, count=1) if HEAD_TAG.search(h) else tag + h


def drifted(cur, want, toggles):
    """True when a copy was edited by hand since its last sync. Blank frames (just created) never count."""
    m = META.search(cur)
    if m:
        return m.group(1) != digest(cur, toggles)
    if re.search(r'<body[^>]*>\s*</body>', cur, re.I):
        return False
    return norm(cur, toggles) != norm(want, toggles)  # legacy copy without a stamp


# ---------------------------------------------------------------- planning

def plan(frames):
    fams, dupes = {}, []
    for f in frames:
        base, v = split(f['name'])
        if v in fams.setdefault(base, {}):
            dupes.append(f['name'])
        fams[base][v] = f
    masters = {b: m for b, m in fams.items() if 'light' in m}
    phone_only = {b: m for b, m in fams.items() if 'light' not in m and 'phone' in m}
    orphans = sorted(f['name'] for m in fams.values() if 'light' not in m and 'phone' not in m for f in m.values())
    missing = [(b, v) for b, m in masters.items() for v in ('dark', 'phone', 'phone-dark') if v not in m]
    missing += [(b, 'phone-dark') for b, m in phone_only.items() if 'phone-dark' not in m]
    return masters, phone_only, orphans, missing, dupes


def id_maps(masters, phone_only):
    maps = {}
    for v in ('dark', 'phone', 'phone-dark'):
        ids = {f['id']: m[v]['id'] for m in masters.values() if v in m for f in m.values()}
        tv = 'phone-dark' if v in DARK else 'phone'
        ids |= {f['id']: m[tv]['id'] for m in phone_only.values() if tv in m for f in m.values()}
        maps[v] = ids
    return maps


def targets(fam, v):
    sib = fam.get(SIBLING[v])
    sid = sib['id'] if sib else None
    return {'other': sid, 'light': sid if v in DARK else None, 'dark': None if v in DARK else sid}


def wanted(masters, phone_only, html, toggles):
    """frame id -> wanted HTML, plus the set of generated-copy ids (the only ones the drift guard applies to)."""
    maps, want, copies = id_maps(masters, phone_only), {}, set()
    for fam in masters.values():
        src = fam['light']
        if src['id'] not in html:
            continue
        h = html[src['id']]
        want[src['id']] = wire(h, toggles, targets(fam, 'light'))  # masters: toggle wiring only
        for v in ('dark', 'phone', 'phone-dark'):
            if v in fam:
                want[fam[v]['id']] = stamp(wire(remap(set_theme(h, v in DARK), maps[v]), toggles, targets(fam, v)), toggles)
                copies.add(fam[v]['id'])
    for fam in phone_only.values():
        src = fam['phone']
        if src['id'] not in html:
            continue
        h = html[src['id']]
        want[src['id']] = wire(remap(h, maps['phone']), toggles, targets(fam, 'phone'))
        if 'phone-dark' in fam:
            want[fam['phone-dark']['id']] = stamp(wire(remap(set_theme(h, True), maps['phone-dark']), toggles, targets(fam, 'phone-dark')), toggles)
            copies.add(fam['phone-dark']['id'])
    return want, copies


def sizes(masters, phone_only):
    """frame id -> (w, h) wanted: dark copies take their source's size; phone dark takes its phone frame's."""
    out = {}
    for fam in masters.values():
        if 'dark' in fam:
            out[fam['dark']['id']] = (WIDTH['dark'], fam['light']['height'])
        for v in ('phone', 'phone-dark'):
            if v in fam:
                h = fam['phone']['height'] if 'phone' in fam else fam['light']['height']
                out[fam[v]['id']] = (WIDTH[v], h)
    for fam in phone_only.values():
        if 'phone-dark' in fam:
            out[fam['phone-dark']['id']] = (WIDTH['phone-dark'], fam['phone']['height'])
    return out


def _round(n, step=200):
    return -(-n // step) * step


def rows(page_frames):
    """Row y per variant for one page: existing rows win, else stack below the tallest frame of the row above."""
    by_v = {}
    for f in page_frames:
        by_v.setdefault(split(f['name'])[1], []).append(f)
    top = lambda v: min((f['y'] for f in by_v.get(v, [])), default=None)
    tall = lambda vs: max((f['height'] for v in vs for f in by_v.get(v, [])), default=900)
    y_dark = top('dark') if top('dark') is not None else _round(tall(['light']) + 400)
    y_phone = top('phone') if top('phone') is not None else _round(y_dark + tall(['dark', 'light']) + 400)
    return {'light': 0, 'dark': y_dark, 'phone': y_phone, 'phone-dark': y_phone}


def layout(frames):
    """frame id -> (x, y) for the standard grid. Masters keep their left-to-right order; phone-only sources
    take the slots after the last master."""
    out = {}
    for page in {f['pageId'] for f in frames}:
        pf = [f for f in frames if f['pageId'] == page]
        masters, phone_only, *_ = plan(pf)
        y = {'light': 0}
        y['dark'] = _round(max((m['light']['height'] for m in masters.values()), default=900) + 400)
        dark_h = max((m['dark']['height'] for m in masters.values() if 'dark' in m), default=0)
        y['phone'] = y['phone-dark'] = _round(y['dark'] + max(dark_h, 900) + 400)
        slots = (sorted(masters.values(), key=lambda m: (m['light']['x'], m['light']['y']))
                 + sorted(phone_only.values(), key=lambda m: (m['phone']['x'], m['phone']['y'])))
        for i, fam in enumerate(slots):
            x = i * 1600
            for v, f in fam.items():
                out[f['id']] = (x + (520 if v == 'phone-dark' else 0), y[v])
    return out


# ---------------------------------------------------------------- Doop I/O

def _text(r):
    return r['text'] if isinstance(r, dict) else str(r)


def _parse(r, read):
    t = _text(r)
    m = re.search(r'Read (artifact://\d+) for full output', t)
    if m:
        full = read(m.group(1))
        t = _text(full) if isinstance(full, dict) else str(full)
    return json.JSONDecoder().raw_decode(t[t.index('{'):])[0]


# The portal's code mode cuts every response near 24,000 characters, and its get_canvas lists frames without
# pageId, x, y or updatedAt. So each result is gzipped inside the sandbox and split across calls when it still
# doesn't fit (each part reruns the Doop call), and get_canvas is rebuilt from every frame's get_frame.
PORTAL = 'mcp__mcp_portal_portal_codemode_execute'
PART = 23000
JS_PACK = r"""
const text = (r) => typeof r === 'string' ? r : Array.isArray(r) ? r.map((c) => c.text ?? '').join('\n') : JSON.stringify(r);
const pack = async (s) => {
  const b = new Uint8Array(await new Response(new Blob([s]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
  let bin = '';
  for (let i = 0; i < b.length; i += 0x8000) bin += String.fromCharCode(...b.subarray(i, i + 0x8000));
  const z = btoa(bin);
  return JSON.stringify({ parts: Math.ceil(z.length / PART), z: z.slice(PART_I * PART, (PART_I + 1) * PART) });
};
"""
JS_DETAILS = r"""
const one = async (id) => {
  for (let i = 0; ; i++) {
    try {
      const t = text(await codemode.doop_get_frame({ frame_id: id, agent_name: AGENT }));
      const f = JSON.parse(t.slice(t.indexOf('{')));
      delete f.html;
      return f;
    } catch (e) {
      if (i === 3) throw e;
      await new Promise((ok) => setTimeout(ok, 1500 * (i + 1)));
    }
  }
};
return JSON.stringify(await Promise.all(IDS.map(one)));
"""


async def _run(ex, body):
    """The full text of the Doop result that JS `body` returns, run in the portal sandbox."""
    parts = []
    while True:
        code = (f'async () => {{ const PART = {PART}, PART_I = {len(parts)};{JS_PACK}'
                f'try {{ return await pack(text(await (async () => {{ {body} }})())); }}'
                ' catch (e) { return JSON.stringify({ error: String(e?.message ?? e) }); } }')
        r = json.loads(_text(await ex({'code': code})))
        if 'error' in r:
            raise RuntimeError(r['error'])
        parts.append(r['z'])
        if len(parts) == r['parts']:
            return gzip.decompress(base64.b64decode(''.join(parts))).decode()


def portal(tool):
    """`call(name, args)` for Doop through the MCP portal's code mode, with whole results."""
    ex = getattr(tool, PORTAL)

    async def call(name, args):
        body = f'return codemode.doop_{name}({json.dumps(args)});'
        if name != 'get_canvas':
            return {'text': await _run(ex, body)}
        c = json.loads(await _run(ex, body))
        ids, agent, frames = [f['id'] for f in c['frames']], json.dumps(args.get('agent_name')), []
        for i in range(0, len(ids), 100):  # about 20 s per 100 frames
            frames += json.loads(await _run(ex, f'const IDS = {json.dumps(ids[i:i + 100])}, AGENT = {agent};{JS_DETAILS}'))
        return {'text': json.dumps({**c, 'frames': frames})}

    return call


async def _get_html(call, read, fid, agent):
    for wait in (2, 4, 6, None):
        try:
            j = _parse(await call('get_frame', {'frame_id': fid, 'agent_name': agent}), read)
            return j.get('html') or j.get('frame', {}).get('html', '')
        except Exception:
            if wait is None:
                raise
            await asyncio.sleep(wait)


async def _write(call, name, args):
    t = _text(await call(name, args))
    if re.match(r'\s*(error|invalid|failed)', t, re.I) or '"error"' in t[:200]:
        raise RuntimeError(f'{name} {args.get("frame_id", args.get("name"))}: {t[:200]}')
    await asyncio.sleep(0.35)
    return t


OPTION = re.compile(r'Option [A-Z0-9]+ · ')


async def get_frames(cfg, call, read):
    c = _parse(await call('get_canvas', {'canvas_id': cfg['canvas_id'], 'agent_name': cfg['agent']}), read)
    return [f for f in c['frames']
            if (cfg['pages'] is None or f['pageId'] in cfg['pages']) and not OPTION.match(f['name'])]


async def tokens_css(cfg, call):
    """The canvas colour tokens as CSS: `:root` light values plus the dark theme block."""
    t = _text(await call('get_tokens', {'canvas_id': cfg['canvas_id'], 'format': 'css', 'agent_name': cfg['agent']}))
    return t[:t.rfind('}') + 1]


async def pull(cfg, call, read, fid, path):
    """Save a frame's HTML to a file, so a big frame is edited on disk instead of passing through the chat, plus the
    canvas tokens as tokens.css beside it (preview.py renders with them)."""
    p = pathlib.Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(await _get_html(call, read, fid, cfg['agent']))
    p.with_name('tokens.css').write_text(await tokens_css(cfg, call))
    return str(p)


async def push(cfg, call, fid, path, height=None):
    """Replace a hand-edited frame's HTML with the file's content; optionally set its height."""
    h = pathlib.Path(path).expanduser().read_text()
    assert 'data-doop-theme' not in (HTML_TAG.search(h) or [''])[0], 'hand-edited frames carry no theme on <html>'
    out = [await _write(call, 'set_frame_html', {'frame_id': fid, 'html': h, 'agent_name': cfg['agent']})]
    if height:
        out.append(await _write(call, 'update_frame', {'frame_id': fid, 'height': int(height), 'agent_name': cfg['agent']}))
    return [t[:160] for t in out]


async def sync(cfg, call, read, write=False, force=False, create=False, only=None):
    a = cfg['agent']
    frames = await get_frames(cfg, call, read)
    masters, phone_only, orphans, missing, dupes = plan(frames)
    created = []
    if create and missing and write:
        by_page = {}
        for f in frames:
            by_page.setdefault(f['pageId'], []).append(f)
        for base, v in missing:
            fam = masters.get(base) or phone_only[base]
            src = fam.get('light') or fam['phone']
            if only and not ({f['id'] for f in fam.values()} & only):
                continue
            ry = rows(by_page[src['pageId']])
            x = (fam['phone']['x'] if 'phone' in fam else src['x']) + 520 if v == 'phone-dark' else src['x']
            h = (fam['phone']['height'] if 'phone' in fam else src['height']) if v.startswith('phone') else src['height']
            t = await _write(call, 'create_frame', {'canvas_id': cfg['canvas_id'], 'pageId': src['pageId'],
                             'name': base + dict(SUFFIX)[v], 'html': '<!doctype html><html><head></head><body></body></html>',
                             'x': x, 'y': ry[v], 'width': WIDTH[v], 'height': h, 'agent_name': a})
            created.append((base + dict(SUFFIX)[v], re.search(r'"id":\s*"([^"]+)"', t).group(1)))
        frames = await get_frames(cfg, call, read)
        masters, phone_only, orphans, missing, dupes = plan(frames)

    fams = list(masters.values()) + list(phone_only.values())
    if only:
        fams = [m for m in fams if {f['id'] for f in m.values()} & only]
    ids = [f['id'] for m in fams for f in m.values()]
    sem = asyncio.Semaphore(4)

    async def fetch(fid):
        async with sem:
            return fid, await _get_html(call, read, fid, a)
    html = dict(await asyncio.gather(*(fetch(i) for i in ids)))
    sel_m = {b: m for b, m in masters.items() if m in fams}
    sel_p = {b: m for b, m in phone_only.items() if m in fams}
    # id maps span every family so --only still remaps links to unselected screens; wanted() skips unfetched sources
    want, copies = wanted(masters, phone_only, html, cfg['toggles'])
    names = {f['id']: f['name'] for f in frames}
    writes, drift = [], []
    for fid, new in want.items():
        cur = html[fid]
        if cur == new:
            continue
        if fid in copies and drifted(cur, new, cfg['toggles']) and not force:
            drift.append(names[fid])
            continue
        writes.append(fid)
    size = {f['id']: (f['width'], f['height']) for f in frames}
    resize = {fid: wh for fid, wh in sizes(sel_m, sel_p).items() if size[fid] != wh}

    rep = dict(masters=len(masters), phone_only=len(phone_only), copies=len(copies), orphans=orphans,
               missing=[f'{b} [{v}]' for b, v in missing], dupes=dupes, created=created,
               writes=[names[f] for f in writes], drift=drift, resize=[names[f] for f in resize])
    if write:
        for fid in writes:
            await _write(call, 'set_frame_html', {'frame_id': fid, 'html': want[fid], 'agent_name': a})
        for fid, (w, h) in resize.items():
            await _write(call, 'update_frame', {'frame_id': fid, 'width': w, 'height': h, 'agent_name': a})
    return rep


async def relayout(cfg, call, read, write=False):
    frames = await get_frames(cfg, call, read)
    pos = layout(frames)
    moves = {f['id']: pos[f['id']] for f in frames if f['id'] in pos and (f['x'], f['y']) != pos[f['id']]}
    if write:
        for fid, (x, y) in moves.items():
            await _write(call, 'update_frame', {'frame_id': fid, 'x': x, 'y': y, 'agent_name': cfg['agent']})
    names = {f['id']: f['name'] for f in frames}
    return dict(moves=[f'{names[f]} -> {xy}' for f, xy in moves.items()])


async def main(argv, call, read):
    """argv: [app repo path, *flags]."""
    cfg, flags = load(argv[0]), argv[1:]
    key = cfg['name']
    write = '--write' in flags
    if '--layout' in flags:
        rep = await relayout(cfg, call, read, write)
    else:
        only = set(flags[flags.index('--only') + 1].split(',')) if '--only' in flags else None
        rep = await sync(cfg, call, read, write, '--force' in flags, '--create' in flags, only)
    print(f"{key} {'WRITE' if write else 'dry run'}:")
    for k, v in rep.items():
        print(f'  {k}: {v if not isinstance(v, list) else f"{len(v)} {v[:40]}"}')
    return rep


# ---------------------------------------------------------------- offline self-check

def selftest():
    tg = {'data-t': 'other'}
    m = {'id': 'M', 'name': 'Home - /', 'height': 900}
    d = {'id': 'D', 'name': 'Home - / · dark', 'height': 1}
    p = {'id': 'P', 'name': 'Home - / · phone', 'height': 2000}
    pd = {'id': 'PD', 'name': 'Home - / · phone · dark', 'height': 5}
    mp = {'id': 'MP', 'name': 'Menu · phone', 'height': 800}
    mpd = {'id': 'MPD', 'name': 'Menu · phone · dark', 'height': 800}
    masters, po, orphans, missing, dupes = plan([m, d, p, pd, mp, mpd, {'id': 'O', 'name': 'Gone · dark', 'height': 1}])
    assert list(masters) == ['Home - /'] and list(po) == ['Menu'] and orphans == ['Gone · dark'] and not missing and not dupes
    h = ('<html lang="en"><head></head><body><button data-t>t</button>'
         '<a data-doop-on="click" data-doop-action="navigate:M">a</a><b data-doop-action="overlay:MP">m</b>'
         """<i data-doop-interactions='[{"on":"click","action":"navigate:M"}]'>i</i></body></html>""")
    want, copies = wanted(masters, po, {'M': h, 'MP': h}, tg)
    assert copies == {'D', 'P', 'PD', 'MPD'}
    assert 'data-t data-doop-on="click" data-doop-action="navigate:D"' in want['M'] and 'navigate:M"' in want['M']
    assert want['D'].count('navigate:D') == 2 and 'overlay:MPD' in want['D'] and 'data-doop-theme="dark"' in want['D']
    assert 'data-t data-doop-on="click" data-doop-action="navigate:M"' in want['D']
    assert want['P'].count('navigate:P"') == 2 and 'overlay:MP"' in want['P'] and 'data-doop-theme' not in want['P']
    assert 'data-doop-action="navigate:PD"' in want['P'] and 'overlay:MPD' in want['PD'] and 'navigate:P"' in want['PD']
    assert '"action":"navigate:PD"' in want['PD']
    assert 'data-doop-action="navigate:MPD"' in want['MP'] and 'data-doop-action="navigate:MP"' in want['MPD']
    # drift guard: untouched copy is safe even when the master changes; a hand edit is caught
    assert not drifted(want['D'], want['D'].replace('>a<', '>b<'), tg)
    assert drifted(want['D'].replace('>a<', '>hand edit<'), want['D'], tg)
    assert not drifted(set_theme(h, True), want['D'], tg) and drifted('<html><body>x</body></html>', want['D'], tg)
    assert not drifted('<!doctype html><html><head></head><body></body></html>', want['D'], tg)
    assert stamp(want['D'], tg).count('doop-sync') == 1 and wire(wire(h, tg, {'other': 'X'}), tg, {'other': 'Y'}).count('navigate:Y') == 1
    roles = {'data-x="light"': 'light', 'data-x="dark"': 'dark'}
    seg = '<html><body><a data-x="light">L</a><a data-x="dark">D</a></body></html>'
    assert wire(seg, roles, targets({'dark': d, 'light': m}, 'light')).count('navigate:') == 1
    assert 'data-x="light" data-doop-on="click" data-doop-action="navigate:M"' in wire(seg, roles, targets({'dark': d, 'light': m}, 'dark'))
    css = '<style>.t [data-x="dark"]{color:red}</style>'
    assert wire(css + seg, roles, {'dark': 'D'}).startswith(css)  # CSS attribute selectors are never wired
    assert sizes(masters, po) == {'D': (1440, 900), 'P': (390, 2000), 'PD': (390, 2000), 'MPD': (390, 800)}
    assert OPTION.match('Option B · Pricing · annual - /pricing') and not OPTION.match('Options - /settings/options')

    # portal: gzip parts reassemble, get_canvas carries each frame's get_frame details, errors raise
    big = ''.join(hashlib.sha256(str(i).encode()).hexdigest() for i in range(1500))
    brief = {'canvas': {'id': 'C'}, 'frames': [{'id': 'A', 'name': 'a'}, {'id': 'B', 'name': 'b'}]}
    details = [{'id': 'A', 'pageId': 'p', 'x': 0, 'y': 0, 'updatedAt': 't'},
               {'id': 'B', 'pageId': 'p', 'x': 1600, 'y': 0, 'updatedAt': 't'}]

    class Tool:
        async def mcp__mcp_portal_portal_codemode_execute(self, a):
            code = a['code']
            if 'doop_boom' in code:
                return {'text': json.dumps({'error': 'boom failed'})}
            s = json.dumps(details) if 'const IDS' in code else json.dumps(brief) if 'doop_get_canvas' in code else big
            z = base64.b64encode(gzip.compress(s.encode(), mtime=0)).decode()
            i = int(re.search(r'PART_I = (\d+)', code).group(1))
            return {'text': json.dumps({'parts': -(-len(z) // PART), 'z': z[i * PART:(i + 1) * PART]})}

    call = portal(Tool())
    assert len(base64.b64encode(gzip.compress(big.encode()))) > 2 * PART
    assert asyncio.run(call('get_frame', {'frame_id': 'A'}))['text'] == big
    c = _parse(asyncio.run(call('get_canvas', {'canvas_id': 'C', 'agent_name': 'x'})), None)
    assert c['canvas'] == {'id': 'C'} and c['frames'] == details, c
    try:
        asyncio.run(call('boom', {}))
        raise AssertionError('portal error not raised')
    except RuntimeError as e:
        assert str(e) == 'boom failed'
    print('doop_sync selftest ok')


if __name__ == '__main__':
    selftest()
