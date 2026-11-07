# Doop Sync Skill

Makes the dark, phone and phone-dark versions of every screen on a [Doop](https://doop.design) canvas from the one you designed (the desktop light "master"), wires the theme switch and the links of each version, and refuses to overwrite a copy someone edited by hand. Then it clicks through the prototype in a local browser, in all four versions, and tells you what broke.

It never changes your designs. A problem it finds goes into its report, and you fix the master with [doop-design](../doop-design/), then sync again.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | The sync → click-test steps for the agent. | Yes |
| `README.md` | Documentation for humans. You're reading it. | No |

The scripts it runs (`doop_sync.py`, `e2e.py`, `player.js`) live in doop-design's `scripts/` folder, so all three Doop skills share one copy.

## Setup

1. **Install the three Doop skills together**:

   ```bash
   pnpx skills add -g Divkix/agent-skills --skill doop-design doop-sync doop-to-code
   ```

2. **Use [omp](https://github.com/can1357/oh-my-pi) with Doop behind your MCP portal** (code mode, `portal_codemode_execute`), and install [`agent-browser`](https://github.com/vercel-labs/agent-browser) for the click test.
3. **The app repo needs `.doop/config.json` and `.doop/journeys.json`**; the doop-design setup writes them.

## How to use it

Open your agent inside the app's repo, after you've reviewed your designs on Doop:

```text
sync the Doop copies
click-test the Doop prototype
```

Or start it by name: `/skill:doop-sync` (omp).

## Where it fits

1. [doop-design](../doop-design/): design or change the desktop light screens, and review them on Doop.
2. This skill: make the other three versions and click-test them. Review all four on Doop.
3. [doop-to-code](../doop-to-code/): build the app from the canvas.

## Notes

- Copies are rebuilt from the master, so a copy changed by hand shows up as "drift" and is left alone until you say otherwise.
- Any change to a frame clears its approval on Doop, so the sync only touches frames that actually change. A run with nothing to do writes nothing.
- Design options you haven't picked yet (frames named `Option A · …`) are skipped.
- Doop's hosted prototype player needs you signed in, so the automated test uses a local copy. You can still click through the hosted one yourself.
- A sync of a 400-frame canvas takes about 3 minutes, because the portal cuts long answers and the scripts fetch the canvas frame by frame.
