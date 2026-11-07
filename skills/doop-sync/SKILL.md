---
name: doop-sync
description: Make and update the dark, phone and phone-dark copies of every master on an app's Doop canvas, wire their links and theme switch, and click-test the prototype locally in all four versions. Use when asked to sync the Doop copies, make dark or phone versions, click-test or crawl a Doop prototype, or check that a canvas is in sync. Needs doop-design installed beside it.
---

# Doop sync

The canvas follows doop-design's "App settings" and "Canvas rules" (read both): per screen the desktop light master is the design the user reviewed. This skill generates ` · dark`, ` · phone` and ` · phone · dark` from each master with `doop_sync.py`, then clicks through all four versions in a local browser with `e2e.py`. The masters stay exactly as the user left them: a design problem you find goes into the report, and the user fixes the master with doop-design, then syncs again.

Call Doop `get_guide` once before any Doop work, and use the config's `agent` as `agent_name` on every call.

## Setup

Doop sits behind the MCP portal and is reachable only from omp's Python eval. The scripts live in doop-design's `scripts/` folder, next to this skill's folder. Setup cell, with that folder's absolute path:

```python
import sys; sys.path.insert(0, '<doop-design dir>/scripts'); import doop_sync, e2e
call = doop_sync.portal(tool)
APP = '~/GitHub/<repo>'; cfg = doop_sync.load(APP)
```

Make every Doop call through `call(name, args)` (doop-design's "Doop quirks").

## Sync

1. Dry run `await doop_sync.main([APP], call, read)`: masters, copies, orphans, missing, writes, drift, resize. `drift` lists copies someone edited by hand: show them to the user, and add `--force` only once they agree to lose the hand edit. `orphans` (copies without a master) and `dupes` (two frames with one name) go to the user as well. Frames named `Option <X> · …` are options waiting for a pick and are skipped; when the user expected one synced, they pick it first with doop-design.
2. `await doop_sync.main([APP, '--write'], call, read)`; add `--create` when masters lack their copies, `--only id,id` to limit the run, `--layout` (dry run first) to move frames to the standard rows.
3. Dry run again: it must report 0 writes, 0 missing, and drift only where the user chose to keep a hand edit.

## Verify

Done = all of these:

1. `get_prototype`: 0 missing targets.
2. Every flow on the canvas has a journey in `.doop/journeys.json` (format at the top of `scripts/e2e.py`). Click test and crawl:
   ```python
   h = e2e.Harness(APP, call, read); await h.load(); await h.export(); h.serve()
   rep = h.journeys(); bad = h.crawl_all(); h.close()
   ```
   `rep` rows are `(variant, journey, ok, clicks, why)`; every row must pass. `bad` maps frame names to covered or tiny targets, missing scroll targets, overflow at 390 and unwired visible links. Expected noise: off-screen rows in wide tables on phone, elements behind an open modal. The default browser is a private headless session; `cdp=<port>` attaches to the user's browser, where another focused tab can swallow clicks.
3. Every written or created copy screenshotted (`get_frame_screenshot` returns its `image_url`, a PNG you can `read`), with each clipping, contrast or height problem noted against its master.
4. `h.close()` ran.

## Report

What the sync wrote and created, drift kept and why, then every failing journey row, crawl finding and screenshot problem, each against the master the user should fix with doop-design. Nothing failing: say the canvas is ready for doop-to-code.

## Quirks

- The hosted prototype player (`/c/<canvas>/proto`) needs a signed-in account, so automation can't click it; that's what the local harness is for.
