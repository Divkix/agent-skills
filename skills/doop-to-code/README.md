# Doop to Code Skill

Turns screens you designed on a [Doop](https://doop.design) canvas into your app's real code. You name the screens; the agent rebuilds each one with the app's own components and colours (it never pastes Doop's HTML), then screenshots the running app next to the Doop design in all four versions (desktop and phone, light and dark) and keeps fixing until they match. The work lands on a feature branch, never on `main`.

It builds on [doop-variants](../doop-variants/): that skill keeps the canvas in shape, this one brings the canvas into the code.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | The find → build → compare → ship steps for the agent. | Yes |
| `scripts/screens.py` | Finds the Doop frames behind the screen names you give, and flags any edited in the last 10 minutes. `python3 screens.py` runs its self-check. | When building |
| `scripts/compare.py` | Screenshots the running app beside the Doop frame in the four versions and puts them side by side. | When checking |
| `README.md` | Documentation for humans. You're reading it. | No |

## Setup

1. **Install this skill and doop-variants side by side** (the scripts reuse doop-variants' code from the folder next to this one):

   ```bash
   ln -s ~/GitHub/agent-skills/skills/doop-variants ~/.agents/skills/doop-variants
   ln -s ~/GitHub/agent-skills/skills/doop-to-code ~/.agents/skills/doop-to-code
   ```

2. **Use [omp](https://github.com/can1357/oh-my-pi) with the Doop MCP server connected**, and install [`agent-browser`](https://github.com/vercel-labs/agent-browser).
3. **The app repo needs `.doop/config.json`** (the doop-variants setup writes it), and the app must run locally.

## How to use it

Open your agent inside the app's repo, start the app, and ask:

```text
build Home and Pricing from Doop
make the About page match its Doop design
```

Or start it by name: `/skill:doop-to-code` (omp).

You don't need to mark screens "ready for dev" on Doop first; asking is enough.

## Notes

- **Shared parts come first, and only with your OK.** If the design's header, footer, fonts or colours differ from the app, changing them changes every page, so the agent lists them and asks before touching them.
- **Recently edited screens wait.** If a screen changed on Doop in the last 10 minutes, the agent asks before building, so it doesn't copy a half-finished design.
- **Nothing is merged for you.** Each screen is its own commit on a feature branch; the agent pushes and opens a pull request only when you ask.
