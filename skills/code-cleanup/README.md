# Code Cleanup Skill

**Version 2.0.0**

Disciplined repo-wide or multi-area cleanup for technical-debt and maintainability work. Auto-applies only provably safe changes, defers anything that needs judgment, and re-validates after every write. Scales the work to what the repo actually contains instead of running a fixed heavyweight process.

Covers eight areas: unused code, legacy/fallback paths, circular dependencies, shared-type consolidation, weak types, duplication, error handling, and comment noise. Language-agnostic — works with TypeScript, Go, Python, Rust, Java, Ruby, C#, and others.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Agent instructions — what the model reads and follows. | Yes |
| `references/` | Detail loaded on demand: invocation contract, cleanup areas, hunk isolation, failure recovery, worked example, and (parallel-subagent path only) shared context + report shape. | On demand |
| `testing-scenarios.md` | Pressure tests for validating the skill itself. | No |
| `README.md` | This file. | No |

## Use It For

- Repo-wide or monorepo cleanup passes
- Broad multi-package or multi-area sweeps
- Technical-debt, code-hygiene, or maintainability passes before a release
- A cleanup audit before editing
- Broad multi-area cleanup inside one large app, package, or service
- `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, `/code-cleanup dry-run`

## Do Not Use It For

- Single bugfixes or feature work
- Pure formatting
- Search, explanation, or review-only requests
- Narrow single-file or single-helper fixes

## How It Works

1. **Preflight** — inspect the repo (languages, package manager, entry points, files in scope, exclusions, boundary files, dirty files) and record the validation matrix with baseline results. Scan which of the eight areas actually have signal. Repo-size guardrail: warn at 5K files, stop for scoping at 20K.
2. **Research (read-only), scaled to the repo:**
   - **Small or serial** (≈ < 50 source files, or no parallel-subagent support): research inline, covering each area with signal and handling entangled areas (cycles/dedup/types around the same modules) as one investigation.
   - **Larger, with parallel subagents:** one research agent per area-with-signal (kin areas merged), each fed the shared context, returning a structured report.
   - A full eight-way sweep is available on request or for large repos — it is not mandatory.
3. **Phase 0 (dry-run)** — report SAFE/REVIEW/RISKY queues; write nothing.
4. **Phase 1 (SAFE)** — auto-apply only provably-safe items, one write at a time in Safe Integration Order, validate after each, run a mechanical final review, one commit.
5. **Phase 2/3 (REVIEW/RISKY)** — tier-gated: surfaced, frozen, and applied only when the run is authorized through that tier. Independent review when real subagents are available. One commit each.

## Invocation Modes

- `/code-cleanup` — SAFE only, then report deferred queues
- `/code-cleanup review` — may continue into REVIEW after that queue is surfaced and frozen
- `/code-cleanup risky` — may continue through REVIEW and RISKY, each surfaced and frozen first
- `/code-cleanup dry-run` — report queues across all tiers, write nothing

The suffix sets the maximum tier. `review`/`risky` count as structured upfront authorization (no extra round-trip), but queues are still surfaced and frozen before any risky write. Vague phrasing — "do the risky cleanup too", "commit everything", "no questions" — is never authorization. These forms act as real slash commands only if your harness registers them; otherwise treat them as phrasing that sets the tier.

## Safety Floor

An eight-rule non-negotiable floor (full text in `SKILL.md`): research-before-write; SAFE-only auto-apply; protect unrelated work (never stage or overwrite edits you didn't make — a dirty file is not auto-SAFE); never fake green (no weakening tests or refreshing snapshots to pass); validate after every write pass and at phase end; re-check each file immediately before editing; one writer and one commit per phase with the committed diff equal to the frozen queue; boundary files excluded by default.

Additional guarantees:

- **Never overwrites unrelated local changes** — exact `git diff` proof commands for hunk isolation; excluding a dirty file is the default, not hunk-splitting.
- **Validation after every write pass**, not just at the end.
- **Phase 1 mechanical checklist review; Phase 2/3 independent review** when real subagents are available.
- **Scratch checkpoints per pass** for mechanical rollback; the phase still produces exactly one commit.
- **One commit per phase** (`chore: code cleanup phase <N> (<tier>)`), on a dedicated branch by default; never mid-phase.
- **Commit-hook protocol** — the post-hook diff must stay within the frozen queue; max 2 iterations; no `--no-verify`.
- **Cross-language boundary files** (generated/IDL/FFI) excluded by default; opt-in downgrades to REVIEW.
- **Polyglot validation** — a per-language matrix; a baseline failure in one language doesn't block cleanup in another.
- **Repo-size guardrail** — warn at 5K files, stop for scoping at 20K.

## Cleanup Areas (Safe Integration Order)

1. Unused code
2. Legacy / deprecated / fallback paths
3. Circular dependencies
4. Shared-type consolidation
5. Weak-type strengthening
6. DRY / deduplication
7. Error-handling audit
8. Stale / obsolete comments

Each step's output feeds the next; do not reorder. Areas 3–6 often form one entangled cluster around the same modules — research them together, but still apply edits in this order.

## Skill Testing

Use [`testing-scenarios.md`](./testing-scenarios.md) to pressure-test the skill: discovery triggers, dirty worktrees, go-green-by-weakening, scope creep, tiered invocation, dry-run isolation, adaptive execution, polyglot matrices, cross-language boundaries, per-phase commit discipline, commit-hook loops, and repo-size scoping. Run these after modifying `SKILL.md`.

## Model Compatibility

Works on frontier instruction-following models and open-weight models. The parallel-subagent report shape and shared-context block exist mainly to keep weaker/open-weight models on-rails when fanning out; on an inline run they do not apply and should not be performed as ceremony. On weaker models, restating the safety-floor rules before the first write is cheap drift insurance, and a second independent reviewer for RISKY work reduces false accepts. Spawned subagents carry real setup overhead, so the adaptive path fans out only where it pays off and runs inline otherwise.

## Harness Notes

This is a model-triggered skill. `SKILL.md` is harness-agnostic: with parallel subagents it fans out; without them it runs inline — the safety floor is identical either way. The `/code-cleanup …` forms act as slash commands only where the harness registers them.
