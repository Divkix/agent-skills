# Doop Design Skill

Designs screens on a [Doop](https://doop.design) canvas. Each screen is one design, the desktop light "master", which also holds its phone layout and takes every colour from the canvas colours. Ask for options and it makes several designs side by side for you to pick from.

It only makes and changes those designs. The dark and phone versions come from [doop-sync](../doop-sync/), which you run after you've reviewed the designs, and [doop-to-code](../doop-to-code/) builds them into the app.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Canvas rules and the design steps for the agent. doop-sync and doop-to-code read its rules too. | Yes |
| `scripts/doop_sync.py` | Reaches Doop through the MCP portal, `pull`/`push`es a frame to a file, and builds the dark and phone copies (doop-sync runs that part). `python3 doop_sync.py` runs its self-check. | Yes |
| `scripts/preview.py` | Renders one frame file in the four versions and checks it (no raw colours, no lost links). | When designing |
| `scripts/e2e.py` | Exports the canvas to local pages and clicks through every journey and frame. Used by doop-sync. | When click-testing |
| `scripts/player.js` | Local stand-in for Doop's prototype player, injected into the exported pages. Used by doop-sync. | When click-testing |
| `README.md` | Documentation for humans. You're reading it. | No |

## Setup

1. **Install the three Doop skills together** (doop-sync and doop-to-code use this skill's scripts):

   ```bash
   pnpx skills add -g Divkix/agent-skills --skill doop-design doop-sync doop-to-code
   ```

2. **Use [omp](https://github.com/can1357/oh-my-pi) with Doop behind your MCP portal** (code mode, `portal_codemode_execute`). The scripts call Doop from omp's Python cell, so agents without a Python cell that can reach MCP tools can't run them.
3. **Install [`agent-browser`](https://github.com/vercel-labs/agent-browser)** for the previews.

## Each app's settings

Each app repo holds two small files, so the skill itself stays app-free:

- `.doop/config.json`: the canvas id, the agent name to use on the canvas, the attribute that marks the theme switch, and optionally which pages to cover.
- `.doop/journeys.json`: the click-through paths doop-sync tests ("upload → sign up", "dashboard tour", …), written against the masters' frame ids.

For a new app, ask the agent to set it up and give it the canvas link; it writes both files and commits them on a branch.

## How to use it

Open your agent inside the app's repo and ask in plain words:

```text
design a pricing page on Doop
make 3 options for the Pricing page
I like option B, use it
make the pricing cards wider
set up doop-design for this repo, canvas https://doop.design/c/<id>
```

Or start it by name: `/skill:doop-design` (omp).

Each design is edited in a local file and previewed in all four versions before it goes back to Doop. Then you review it on Doop and run doop-sync.

## Notes

- Options are named `Option A · Pricing - /pricing` and so on. Until you pick one, doop-sync skips them and doop-to-code never builds them. Picking one for an existing page puts the winner into that page's design, so its links and versions carry over, and the other options are deleted.
- Never edit a dark or phone version by hand: the next sync leaves it alone and reports it as "drift". Change the master.
- Any change to a frame clears its approval on Doop.
