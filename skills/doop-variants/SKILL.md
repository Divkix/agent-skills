---
name: doop-variants
description: Keep a Doop design canvas at four frames per screen (desktop light, desktop dark, phone, phone dark) from one hand-edited master, and click-test its prototype locally. Use when editing, adding or syncing screens on a Doop canvas that has ` · dark` / ` · phone` copies, when asked to "sync the Doop copies", generate dark or phone versions, click-test or crawl a Doop prototype, or set up a new app's canvas this way.
---

# Doop variants

Per screen only the desktop light **master** (1440 wide) is edited by hand. `scripts/doop_sync.py` generates ` · dark`, ` · phone` and ` · phone · dark` from it; `scripts/e2e.py` exports the canvas and clicks through it in a local browser. Each app keeps its own settings in its repo under `.doop/`.

Call Doop `get_guide` once before any Doop work, and use the config's `agent` as `agent_name` on every call.

## App settings

`<repo>/.doop/config.json`:

| Key | Meaning |
|---|---|
| `canvas_id` | The Doop canvas |
| `agent` | `agent_name` for every Doop call, scripts included |
| `toggles` | Theme-switch marker attribute → role. `other`: one button that flips to the sibling theme. `light` / `dark`: segments of a switch, wired only where they change the theme |
| `pages` | Optional page ids to sync and test; default every page |
| `crawl_skip` | Optional CSS for visible links that are unwired on purpose |

`<repo>/.doop/journeys.json`: click-through journeys; the format is at the top of `scripts/e2e.py`. A new flow on the canvas gets a journey here. No `.doop/` yet: ask for the canvas id, write both files, and commit them on a branch in the app repo.

## Canvas rules the scripts depend on

- **Names:** `Screen[ · state] - /route[ · phone][ · dark]`, separator ` - ` before the route. Frames pair by name, so renaming a master means renaming its copies in the same pass.
- **Masters:** colours only through canvas tokens (`var(--color-*)`, `color-mix(in oklab, …)`, `transparent`, `currentColor`); no hex/rgb/hsl/oklch literal anywhere, SVG attributes included. Exception: artwork of a fixed palette (template thumbnails) declares each colour once as `--art-*`. Never `data-doop-theme` or `class="dark"` on `<html>`; a dark-only tweak goes under `html[data-doop-theme="dark"] .x`.
- **One responsive DOM:** the phone layout lives in the master's `@media (max-width:639px)`, no horizontal overflow at 390, app shells `min-height:100vh` (frame height = viewport height).
- **Phone-only screens** (menus, drawers): `X · phone` is the hand-edited source; its ` · phone · dark` is generated.
- **Copies are never edited by hand.** A copy whose content no longer matches its sync stamp is reported as drift and skipped; fix the master instead, and use `--force` only after the user agrees to lose the hand edit.
- **Theme switch:** put the marker attribute on the button and leave its `data-doop-*` wiring to the sync; never write another `data-doop-*` attribute right after the marker. The selected segment comes from CSS (`html[data-doop-theme="dark"] [marker]`), not a class.
- **Links:** masters link to masters (and phone menus link to phone menus); the sync remaps every `navigate:` / `overlay:` id per variant. The Doop player follows only `navigate:`, `back`, `overlay:`, `close-overlay`, `scroll-to:` and `url:` in `data-doop-action` / `data-doop-interactions`; it never follows `href` and has no theme action.
- **Approval:** any HTML or size change clears a frame's approval, so the sync writes only frames whose wanted HTML differs.

## Running it

Doop is reachable only from omp's Python eval. Setup cell, with the absolute path of this skill's `scripts/` folder:

```python
import sys; sys.path.insert(0, '<skill dir>/scripts'); import doop_sync, e2e
call = lambda name, args: getattr(tool, 'mcp__doop_' + name)(args)
APP = '~/GitHub/<repo>'; cfg = doop_sync.load(APP)
```

**Edit a master** (frames run to 50 KB; never paste them through the chat):

1. `await doop_sync.pull(cfg, call, read, fid, '/tmp/doop-edit/<fid>.orig.html')`, then copy it to `<fid>.html` and edit that file. `pull` writes `tokens.css` beside it.
2. `python3 -I <skill dir>/scripts/preview.py /tmp/doop-edit/<fid>.html --app <repo> --orig /tmp/doop-edit/<fid>.orig.html` renders light/dark × 1440/390 PNGs and lints. Read the PNGs; iterate until `LINT OK` and no `OVERFLOW`.
3. `await doop_sync.push(cfg, call, fid, path, height=<light-1440 height>)`, then `get_frame_screenshot` and fix what Doop's render shows.

**Sync** after any master change:

1. Dry run `await doop_sync.main([APP], call, read)`: masters, copies, orphans, missing, writes, drift, resize.
2. `await doop_sync.main([APP, '--write'], call, read)`; add `--create` when new masters need their copies, `--only id,id` to limit the run, `--layout` (dry run first) to move frames to the standard rows.
3. Dry run again: it must report 0 writes, 0 drift, 0 missing.

**Verify** (done = all of these):

1. `get_prototype`: 0 missing targets.
2. Click test and crawl:
   ```python
   h = e2e.Harness(APP, call, read); await h.load(); await h.export(); h.serve()
   rep = h.journeys(); bad = h.crawl_all(); h.close()
   ```
   `rep` rows are `(variant, journey, ok, clicks, why)`; every row must pass. `bad` maps frame names to covered or tiny targets, missing scroll targets, overflow at 390 and unwired visible links. Expected noise: off-screen rows in wide tables on phone, elements behind an open modal. The default browser is a private headless session; `cdp=<port>` attaches to the user's browser, where another focused tab can swallow clicks.
3. Screenshot every changed frame and fix clipping, contrast and frame height.
4. `h.close()` ran, and `/tmp/doop-edit` is deleted.

## Doop quirks

- `get_frame_screenshot` sometimes renders before webfonts load (wider wrapping, clipped bottom): take another screenshot; never change layout or height for a fallback-font render.
- HTTP 429: wait a few seconds; stay under about one call per second.
- Large `get_canvas` / `get_frame` output is cut off in omp; the scripts follow its `Read artifact://N` pointer, so parse Doop JSON through `doop_sync._parse(result, read)` in your own cells too.
- The hosted prototype player (`/c/<canvas>/proto`) needs a signed-in account, so automation can't click it; that's what the local harness is for.
