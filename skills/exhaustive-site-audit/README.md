# Exhaustive Site Audit Skill

**Version 1.0.0**

**Requires the `agent-browser` CLI.** This skill is a thin wrapper over agent-browser's dogfood methodology — it will stop and report a missing dependency rather than silently falling back to another browser tool.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Main agent instructions. Hard constraints, audit workflow, bug confirmation standard, coverage gate, and output contract. | Yes |
| `README.md` | Documentation for humans. You're reading it. | No |

## Use It For

- Pre-launch QA sweeps of a web app or site
- Dogfooding a running app end to end
- Visual and responsive regression hunting across viewports
- Keyboard/accessibility spot audits (WCAG A/AA oriented)
- Chaos testing: rapid clicks, interrupted flows, refresh mid-state, unusual input
- Console/network error discovery from the user side

## Do Not Use It For

- Fixing bugs — this skill is report-only by design
- Source-code review or static analysis (it treats the app as a black box)
- Security exploitation or pentesting (input testing stops short of payloads meant to compromise systems)
- API-only testing without a browser surface
- Audits where destructive actions are acceptable (it refuses purchases, deletions, publishing, account changes, and irreversible submissions)

## Requirements

- The `agent-browser` CLI installed and its `dogfood` skill available (`agent-browser skills get dogfood`)
- A reachable target URL (defaults to `http://localhost:4321` when none is given)

## How It Works

1. **Surface discovery** — Crawls from the target URL using only browser-visible behavior and builds a coverage ledger of every reachable route, control, state, and interaction surface.
2. **Specialist passes** — Six independent perspectives: functional user, adversarial/chaos user, input/boundary user, visual/responsive user (mandatory screenshots at mobile + desktop for every route), accessibility/keyboard user, and navigation/state user. Console and network failures are observed throughout.
3. **Reproduction verification** — Every candidate bug is reproduced, classified as deterministic or intermittent, and recorded with URL, viewport, exact steps, screenshots/video, and expected vs. actual behavior.
4. **Coverage reconciliation** — The audit is complete only when every discovered surface is `TESTED` or `UNTESTED WITH REASON`: `D = T + U`. A high bug count never satisfies the stopping condition.
5. **Final report** — Findings by severity (CRITICAL/HIGH/MEDIUM/LOW), untested areas, coverage gaps, and a final assessment.

## Output

Creates a `dogfood-output/` directory:

```text
dogfood-output/
├── report.md       # Findings by severity with full evidence per bug
├── coverage.md     # Coverage ledger and final D/T/U reconciliation
├── screenshots/    # Visual evidence
└── videos/         # Motion/timing evidence where relevant
```

## Safety Guarantees

- **Black box only** — no source inspection, no config/dependency/test modification, no fixes.
- **Non-destructive** — production and external services are never exposed to purchases, deletions, publishing, outbound messages, or irreversible submissions; unsafe surfaces are reported as untested with the reason.
- **Evidence-backed** — no reproduction steps + screenshot/video evidence, no bug. Unconfirmed observations are kept separate from confirmed findings.
- **Fail-loud dependency** — missing `agent-browser` aborts the audit instead of degrading tooling.
