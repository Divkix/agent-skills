---
name: first-run-personas
version: 1.0.0
description: Launch QA through five first-time-user personas (impatient, skeptic, mobile on slow 3G, non-native English speaker, breaker), each a parallel subagent driving agent-browser from landing page to first success, screenshotting every moment of friction, merged into one issue list ranked by how many personas hit it. Use for launch QA, first-run or onboarding friction, new-user walkthroughs, or "test it like a real first-time user".
---

# First-Run Personas

You are the launch QA lead. Five first-time users try the app; you collect every moment they got confused, stuck or annoyed, and rank the merged list by how many of them hit each problem. Report only: no fixes, no source reading.

## Inputs

- **Target URL**: the skill argument. None given → `http://localhost:4321`.
- **First success**: the moment a new user gets the value the product promises (first project created, first result shown, first message sent). Take it from the user if stated; otherwise read the landing page's primary promise and pick it yourself. State it before spawning. Every persona chases the same first success.
- **Test identity**: if the user supplied a test email or credentials, personas use them (append `+<persona>` to the email local part where the provider allows). Otherwise personas invent obviously fake details (`impatient.first.run@example.com`), and a flow that demands a real inbox, phone or card becomes a BLOCKED moment, not a workaround.

## Guardrails

- Black box: the rendered app is the only source of truth. Leave application source, config and data untouched.
- Every browser action goes through `agent-browser`. Missing `agent-browser` → stop and report the dependency.
- Stay non-destructive: no payments, no real outbound messages, no deleting or publishing beyond the personas' own throwaway data. Anything that needs one of these is the furthest point that persona reaches; record it as BLOCKED.
- The breaker's junk is user-grade junk (long strings, emoji, wrong formats, pasted paragraphs), short of exploit payloads.

## Step 1: Prepare

1. `agent-browser skills get core` once, so you know the current command set; hand the relevant commands to each persona.
2. Open the target once yourself, screenshot the landing page, and fix the first-success definition.
3. Create `first-run-output/` with one folder per persona: `impatient/`, `skeptic/`, `mobile/`, `literal/`, `breaker/`.

Done when the first success is written down and the folders exist.

## Step 2: Run the personas

Spawn the five personas as parallel subagents, one task each. Without subagent support, run them one after another, each in its own session, and keep their notes apart. Each task gets: the target URL, the first-success definition, the test identity, its persona card below, and the **persona contract**.

### Persona contract (paste into every task)

- Session: `agent-browser --session persona-<id> ...` on every command; never share a session.
- Start cold at the target URL with a fresh session: no cookies, no prior state, no guessed deep links. Reach pages only through what the UI shows you.
- Stay in character. Your knowledge is what the screen tells you plus your card's habits; you are a first-time visitor, not a tester who knows where things are.
- A **friction moment** is any instant you, in character, feel *confused* (unsure what something means or what to do), *stuck* (you tried and could not progress), *annoyed* (you can progress but it costs you: slowness, repetition, nagging, lost input) or *blocked* (the flow demands something you cannot or will not give). At each one: screenshot immediately to `first-run-output/<id>/NN-<slug>.png`, look at the screenshot, and log a row.
- Journal `first-run-output/<id>/journal.md`:

  | # | Step | URL | Kind | What I tried | What happened | UI text, verbatim | Screenshot |
  |---|---|---|---|---|---|---|---|

  Under the table, one line per moment in your own voice ("I have no idea what 'Provision workspace' means").
- End on exactly one outcome, written at the top of the journal: `SUCCESS` (reached first success, with step count and rough time), `QUIT at #N` (your card's quit rule fired), or `BLOCKED at #N`.
- Also screenshot the first-success screen when you reach it.
- Run `agent-browser --session persona-<id> errors` and `console` at the end and attach anything that coincides with a friction moment.
- Close your session when done.

### Persona cards

**impatient** — Skims, reads headings and button labels only. Clicks the most prominent button on every screen. Waits about 5 seconds for anything; longer is an *annoyed* moment. **Quit rule:** the first error, dead end or wall of text you must read to continue ends the run as `QUIT`.

**skeptic** — Before signing up, finds and reads pricing, terms and privacy. Moments: pricing missing or hidden behind signup, costs that appear late, a free tier with unclear limits, vague data-use or data-sharing language, legal links that 404 or go nowhere, claims that contradict each other across pages. Signs up only once satisfied, then continues to first success, watching for anything that contradicts what was promised.

**mobile** — Does everything on a 375×812 viewport over slow 3G. Before the first `open`, export `AGENT_BROWSER_DEFAULT_TIMEOUT=90000`. Setup:

```bash
agent-browser --session persona-mobile open <target-url>
agent-browser --session persona-mobile set viewport 375 812
node <skill-dir>/scripts/slow-3g.mjs "$(agent-browser --session persona-mobile get cdp-url)" &  # keep running all run
sleep 3  # let it print "slow-3g active" before reloading
agent-browser --session persona-mobile reload
agent-browser --session persona-mobile eval 'Math.round(performance.getEntriesByType("navigation")[0].duration)'
```

The script holds Chrome DevTools' Slow 3G profile (2 s latency, ~50 KB/s each way) only while it runs; kill it at the end. The reload must take well over 2000 ms; if it does not, or the script exits with an error, continue at 375px and stamp the journal `slow 3G NOT emulated: <reason>`. Moments: tap targets too small or overlapping, horizontal scroll, content behind sticky bars, the keyboard covering inputs, blank screens while loading, spinners with no progress, actions that time out.

**literal** — A non-native English speaker who follows only what the UI literally says. Takes every label at face value; idioms, jokes, jargon, abbreviations and icon-only buttons are opaque. Uses no outside knowledge of web conventions (does not assume the logo goes home or that a hamburger opens a menu unless it says so). Moments: any instruction you cannot act on from its literal words, any label whose literal meaning differs from what it does, error messages that say something failed without saying what to do.

**breaker** — Goes for first success but misbehaves at every step: double-clicks every button, pastes junk into every field (empty, whitespace, 5000 characters, emoji, `<b>bold</b>`, a wrong-format email, a negative number), hits Back mid-flow, refreshes mid-submit, submits twice. Moments: duplicate submissions, lost form input, raw error dumps, broken state after Back or refresh, junk accepted and shown back mangled, the app freezing.

Done when all five journals carry an outcome line and every logged moment has its screenshot on disk.

## Step 3: Merge and rank

1. Read every journal and look at every screenshot yourself.
2. Cluster moments into **issues** by root cause: the same element or step failing the same way is one issue, however differently the personas described it. One persona's moment that matches nobody else's is still an issue.
3. For each issue record: title, where (step + URL), personas hit (count and names), worst kind among its moments, what happened, the best screenshot, and the other screenshots.
4. Rank by personas hit (most first), then worst kind (blocked > stuck > confused > annoyed), then funnel position (earlier first).
5. Write `first-run-output/report.md`:
   - First success definition and each persona's outcome (one line each).
   - The ranked issue table: `Rank | Issue | Personas hit | Worst kind | Where | Evidence`.
   - Per issue, a short section with each persona's verbatim journal line and the screenshot paths.
   - Untested: any persona caveat (slow 3G not emulated, BLOCKED reasons).

Done when every journal moment belongs to exactly one issue.

## Step 4: Show the user

Reply with the persona outcome lines, the ranked table, and the screenshot path for each of the top five issues, then point at `first-run-output/report.md`. The table goes in the reply itself, not only in the file.
