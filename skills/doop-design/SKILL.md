---
name: doop-design
description: Design or change screens on an app's Doop canvas as desktop light masters, 1440 wide, that adapt to phone and take every colour from the canvas tokens, or as options to pick from. Use whenever asked to design, mock up, redesign, add or edit a screen or page on a Doop canvas whose app repo has `.doop/config.json`, to make design options for a screen, or to set up a new app's canvas. Its canvas rules, settings and scripts are shared with doop-sync and doop-to-code.
---

# Doop design

Per screen only the desktop light **master** (1440 wide) is designed; its `@media (max-width:639px)` block is the phone layout. This skill makes and changes masters only. The ` · dark`, ` · phone` and ` · phone · dark` copies belong to doop-sync, which the user runs after reviewing the masters, so existing copies stay as they are, stale or not, until then. Each app keeps its own settings in its repo under `.doop/`.

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

`<repo>/.doop/journeys.json`: doop-sync's click-through journeys; the format is at the top of `scripts/e2e.py`. No `.doop/` yet: ask for the canvas id, write both files, and commit them on a branch in the app repo.

## Canvas rules

doop-sync and doop-to-code read these too.

- **Names:** `Screen[ · state] - /route[ · phone][ · dark]`, separator ` - ` before the route. Frames pair by name, so renaming a master means renaming its copies in the same pass.
- **Options:** design options waiting for a pick are named `Option <letter> · Screen[ · state] - /route`. The scripts skip them, so doop-sync never copies them and doop-to-code never builds them.
- **Masters:** colours only through canvas tokens (`var(--color-*)`, `color-mix(in oklab, …)`, `transparent`, `currentColor`); no hex/rgb/hsl/oklch literal anywhere, SVG attributes included. Exception: artwork of a fixed palette (template thumbnails) declares each colour once as `--art-*`. Never `data-doop-theme` or `class="dark"` on `<html>`; a dark-only tweak goes under `html[data-doop-theme="dark"] .x`.
- **One responsive DOM:** the phone layout lives in the master's `@media (max-width:639px)`, no horizontal overflow at 390, app shells `min-height:100vh` (frame height = viewport height).
- **Phone-only screens** (menus, drawers): `X · phone` is the hand-edited source; its ` · phone · dark` is generated.
- **Copies change only through the sync.** A copy whose content no longer matches its sync stamp is reported as drift and skipped; the fix goes into the master.
- **Theme switch:** put the marker attribute on the button and leave its `data-doop-*` wiring to the sync; never write another `data-doop-*` attribute right after the marker. The selected segment comes from CSS (`html[data-doop-theme="dark"] [marker]`), not a class.
- **Links:** masters link to masters (and phone menus link to phone menus); the sync remaps every `navigate:` / `overlay:` id per variant. The Doop player follows only `navigate:`, `back`, `overlay:`, `close-overlay`, `scroll-to:` and `url:` in `data-doop-action` / `data-doop-interactions`; it never follows `href` and has no theme action.
- **Approval:** any HTML or size change clears a frame's approval, so the sync writes only frames whose wanted HTML differs.

## Running it

Doop sits behind the MCP portal and is reachable only from omp's Python eval. Setup cell, with the absolute path of this skill's `scripts/` folder:

```python
import sys; sys.path.insert(0, '<skill dir>/scripts'); import doop_sync
call = doop_sync.portal(tool)
APP = '~/GitHub/<repo>'; cfg = doop_sync.load(APP)
```

**New screen:** `create_frame` 1440 wide on the app's page, named by the Names rule, then build it as in "Edit a master" (pull the blank frame and write the whole design into the file). The design is one page that adapts to phone; a separate phone frame only for phone-only screens.

**Options** (asked for several designs to choose from): one 1440-wide frame per option, named by the Options rule, side by side on the screen's page, each built like a new screen. When the user picks one:

- new screen: rename the winner to its plain name (`update_frame` with `name`), then delete the other options;
- existing screen: pull the winner and push its HTML into the existing master, so the master keeps its id, links and copies, then delete every option.

**Edit a master** (frames run to 50 KB; never paste them through the chat):

1. `await doop_sync.pull(cfg, call, read, fid, '/tmp/doop-edit/<fid>.orig.html')`, then copy it to `<fid>.html` and edit that file. `pull` writes `tokens.css` beside it.
2. `python3 -I <skill dir>/scripts/preview.py /tmp/doop-edit/<fid>.html --app <repo> --orig /tmp/doop-edit/<fid>.orig.html` renders light/dark × 1440/390 PNGs and lints. Read the PNGs; iterate until `LINT OK` and no `OVERFLOW`.
3. `await doop_sync.push(cfg, call, fid, path, height=<light-1440 height>)`, then `get_frame_screenshot` (it returns the frame's `image_url`, a PNG you can `read`) and fix what Doop's render shows.

**Done** when every master or option you touched is pushed, its Doop render checked, and `/tmp/doop-edit` deleted.

## Report

The masters changed and the options waiting for a pick, each with its frame link. Then the next step for the user: review them on Doop, and run `/skill:doop-sync` to make and click-test the copies.

## Doop quirks

- `get_frame_screenshot` sometimes renders before webfonts load (wider wrapping, clipped bottom): take another screenshot; never change layout or height for a fallback-font render.
- HTTP 429: wait a few seconds; stay under about one call per second.
- The portal cuts every response near 24,000 characters, and its `get_canvas` lists frames without `pageId`, `x`, `y` or `updatedAt`. `call(name, args)` returns whole results (gzipped in transit; `get_canvas` rebuilt from each frame's `get_frame`, about 20 s per 100 frames), so make every Doop call through it, and parse Doop JSON with `doop_sync._parse(result, read)`.
