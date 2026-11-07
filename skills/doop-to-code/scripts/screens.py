"""Find the Doop frames behind the screens a user names, flag ones edited too recently, and keep the app's build stamp.

Runs inside omp's Python eval with doop-design's scripts on sys.path (SKILL.md, Setup):

    found, unknown = await screens.find(cfg, call, read, ['Home', 'Pricing'])
    todo = await screens.changed(cfg, call, read)  # what changed on Doop since the last build
    screens.stamp(cfg, row, path)                  # after building row from the frame saved at path

A name matches a screen (`Home` matches `Home - /` and its states like `Home · empty - /`) or one exact frame base
name. Each row of `found`:
  screen, state, route  parsed from the frame name `Screen[ · state] - /route`
  name                  the frame base name `Screen[ · state] - /route`, as `changed` reports it
  kind                  'master' (desktop light is the source) or 'phone-only' (the ` · phone` frame is)
  source, updatedAt     id and last edit time of the hand-edited frame to build from
  variants              variant -> frame id (light, dark, phone, phone-dark)
  recent                names of this screen's frames edited in the last `quiet_minutes`
`unknown` lists the names that matched nothing.

The build stamp `<app>/.doop/built.json` holds, per source frame built, its name, updatedAt and a hash of its HTML,
plus a hash of the canvas colour tokens. It is committed with the code, so the commit that last changed a frame's
hash is the commit that built that design.
"""
import datetime as dt
import hashlib
import json
import pathlib
import sys

# doop-design is installed beside this skill; resolve() follows a symlinked install back to the real folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'doop-design' / 'scripts'))
import doop_sync as ds  # noqa: E402


def parse(base):
    """'Edit Resume · saving - /edit' -> ('Edit Resume', 'saving', '/edit')."""
    title, _, route = base.partition(' - ')
    screen, _, state = title.partition(' · ')
    return screen, state, route


def edited_since(f, cutoff):
    return dt.datetime.fromisoformat(f['updatedAt'].replace('Z', '+00:00')) > cutoff


def pick(frames, names, cutoff):
    masters, phone_only, *_ = ds.plan(frames)
    want, hit, found = {n.casefold(): n for n in names}, set(), []
    for kind, fams, src in (('master', masters, 'light'), ('phone-only', phone_only, 'phone')):
        for base, fam in sorted(fams.items()):
            screen, state, route = parse(base)
            keys = {screen.casefold(), base.casefold()} & want.keys()
            if not keys:
                continue
            hit |= keys
            found.append(dict(screen=screen, state=state, route=route, kind=kind, source=fam[src]['id'],
                              name=base, updatedAt=fam[src]['updatedAt'],
                              variants={v: f['id'] for v, f in fam.items()},
                              recent=sorted(f['name'] for f in fam.values() if edited_since(f, cutoff))))
    return found, sorted(n for k, n in want.items() if k not in hit)


async def find(cfg, call, read, names, quiet_minutes=10):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=quiet_minutes)
    return pick(await ds.get_frames(cfg, call, read), names, cutoff)


BUILT = '.doop/built.json'


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def built(cfg):
    """The app's build stamp: {'tokens': sha, 'frames': {source id: {name, updatedAt, sha}}}; empty before the first build."""
    p = pathlib.Path(cfg['root']) / BUILT
    return json.loads(p.read_text()) if p.exists() else {'tokens': None, 'frames': {}}


def stamp(cfg, row, path):
    """Record that row's screen is built from the frame saved at path (tokens.css beside it); commit BUILT with the code."""
    path, b = pathlib.Path(path), built(cfg)
    b['tokens'] = digest(path.with_name('tokens.css').read_text())
    b['frames'][row['source']] = dict(name=row['name'], updatedAt=row['updatedAt'], sha=digest(path.read_text()))
    (pathlib.Path(cfg['root']) / BUILT).write_text(json.dumps(b, indent=2, ensure_ascii=False, sort_keys=True) + '\n')


def diff(frames, b):
    """(new, gone, moved): source frames never built, built names gone from the canvas, built sources whose
    updatedAt moved (moved -> frame id; their HTML still has to be compared, a drag also moves updatedAt)."""
    masters, phone_only, *_ = ds.plan(frames)
    src = {fam[s]['id']: (base, fam[s]) for fams, s in ((masters, 'light'), (phone_only, 'phone'))
           for base, fam in fams.items()}
    new = sorted(base for i, (base, _) in src.items() if i not in b['frames'])
    gone = sorted(e['name'] for i, e in b['frames'].items() if i not in src)
    moved = {base: i for i, (base, f) in src.items() if i in b['frames'] and f['updatedAt'] != b['frames'][i]['updatedAt']}
    return new, gone, moved


async def changed(cfg, call, read):
    """What to build since the last stamp: {'changed', 'new', 'gone': frame names, 'tokens': canvas colours changed}."""
    b = built(cfg)
    new, gone, moved = diff(await ds.get_frames(cfg, call, read), b)
    edited = [n for n, i in sorted(moved.items())
              if digest(await ds._get_html(call, read, i, cfg['agent'])) != b['frames'][i]['sha']]
    tokens = b['tokens'] is not None and digest(await ds.tokens_css(cfg, call)) != b['tokens']
    return dict(changed=edited, new=new, gone=gone, tokens=tokens)


def selftest():
    old, new = '2026-01-01T00:00:00.000Z', '2026-01-01T00:20:00.000Z'
    fr = lambda i, n, t=old: {'id': i, 'name': n, 'updatedAt': t}
    frames = [fr('H', 'Home - /'), fr('HD', 'Home - / · dark'), fr('HE', 'Home · empty - /', new),
              fr('M', 'Menu - / · phone'), fr('MD', 'Menu - / · phone · dark'), fr('A', 'About - /about')]
    cutoff = dt.datetime(2026, 1, 1, 0, 10, tzinfo=dt.timezone.utc)
    found, unknown = pick(frames, ['home', 'Menu', 'Pricing'], cutoff)
    assert [(r['screen'], r['state'], r['route'], r['kind'], r['source']) for r in found] == [
        ('Home', '', '/', 'master', 'H'), ('Home', 'empty', '/', 'master', 'HE'), ('Menu', '', '/', 'phone-only', 'M')]
    assert found[0]['variants'] == {'light': 'H', 'dark': 'HD'} and found[0]['recent'] == []
    assert found[1]['recent'] == ['Home · empty - /'] and unknown == ['Pricing']
    assert pick(frames, ['Home · empty - /'], cutoff)[0][0]['source'] == 'HE'
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        cfg, page = {'root': d}, pathlib.Path(d) / 'H.html'
        (pathlib.Path(d) / '.doop').mkdir()
        page.write_text('<p>home</p>')
        page.with_name('tokens.css').write_text(':root{}')
        stamp(cfg, found[0], page)
        b = built(cfg)
        assert b['frames']['H'] == {'name': 'Home - /', 'updatedAt': old, 'sha': digest('<p>home</p>')}
        assert b['tokens'] == digest(':root{}') and diff(frames, b)[2] == {}
    b['frames']['X'] = {'name': 'Old - /old', 'updatedAt': old, 'sha': ''}
    dragged = [dict(f, updatedAt=new) if f['id'] == 'H' else f for f in frames]
    assert diff(dragged, b) == (['About - /about', 'Home · empty - /', 'Menu - /'], ['Old - /old'],
                                {'Home - /': 'H'})
    print('screens selftest ok')


if __name__ == '__main__':
    selftest()
