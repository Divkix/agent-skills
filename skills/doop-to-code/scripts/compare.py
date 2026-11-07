#!/usr/bin/env python3
"""Measure a running app against the Doop frame it should match, in the 4 variants light/dark x 1440/390.

usage: python3 -I compare.py URL FRAME.html [--only light-1440,dark-390] [--session NAME]
       python3 -I compare.py --selftest

FRAME.html is a frame saved with doop_sync.pull (tokens.css beside it). The Doop side renders exactly like
doop-design's preview.py (dark = data-doop-theme on <html>, phone = 390 wide); the app side loads URL with the
browser's colour scheme set to the variant's, so an app that follows the system theme switches with it. Both sides
are measured with CSS animations, transitions and smooth scrolling off, in the same browser.
Prints per variant:
  height   both page heights and the app's scrollWidth (OVERFLOW when wider than the viewport)
  slices   the share of pixels that differ in each screen-high slice, top down, by Doop scroll position
  text     each text on both pages whose size, weight, line height, letter spacing, font, colour, box or wording
           differs; a move is measured against the text before it, so one section that is too tall is reported
           once; text that differs only slightly (a line break, a curly quote) still pairs, with its app wording
  missing  text only the Doop frame has; "only in app": text only the app has
  fonts    web fonts that failed to load on either side (the numbers are wrong until that is fixed)
Writes beside FRAME:
  FRAME.<variant>.compare.png        both full pages side by side: Doop left, app right
  FRAME.<variant>.slice-<y>.png      each differing slice at full size: Doop left, app right
  FRAME.<variant>.slice-<y>.red.png  where that slice differs, in red
--session reuses a named agent-browser session (one already signed in, say) and leaves it open.
--selftest checks the checker: a page against itself reads 0, a resized heading and a missing paragraph don't.
"""
import json
import pathlib
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from difflib import SequenceMatcher

# doop-design is installed beside this skill; resolve() follows a symlinked install back to the real folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'doop-design' / 'scripts'))
import preview  # noqa: E402

GAP = 24
NEAR = 4  # px a box may differ by before it is reported
TINT = 8  # per-channel colour difference (0-255) before it is reported
SHOW = 25  # text rows printed per variant

STILL = ("document.head.insertAdjacentHTML('beforeend', '<style>*,*::before,*::after{animation:none!important;"
         "transition:none!important;caret-color:transparent!important}html{scroll-behavior:auto!important}</style>')")

SCROLL = """(async () => {
  scrollTo(0, Y_);
  const seen = [...document.images].filter(i => { const b = i.getBoundingClientRect(); return !i.complete && b.bottom > 0 && b.top < innerHeight; });
  const load = seen.map(i => new Promise(r => { i.addEventListener('load', r, {once: true}); i.addEventListener('error', r, {once: true}); }));
  await Promise.race([Promise.all(load), new Promise(r => setTimeout(r, 3000))]);
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  return JSON.stringify(scrollY);
})()"""

# Every element with its own text: [text, x, y, w, h, font size, weight, line height, letter spacing, font, colour].
# The box is the text's own (a Range), not the element's, so a wider block with the same lines reads the same.
TEXTS = r"""(() => {
  const cv = document.createElement('canvas').getContext('2d', {willReadFrequently: true});
  const rgba = c => { cv.clearRect(0, 0, 1, 1); cv.fillStyle = '#000'; cv.fillStyle = c; cv.fillRect(0, 0, 1, 1); return [...cv.getImageData(0, 0, 1, 1).data]; };
  const r = document.createRange(), out = [];
  for (const el of document.body.querySelectorAll('*')) {
    if (/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE)$/.test(el.tagName)) continue;
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const s = getComputedStyle(el);
    if (s.visibility !== 'visible' || +s.opacity === 0) continue;
    const e = el.getBoundingClientRect();
    if (e.width < 2 || e.height < 2) continue;  // a 1px "skip to content" link
    r.selectNodeContents(el);
    const b = r.getBoundingClientRect();
    if (b.width < 2 || b.height < 2) continue;
    out.push([el.textContent.replace(/\s+/g, ' ').trim().slice(0, 80), Math.round(b.left + scrollX), Math.round(b.top + scrollY),
      Math.round(b.width), Math.round(b.height), parseFloat(s.fontSize), s.fontWeight, s.lineHeight,
      s.letterSpacing === 'normal' ? '0px' : s.letterSpacing, s.fontFamily.split(',')[0].replace(/["']/g, '').trim(), rgba(s.color)]);
  }
  const bad = [...document.fonts].filter(f => f.status === 'error').map(f => f.family.replace(/["']/g, ''));
  return JSON.stringify({texts: out, bad: [...new Set(bad)]});
})()"""


def js(session, code):
    m = preview.ab(session, 'eval', code)
    try:
        v = json.loads(m)
        return json.loads(v) if isinstance(v, str) else v
    except ValueError:
        sys.exit(f'agent-browser eval failed: {m[:300]}')


def side_by_side(session, cells, w, out, tmp):
    """cells: (label, png) pairs shown left to right at width w each."""
    cell = lambda label, png: (f'<figure style="margin:0;width:{w}px"><figcaption style="font:600 20px sans-serif;'
                               f'padding:0 0 8px">{label}</figcaption><img src="{png.as_uri()}" style="display:block;'
                               f'width:{w}px"></figure>')
    page = pathlib.Path(tmp) / 'compare.html'
    page.write_text(f'<html><body style="margin:0;padding:{GAP}px;display:flex;gap:{GAP}px;align-items:flex-start;'
                    f'background:#d4d4d4">{"".join(cell(*c) for c in cells)}</body></html>')
    return preview.shoot(session, page.as_uri(), len(cells) * (w + GAP) + GAP, out)


def capture(session, url, w, png):
    """Load url at width w with motion off; returns its dims and texts, and leaves it open at the top."""
    dims = preview.shoot(session, url, w, png)
    preview.ab(session, 'eval', STILL)
    preview.ab(session, 'screenshot', '--full', str(png))  # again, now that animations are off
    return dims, js(session, TEXTS)


def px(v):
    return float(v[:-2]) if v.endswith('px') else None


def notes(d, a, shift):
    """What differs between one Doop text and its app counterpart; shift is how far the text before it moved."""
    n = []
    if abs(d[5] - a[5]) > 0.5:
        n.append(f'size {d[5]:g} -> {a[5]:g}px')
    if d[6] != a[6]:
        n.append(f'weight {d[6]} -> {a[6]}')
    for name, i, tol in (('line height', 7, 1), ('letter spacing', 8, 0.2)):
        p, q = px(d[i]), px(a[i])
        if (abs(p - q) > tol) if p is not None and q is not None else d[i] != a[i]:
            n.append(f'{name} {d[i]} -> {a[i]}')
    if d[9].lower() != a[9].lower():
        n.append(f'font {d[9]} -> {a[9]}')
    if max(abs(x - y) for x, y in zip(d[10], a[10])) > TINT:
        hexa = lambda c: '#' + ''.join(f'{x:02x}' for x in (c if c[3] < 255 else c[:3]))
        n.append(f'colour {hexa(d[10])} -> {hexa(a[10])}')
    jump = (a[2] - d[2]) - shift
    if abs(jump) > NEAR:
        n.append(f'{abs(jump)}px {"lower" if jump > 0 else "higher"}, relative to the text before it')
    if abs(a[1] - d[1]) > NEAR:
        n.append(f'{abs(a[1] - d[1])}px further {"right" if a[1] > d[1] else "left"}')
    for name, i in (('width', 3), ('height', 4)):
        if abs(a[i] - d[i]) > NEAR:
            n.append(f'{name} {d[i]} -> {a[i]}')
    return n


def pair(doop, app):
    """Pair texts by content in reading order; returns (rows that differ, Doop-only texts, app-only texts)."""
    # ponytail: pairs by text only; textless parts (icons, photos, shapes) are covered by the slice pixels
    order = lambda t: (t[2], t[1])
    left = defaultdict(list)
    for t in sorted(app, key=order):
        left[t[0]].append(t)
    pairs, missing = [], []
    for d in sorted(doop, key=order):
        (pairs.append((d, left[d[0]].pop(0))) if left[d[0]] else missing.append(d))
    extra = sorted((t for ts in left.values() for t in ts), key=order)
    like = lambda d, a: SequenceMatcher(None, d[0], a[0]).ratio()
    for d in list(missing):  # the same text but for a line break, a curly quote or spacing
        a = max(extra, key=lambda a: like(d, a), default=None)
        if a and like(d, a) >= 0.8:
            missing.remove(d)
            extra.remove(a)
            pairs.append((d, a))
    rows, shift = [], 0
    for d, a in sorted(pairs, key=lambda p: order(p[0])):
        n = ([f'wording "{a[0]}"'] if a[0] != d[0] else []) + notes(d, a, shift)
        if n:
            rows.append((d, n))
        shift = a[2] - d[2]
    return rows, missing, extra


def compare(session, url, h, tk, v, out, tmp):
    """One variant: both pages shot, sliced and measured. out(kind) names a result file."""
    dark, w = preview.VARIANTS[v]
    tmp = pathlib.Path(tmp)
    f = tmp / f'{v}.html'
    f.write_text(preview.variant_html(h, tk, dark))
    preview.ab(session, 'set', 'media', 'dark' if dark else 'light')
    d, dt = capture(session, f.as_uri(), w, out('doop'))
    vh = js(session, 'innerHeight')
    cuts = []
    for y in range(0, max(d.get('h') or vh, 1), vh):
        png = tmp / f'{v}-{y}.png'
        cuts.append((js(session, SCROLL.replace('Y_', str(y))), png))
        preview.ab(session, 'screenshot', str(png))
    a, at = capture(session, url, w, out('app'))
    slices = []
    for dy, png in cuts:
        ay = js(session, SCROLL.replace('Y_', str(dy)))
        red = tmp / f'{v}-{dy}.red.png'
        m = preview.ab(session, '--json', 'diff', 'screenshot', '--baseline', str(png), '--output', str(red))
        r = (json.loads(m).get('data') or {}) if m.startswith('{') else {}
        s = dict(y=dy, app_y=ay, pixels=r.get('differentPixels'), pct=r.get('mismatchPercentage'),
                 size=r.get('dimensionMismatch'), doop=png, red=red, app=tmp / f'{v}-{dy}.app.png')
        if s['pixels'] != 0:
            preview.ab(session, 'screenshot', str(s['app']))
        slices.append(s)
    side_by_side(session, [('Doop', d['png']), ('App', a['png'])], w, out('compare'), tmp)
    for old in out('slice-').parent.glob(out('slice-').name.replace('.png', '*.png')):
        old.unlink()
    for s in slices:
        if s['pixels'] != 0:
            s['png'] = side_by_side(session, [('Doop', s['doop']), ('App', s['app'])], w, out(f'slice-{s["y"]}'), tmp)['png']
            if s['red'].exists():
                shutil.copyfile(s['red'], out(f'slice-{s["y"]}.red'))
    rows, missing, extra = pair(dt['texts'], at['texts'])
    return dict(v=v, w=w, doop=d, app=a, slices=slices, rows=rows, missing=missing, extra=extra,
                matched=len(dt['texts']) - len(missing), fonts=(dt['bad'], at['bad']), compare=out('compare'))


def show(rep):
    d, a, w = rep['doop'], rep['app'], rep['w']
    over = '  OVERFLOW' if a.get('w', w) > w else ''
    print(f'{rep["v"]}: height Doop {d.get("h")} | app {a.get("h")} | app scrollWidth {a.get("w")}{over}'
          f' | {rep["compare"]}')
    cell = lambda s: (f'{s["y"]}' + (f' (app {s["app_y"]})' if s['app_y'] != s['y'] else '') + ' '
                      + ('size differs' if s['size'] else 'error' if s['pixels'] is None
                         else '0' if s['pixels'] == 0 else f'{s["pct"]:.2f}%'))
    print('  slices: ' + ' | '.join(cell(s) for s in rep['slices']))
    clip = lambda t: f'"{t[0][:48]}{"…" if len(t[0]) > 48 else ""}"'
    print(f'  text: {rep["matched"]} on both, {len(rep["rows"])} differ')
    for t, n in rep['rows'][:SHOW]:
        print(f'    y {t[2]} {clip(t)}  ' + '; '.join(n))
    if len(rep['rows']) > SHOW:
        print(f'    +{len(rep["rows"]) - SHOW} more')
    for label, ts in (('missing in app', rep['missing']), ('only in app', rep['extra'])):
        if ts:
            print(f'  {label}: ' + ', '.join(f'{clip(t)} (y {t[2]})' for t in ts[:12])
                  + (f', +{len(ts) - 12} more' if len(ts) > 12 else ''))
    if any(rep['fonts']):
        print(f'  fonts failed: Doop {rep["fonts"][0]} | app {rep["fonts"][1]}')


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    url, path = argv[0], pathlib.Path(argv[1]).resolve()
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    tokens = path.with_name('tokens.css')
    if not tokens.exists():
        sys.exit(f'{tokens} missing: doop_sync.pull() writes it beside the frame file')
    h, tk = path.read_text(), tokens.read_text()
    session = opt('--session') or 'doop-compare-' + re.sub(r'[^A-Za-z0-9]', '', path.stem)[:24]
    with tempfile.TemporaryDirectory() as tmp:
        for v in (opt('--only') or ','.join(preview.VARIANTS)).split(','):
            show(compare(session, url, h, tk, v, lambda kind: path.with_name(f'{path.stem}.{v}.{kind}.png'), tmp))
        if not opt('--session'):
            preview.ab(session, 'close')


def selftest():
    frame = ('<!doctype html><html><head><style>*{margin:0;box-sizing:border-box}body{background:var(--color-bg);'
             'color:var(--color-fg);font:16px/24px sans-serif}h1{font-size:48px;line-height:56px;margin:40px}'
             'p{margin:0 40px;height:1400px}</style></head><body><h1>Hello there</h1><p>Body copy</p></body></html>')
    tokens = ':root{--color-bg:#ffffff;--color-fg:#15171a}[data-doop-theme="dark"]{--color-bg:#0e0f14;--color-fg:#eceef3}'
    session = 'doop-compare-selftest'
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)

        def run(app_frame, name):
            f = tmp / f'{name}.html'
            f.write_text(preview.variant_html(app_frame, tokens, False))
            return compare(session, f.as_uri(), frame, tokens, 'light-1440', lambda kind: tmp / f'{name}.{kind}.png', tmp)

        same = run(frame, 'same')
        assert len(same['slices']) == 2 and all(s['pixels'] == 0 for s in same['slices']), same['slices']
        assert same['rows'] == same['missing'] == same['extra'] == [] and same['matched'] == 2, same
        skip = ('<body><a href="#m" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">'
                'Skip to content</a>')
        small = run(frame.replace('font-size:48px', 'font-size:44px').replace('Body copy', 'Body copy!')
                    .replace('<body>', skip), 'small')
        assert small['slices'][0]['pixels'] > 0 and (tmp / 'small.slice-0.png').exists(), small['slices']
        assert (tmp / 'small.slice-0.red.png').exists() and small['missing'] == small['extra'] == [], small
        assert [r[0][0] for r in small['rows']] == ['Hello there', 'Body copy'], small['rows']
        assert 'size 48 -> 44px' in small['rows'][0][1] and small['rows'][1][1][0] == 'wording "Body copy!"', small['rows']
        gone = run(frame.replace('<p>Body copy</p>', ''), 'gone')
        assert [t[0] for t in gone['missing']] == ['Body copy'] and gone['extra'] == [], gone
        preview.ab(session, 'close')
    print('compare selftest ok')


if __name__ == '__main__':
    selftest() if sys.argv[1:] == ['--selftest'] else main(sys.argv[1:])
