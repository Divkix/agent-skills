---
name: doop-to-code
description: Build screens from a Doop design canvas into an app's real code, then measure the running app against each Doop frame (differing pixels per screen-high slice, plus each text's size, font, colour and position, light/dark × desktop/phone) until they match; a build stamp in the app repo tracks which design each screen was built from. Use when asked to build, implement or code Doop designs, redesign the app from Doop, build what changed on Doop since the last build, "make the app look like Doop", "build Home and Pricing from Doop", or bring a page in line with its Doop frame. Needs the doop-design skill installed beside it and the app's `.doop/config.json`.
---

# Doop to code

The user names screens; each becomes app code that matches its Doop frame. Approval on Doop is optional: the user's request is the go-ahead. The canvas follows the doop-design rules (read that skill's "Canvas rules"): per screen the desktop light master is the design, and its `@media (max-width:639px)` block is the phone layout; the dark and phone copies, made by doop-sync, exist only to compare against.

Call Doop `get_guide` once before any Doop work, and use the config's `agent` as `agent_name` on every call.

## Setup

Doop sits behind the MCP portal and is reachable only from omp's Python eval. Setup cell, with the absolute path of this skill's `scripts/` folder (it loads doop-design's scripts from the sibling folder itself):

```python
import sys; sys.path.insert(0, '<skill dir>/scripts'); import screens, doop_sync
call = doop_sync.portal(tool)
APP = '~/GitHub/<repo>'; cfg = doop_sync.load(APP)
```

Make every Doop call through `call(name, args)`: the portal cuts its responses near 24,000 characters, and `call` returns them whole (doop-design's "Doop quirks").

Check the checker once per session: `python3 -I <skill dir>/scripts/compare.py --selftest` must print `compare selftest ok`.

**Run the app** when nothing answers on its port: start it as a named background service with `pnpm run local-dev` when the app's `package.json` has that script (local Postgres with sample data; the app's README names its port and a test sign-in). Otherwise use its dev script under `env -u CI`: with `CI` set, Alchemy ignores the saved Cloudflare login. Stop the service at the end if you started it. Apps can share a port, so when something already answers, check it's this repo: `lsof -a -d cwd -Fn -p "$(lsof -tiTCP:<port> -sTCP:LISTEN)"` must print this repo's path. If it's another app, ask the user before stopping it; never measure it.

## Steps

1. **Find.** `found, unknown = await screens.find(cfg, call, read, ['Home', 'Pricing'])`. A name matches a screen and all its states. Anything in `unknown`: show the user the screen list and ask; never guess. A row with `recent` was edited in the last 10 minutes, so someone may still be working on it: ask before building it.
   Asked for what changed on Doop (or for a whole redesign): `todo = await screens.changed(cfg, call, read)` compares the canvas with the app's build stamp `.doop/built.json`. Pass `todo['changed'] + todo['new']` to `find`; `tokens: True` means the canvas colours changed, so shared parts too; `gone` lists built screens no longer on the canvas: ask whether their routes go.
   The copies must be in step with their masters, since step 6 measures against them: `rep = await doop_sync.main([APP, '--only', ','.join(r['source'] for r in found)], call, read)` must show no `writes`, `drift` or `missing` for these screens. Anything listed: stop and ask the user to run doop-sync first.
2. **Pull** each row's `source` frame: `await doop_sync.pull(cfg, call, read, fid, '/tmp/doop-code/<repo>/<fid>.html')`.
3. **Compare first**, before editing: run step 6 against the current app. Its numbers show what has to change.
4. **Shared parts first.** The canvas is the finished design, so before any screen, build the header, footer, fonts and colour tokens it uses everywhere, the way step 5 builds a screen. Colours come from the canvas tokens, never from hex values in the frame's HTML: `await call('get_tokens', {'canvas_id': cfg['canvas_id'], 'agent_name': cfg['agent']})` lists each colour's light and dark value; match the app's own tokens to them by name (`--color-primary` is the app's primary). Shared parts change every page: give them their own commit, ahead of the screens, and check them on the first screen you compare. Leave one as it is only when the user says so.
5. **Build** with the app's own components, tokens and rules (its AGENTS.md); never paste Doop's HTML. Take sizes, spacing and copy from the frame's CSS, colours from the tokens; its phone block maps to the app's breakpoint for 640px and up. A button's `data-doop-action="navigate:<id>"` names the frame it leads to: resolve the id to that frame's name to learn the route or modal it opens. Keep what the frame can't show: page metadata, structured data, analytics events.
6. **Check** with the app running locally: `python3 -I <skill dir>/scripts/compare.py http://localhost:<port><route> /tmp/doop-code/<repo>/<fid>.html`. Per variant it prints the share of pixels that differ in each screen-high slice, then each text whose size, weight, line height, letter spacing, font, colour, box or wording differs, and the text only one side has. Work from the numbers, top down: fix the first slice that differs and the text rows inside it, run it again, then move down; a section that is too tall shifts everything under it. A `fonts failed` line means the numbers are wrong: fix the font first. Look at pictures last, for what numbers can't see (a wrong image, clipping, overlap): each differing slice has `<fid>.<variant>.slice-<y>.png` (Doop left, app right) and `.red.png` (where it differs). Done when every slice reads 0 and no text row is left, except differences with a named cause: data the frame invents (names, counts, photos), or a part the user asked to keep. Never wave a measured difference away as close enough; if you can't remove it or name its cause, ask the user. Pages behind sign-in: sign in an agent-browser session first and pass `--session <name>`. Then click each changed button once in the running app.
7. **Ship.** After a screen passes step 6, `screens.stamp(cfg, row, '/tmp/doop-code/<repo>/<fid>.html')`. Run the repo's own checks (and its build when routes or config changed), then commit on a feature branch: shared parts first, then one commit per screen, each with its `.doop/built.json` change. That commit is the screen's reference point: `git log -1 -S <sha> -- .doop/built.json` finds it, and on Doop `list_frame_versions` holds the design as it was at the stamp's `updatedAt`. Never commit to `main` or merge; push and open a pull request when the user asks.
8. Delete `/tmp/doop-code`.

## Report

Shared parts changed, then per screen: route, commit, and each slice or text row still differing in the comparison, with its cause. Asked for changes only: also what `changed` found and anything left unbuilt.
