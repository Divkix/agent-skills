#!/usr/bin/env python3
"""Screenshot a running app beside the Doop frame it should match, in the 4 variants light/dark x 1440/390.

usage: python3 -I compare.py URL FRAME.html [--only light-1440,dark-390] [--session NAME]

FRAME.html is a frame saved with doop_sync.pull (tokens.css beside it). The Doop side renders exactly like
doop-variants' preview.py (dark = data-doop-theme on <html>, phone = 390 wide); the app side loads URL with the
browser's colour scheme set to the variant's, so an app that follows the system theme switches with it.
Writes beside FRAME:
  FRAME.<variant>.doop.png, FRAME.<variant>.app.png   the two full-page screenshots
  FRAME.<variant>.compare.png                         both side by side: Doop left, app right
and prints per variant both heights and the app's scrollWidth (OVERFLOW when wider than the viewport).
--session reuses a named agent-browser session (one already signed in, say) and leaves it open.
"""
import pathlib
import re
import sys
import tempfile

# doop-variants is installed beside this skill; resolve() follows a symlinked install back to the real folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'doop-variants' / 'scripts'))
import preview  # noqa: E402

GAP = 24


def side_by_side(session, left, right, w, out, tmp):
    cell = lambda label, png: (f'<figure style="margin:0;width:{w}px"><figcaption style="font:600 20px sans-serif;'
                               f'padding:0 0 8px">{label}</figcaption><img src="{png.as_uri()}" style="display:block;'
                               f'width:{w}px"></figure>')
    page = pathlib.Path(tmp) / 'compare.html'
    page.write_text(f'<html><body style="margin:0;padding:{GAP}px;display:flex;gap:{GAP}px;align-items:flex-start;'
                    f'background:#d4d4d4">{cell("Doop", left)}{cell("App", right)}</body></html>')
    return preview.shoot(session, page.as_uri(), 2 * w + 3 * GAP, out)


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
            dark, w = preview.VARIANTS[v]
            out = lambda kind: path.with_name(f'{path.stem}.{v}.{kind}.png')
            f = pathlib.Path(tmp) / f'{v}.html'
            f.write_text(preview.variant_html(h, tk, dark))
            preview.ab(session, 'set', 'media', 'dark' if dark else 'light')
            d = preview.shoot(session, f.as_uri(), w, out('doop'))
            a = preview.shoot(session, url, w, out('app'))
            side_by_side(session, d['png'], a['png'], w, out('compare'), tmp)
            over = '  OVERFLOW' if a.get('w', w) > w else ''
            print(f'{v}: doop height {d.get("h")} | app height {a.get("h")} | app scrollWidth {a.get("w")}{over}'
                  f' | {out("compare")}')
        if not opt('--session'):
            preview.ab(session, 'close')


if __name__ == '__main__':
    main(sys.argv[1:])
