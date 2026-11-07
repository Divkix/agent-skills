"""Find the Doop frames behind the screens a user names, and flag ones edited too recently to build from.

Runs inside omp's Python eval with doop-variants' scripts on sys.path (SKILL.md, Setup):

    found, unknown = await screens.find(cfg, call, read, ['Home', 'Pricing'])

A name matches a screen (`Home` matches `Home - /` and its states like `Home · empty - /`) or one exact frame base
name. Each row of `found`:
  screen, state, route  parsed from the frame name `Screen[ · state] - /route`
  kind                  'master' (desktop light is the source) or 'phone-only' (the ` · phone` frame is)
  source                id of the hand-edited frame to build from
  variants              variant -> frame id (light, dark, phone, phone-dark)
  recent                names of this screen's frames edited in the last `quiet_minutes`
`unknown` lists the names that matched nothing.
"""
import datetime as dt
import pathlib
import sys

# doop-variants is installed beside this skill; resolve() follows a symlinked install back to the real folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'doop-variants' / 'scripts'))
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
                              variants={v: f['id'] for v, f in fam.items()},
                              recent=sorted(f['name'] for f in fam.values() if edited_since(f, cutoff))))
    return found, sorted(n for k, n in want.items() if k not in hit)


async def find(cfg, call, read, names, quiet_minutes=10):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=quiet_minutes)
    return pick(await ds.get_frames(cfg, call, read), names, cutoff)


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
    print('screens selftest ok')


if __name__ == '__main__':
    selftest()
