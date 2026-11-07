# Doop Variants Skill

Keeps a [Doop](https://doop.design) design canvas at four frames per screen (desktop light, desktop dark, phone light, phone dark) while you only ever edit one: the desktop light "master". A sync script builds the other three from it, wires the theme switch and the links of each version, and refuses to overwrite a copy someone edited by hand. A click-test script then walks through the prototype in a local browser, in all four versions.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Canvas rules and the edit → sync → verify loop for the agent. | Yes |
| `scripts/doop_sync.py` | Builds and updates the dark and phone copies; also `pull`/`push` a frame to a file. `python3 doop_sync.py` runs its self-check. | When syncing |
| `scripts/e2e.py` | Exports the canvas to local pages, serves them, clicks through every journey and crawls every frame. | When testing |
| `scripts/player.js` | Local stand-in for Doop's prototype player, injected into the exported pages. | When testing |
| `scripts/preview.py` | Renders one frame file in the four versions and checks it (no raw colours, no lost links). | When editing a frame |
| `README.md` | Documentation for humans. You're reading it. | No |

## Setup

1. **Install the skill.** Either `npx skills add divkix/agent-skills --skill doop-variants`, or symlink it to keep it updating with this repo:

   ```bash
   ln -s ~/GitHub/agent-skills/skills/doop-variants ~/.agents/skills/doop-variants
   ```

2. **Use [omp](https://github.com/can1357/oh-my-pi) with the Doop MCP server connected.** The scripts call Doop from omp's Python cell, so agents without a Python cell that can reach MCP tools can't run them.
3. **Install [`agent-browser`](https://github.com/vercel-labs/agent-browser)** for the click test and previews.

## Each app's settings

Each app repo holds two small files, so the skill itself stays app-free:

- `.doop/config.json`: the canvas id, the agent name to use on the canvas, the attribute that marks the theme switch, and optionally which pages to cover.
- `.doop/journeys.json`: the click-through paths to test ("upload → sign up", "dashboard tour", …), written against the masters' frame ids.

For a new app, ask the agent to set it up and give it the canvas link; it writes both files and commits them on a branch.

## How to use it

Open your agent inside the app's repo and ask in plain words:

```text
I changed the Home master on Doop, sync the copies
add a pricing screen to the Doop canvas, with all four versions
click-test the Doop prototype
set up doop variants for this repo, canvas https://doop.design/c/<id>
```

Or start it by name: `/skill:doop-variants` (omp).

Every change follows the same loop: edit the master (in a local file, previewed in all four versions), sync, check the sync now has nothing left to do, then click-test and screenshot.

## Notes

- Copies are rebuilt from the master, so edit the master, never a copy. A copy changed by hand shows up as "drift" and is left alone until you say otherwise.
- Any change to a frame clears its approval on Doop, so the sync only touches frames that actually change. A run with nothing to do writes nothing.
- Doop's hosted prototype player needs you signed in, so automated tests use the local copy. You can still click through the hosted one yourself.
