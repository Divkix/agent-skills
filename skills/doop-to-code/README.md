# Doop to Code Skill

Turns screens you designed on a [Doop](https://doop.design) canvas into your app's real code. You name the screens; the agent rebuilds each one with the app's own components and colours (it never pastes Doop's HTML), then measures the running app against the Doop design in all four versions (desktop and phone, light and dark) and keeps fixing until the numbers match. The work lands on a feature branch, never on `main`.

It builds on [doop-design](../doop-design/): that skill designs the canvas and keeps it in shape, this one brings the canvas into the code.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | The find → build → compare → ship steps for the agent. | Yes |
| `scripts/screens.py` | Finds the Doop frames behind the screen names you give, flags any edited in the last 10 minutes, and keeps the build stamp (which Doop version each screen was built from). `python3 screens.py` runs its self-check. | When building |
| `scripts/compare.py` | Measures the running app against the Doop frame in the four versions: how many pixels differ in each screen-high slice, and each text whose size, font, colour, position or wording differs. Also saves side-by-side pictures. `python3 compare.py --selftest` checks the checker. | When checking |
| `README.md` | Documentation for humans. You're reading it. | No |

## Setup

1. **Install this skill and doop-design together** (the scripts reuse doop-design's code from the folder next to this one):

   ```bash
   pnpx skills add -g Divkix/agent-skills --skill doop-design doop-to-code
   ```

2. **Use [omp](https://github.com/can1357/oh-my-pi) with Doop behind your MCP portal** (code mode, `portal_codemode_execute`), and install [`agent-browser`](https://github.com/vercel-labs/agent-browser).
3. **The app repo needs `.doop/config.json`** (the doop-design setup writes it), and the app must run locally. An app with a `pnpm run local-dev` script gets started by the agent itself, with a local database and sample data.

## How to use it

Open your agent inside the app's repo and ask:

```text
redesign the app from Doop
build Home and Pricing from Doop
make the About page match its Doop design
build what changed on Doop since the last build
```

Or start it by name: `/skill:doop-to-code` (omp).

You don't need to mark screens "ready for dev" on Doop first; asking is enough.

## Where it fits

1. Design the whole app on Doop as desktop light screens (the "masters"), and review them.
2. Run [doop-design](../doop-design/) to make the dark and phone versions, and review all four on Doop. Anything that looks wrong gets fixed in the master, then synced again.
3. Run this skill to build the app from the canvas.

A later design change goes the same way: edit the master, sync, then ask for "what changed on Doop since the last build".

## Notes

- **Numbers, not eyeballing.** The agent doesn't judge the match by looking at two screenshots: it counts the differing pixels and reads each text's real size, font, colour and position from both pages, then fixes from the top down. It looks at the pictures only for what numbers can't see, like a wrong photo. A difference it can't fix or explain goes to you.
- **Shared parts come first.** The header, footer, fonts and colours show on every page, so the agent builds them before any screen, in their own commit. Tell it if you want one kept as it is.
- **Recently edited screens wait.** If a screen changed on Doop in the last 10 minutes, the agent asks before building, so it doesn't copy a half-finished design.
- **Every build leaves a reference point.** The app repo's `.doop/built.json` records which version of each Doop screen the code was built from, and it's committed with that screen's code. So the agent can tell exactly which screens changed on Doop since, and the commit shows when each one was last built. It only notes real design edits; moving a frame around on the canvas doesn't count.
- **Nothing is merged for you.** Each screen is its own commit on a feature branch; the agent pushes and opens a pull request only when you ask.
