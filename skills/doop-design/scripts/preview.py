#!/usr/bin/env python3
"""Render a hand-edited frame file the way Doop will (canvas tokens injected) in the 4 variants light/dark x
1440/390, then lint it.

usage: python3 preview.py FILE.html [--app REPO] [--orig ORIG.html] [--only light-1440,dark-390]

Needs tokens.css beside FILE (doop_sync.pull writes it). --app reads the theme-toggle markers from
REPO/.doop/config.json. Writes FILE.<variant>.png beside FILE. Prints per variant the content height and horizontal
overflow, then:
  colours  hex/rgb/hsl/oklch literals outside --art-* declarations (must be 0)
  theme    class="dark" / data-doop-theme on <html> (must be absent)
  wiring   actions the --orig frame had that FILE lost (must be 0; theme-toggle wiring belongs to the sync)
  markers  how often each theme-toggle marker appears
"""
import json, pathlib, re, subprocess, sys, tempfile
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # -I drops the script dir from sys.path
import doop_sync as ds

VARIANTS = {'light-1440': (False, 1440), 'dark-1440': (True, 1440), 'light-390': (False, 390), 'dark-390': (True, 390)}
ACT = re.compile(r'data-doop-action="([^"]+)"|&quot;action&quot;:\s*&quot;(.+?)&quot;|"action"\s*:\s*"([^"]+)"')
TOK_TAG = re.compile(r'<style\b[^>]*\bdata-doop-tokens\b[^>]*>.*?</style>', re.S)


def variant_html(h, tokens, dark):
    h = ds.set_theme(TOK_TAG.sub('', h), dark)  # Doop stores its own token block once a frame uses tokens; render with ours only
    tag = f'<style data-doop-tokens>{tokens}</style>'
    return ds.HEAD_TAG.sub(lambda m: m.group(0) + tag, h, count=1) if ds.HEAD_TAG.search(h) else tag + h


def ab(session, *args, timeout=90):
    r = subprocess.run(['agent-browser', '--session', session, *args], capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()


def shoot(session, url, w, png):
    """Full-page screenshot of url at width w once webfonts load; returns {h, w, png}: content height and scrollWidth."""
    ab(session, 'set', 'viewport', str(w), '844' if w == 390 else '900')  # phone frames are 844 tall; Doop's 100vh = frame height
    for _ in range(2):  # on a just-launched browser the viewport change aborts the next navigation
        if 'Navigation failed' not in ab(session, 'open', url):
            break
    ab(session, 'wait', '--load', 'networkidle', timeout=40)
    m = ab(session, 'eval', 'document.fonts.ready.then(() => new Promise(r => requestAnimationFrame(() => r(JSON.stringify({h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth})))))')
    ab(session, 'screenshot', '--full', str(png))
    try:
        dims = json.loads(json.loads(m) if m.startswith('"') else m)
    except Exception:
        dims = {'raw': m[:200]}
    return {**dims, 'png': png}


def actions(h):
    return Counter(a or b or c for a, b, c in ACT.findall(h))


def lint(h, orig, toggles):
    h = TOK_TAG.sub('', h)
    css = ' '.join(re.findall(r'<style\b[^>]*>(.*?)</style>', h, re.S)) + ' ' + ' '.join(re.findall(r'\bstyle="([^"]*)"', h))
    css += ' ' + ' '.join(re.findall(r'\b(?:fill|stroke|stop-color|color|bgcolor)="([^"]*)"', h))
    css = re.sub(r'--art-[\w-]+\s*:[^;}]*', '', css)
    colours = sorted(set(re.findall(r'#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch|hwb)\([^)]*\)', css)))
    html_tag = (ds.HTML_TAG.search(h) or [''])[0]
    theme = [x for x in ('class="dark"', 'data-doop-theme') if x in html_tag]
    lost = []
    if orig:
        o, n = actions(ds.wire(orig, toggles, {})), actions(ds.wire(h, toggles, {}))
        lost = [f'{a} x{c - n[a]}' for a, c in o.items() if n[a] < c]
    markers = {lit: len(ds._toggle_re(lit).findall(h)) for lit in toggles}
    return dict(colours=colours, theme=theme, lost_wiring=lost, markers=markers)


def main(argv):
    path = pathlib.Path(argv[0]).resolve()
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    tokens = path.with_name('tokens.css')
    if not tokens.exists():
        sys.exit(f'{tokens} missing: doop_sync.pull() writes it beside the frame file')
    toggles = ds.load(opt('--app'))['toggles'] if opt('--app') else {}
    orig = pathlib.Path(opt('--orig')).read_text() if opt('--orig') else None
    h, tk = path.read_text(), tokens.read_text()
    session = 'doop-preview-' + re.sub(r'[^A-Za-z0-9]', '', path.stem)[:24]
    with tempfile.TemporaryDirectory() as tmp:
        for v in (opt('--only') or ','.join(VARIANTS)).split(','):
            dark, w = VARIANTS[v]
            f = pathlib.Path(tmp) / f'{v}.html'
            f.write_text(variant_html(h, tk, dark))
            dims = shoot(session, f.as_uri(), w, path.with_name(f'{path.stem}.{v}.png'))
            print(f'{v}: height {dims.get("h")} | scrollWidth {dims.get("w")}{"  OVERFLOW" if dims.get("w", w) > w else ""} | {dims["png"]}')
        ab(session, 'close')
    rep = lint(h, orig, toggles)
    for k, v in rep.items():
        print(f'{k}: {v}')
    print('LINT OK' if not (rep['colours'] or rep['theme'] or rep['lost_wiring']) else 'LINT FAIL')


if __name__ == '__main__':
    main(sys.argv[1:])
