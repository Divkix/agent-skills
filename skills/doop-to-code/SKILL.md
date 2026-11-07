---
name: doop-to-code
description: Build screens from a Doop design canvas into an app's real code, then screenshot the running app beside each Doop frame (light/dark × desktop/phone) until they match. Use when asked to build, implement or code Doop designs, "make the app look like Doop", "build Home and Pricing from Doop", or bring a page in line with its Doop frame. Needs the doop-variants skill installed beside it and the app's `.doop/config.json`.
---

# Doop to code

The user names screens; each becomes app code that matches its Doop frame. Approval on Doop is optional: the user's request is the go-ahead. The canvas follows the doop-variants rules (read that skill's "Canvas rules"): per screen the desktop light master is the design, and its `@media (max-width:639px)` block is the phone layout; the dark and phone copies exist only to compare against.

Call Doop `get_guide` once before any Doop work, and use the config's `agent` as `agent_name` on every call.

## Setup

Doop is reachable only from omp's Python eval. Setup cell, with the absolute path of this skill's `scripts/` folder (it loads doop-variants' scripts from the sibling folder itself):

```python
import sys; sys.path.insert(0, '<skill dir>/scripts'); import screens, doop_sync
call = lambda name, args: getattr(tool, 'mcp__doop_' + name)(args)
APP = '~/GitHub/<repo>'; cfg = doop_sync.load(APP)
```

## Steps

1. **Find.** `found, unknown = await screens.find(cfg, call, read, ['Home', 'Pricing'])`. A name matches a screen and all its states. Anything in `unknown`: show the user the screen list and ask; never guess. A row with `recent` was edited in the last 10 minutes, so someone may still be working on it: ask before building it.
2. **Pull** each row's `source` frame: `await doop_sync.pull(cfg, call, read, fid, '/tmp/doop-code/<repo>/<fid>.html')`.
3. **Compare first**, before editing: run step 6 against the current app. The pictures show what has to change.
4. **Shared parts.** A header, footer, font or colour token that differs from the app changes every page. List those differences and ask before changing them; when agreed, build them in their own commit, ahead of the screens.
5. **Build** with the app's own components, tokens and rules (its AGENTS.md); never paste Doop's HTML. Take sizes, spacing and copy from the frame's CSS; its phone block maps to the app's breakpoint for 640px and up. A button's `data-doop-action="navigate:<id>"` names the frame it leads to: resolve the id to that frame's name to learn the route or modal it opens. Keep what the frame can't show: page metadata, structured data, analytics events.
6. **Check** with the app running locally: `python3 -I <skill dir>/scripts/compare.py http://localhost:<port><route> /tmp/doop-code/<repo>/<fid>.html` writes one side-by-side PNG per variant and prints both page heights. Read every PNG and iterate until the only differences left are the shared parts the user chose to keep. Pages behind sign-in: sign in an agent-browser session first and pass `--session <name>`. Then click each changed button once in the running app.
7. **Ship.** Run the repo's own checks (and its build when routes or config changed), then commit on a feature branch, one commit per screen. Never commit to `main` or merge; push and open a pull request when the user asks.
8. Delete `/tmp/doop-code`.

## Report

Per screen: route, commit, and the differences still showing in the comparison and why (usually a shared part the user deferred).
