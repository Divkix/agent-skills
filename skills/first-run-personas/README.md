# First-Run Personas Skill

**Version 1.0.0**

**Requires the `agent-browser` CLI and Node 22+** (for the slow-3G script's built-in `WebSocket`).

Launch QA through five first-time users. Each persona runs as its own subagent in an isolated browser session, goes from landing page to first success, and screenshots every moment it gets confused, stuck, annoyed or blocked. The results merge into one issue list ranked by how many personas hit each problem.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Agent instructions: inputs, guardrails, persona contract and cards, merge and ranking rules. | Yes |
| `scripts/slow-3g.mjs` | Holds Chrome DevTools' Slow 3G profile on an agent-browser session (agent-browser has no throttle command). | Run by the mobile persona |
| `README.md` | Documentation for humans. | No |

## The personas

| Persona | Behaviour | Ends when |
|---|---|---|
| impatient | Skims, clicks the most prominent button | First error, dead end or wall of text |
| skeptic | Reads pricing, terms and privacy before signing up | First success or blocked |
| mobile | 375×812 viewport on slow 3G | First success or blocked |
| literal | Non-native English speaker; follows only what the UI literally says | First success or blocked |
| breaker | Junk in forms, Back mid-flow, double-clicks everything | First success or blocked |

## Use it vs. `exhaustive-site-audit`

- **first-run-personas**: one journey (landing page → first success), UX friction counted per persona. Pre-launch onboarding checks.
- **exhaustive-site-audit**: every reachable surface, reproducible bugs by severity. Full QA sweeps.

## Output

```text
first-run-output/
├── report.md          # Persona outcomes + issues ranked by personas hit
├── impatient/         # journal.md + numbered screenshots
├── skeptic/
├── mobile/
├── literal/
└── breaker/
```

## Limits

- Slow 3G is applied to the first tab only; if the mobile persona opens a new tab, that tab is unthrottled.
- Flows that need a real inbox, phone or card stop there as BLOCKED unless you supply test credentials.
- The personas are simulated by a model; they surface likely friction, not usability-study statistics.
