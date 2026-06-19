---
name: code-cleanup
version: 2.0.0
description: Use when cleaning up a whole repo, monorepo, or several packages/areas at once — technical-debt sweeps, code-hygiene or maintainability passes, pre-release cleanup, or a cleanup audit before editing. Covers dead/unused code, legacy and fallback paths, circular dependencies, duplicated logic, weak types, error-handling noise, and stale comments. Not for a single bugfix, feature, one-file change, migration, or pure formatting. Also triggers on `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, `/code-cleanup dry-run`.
---

# Code Cleanup

Disciplined repo-wide or multi-area cleanup. Auto-applies only provably safe changes, defers anything that needs judgment, and re-validates after every write. Scales the work to what the repo actually contains instead of running a fixed heavyweight process.

## When to Use

- Whole-repo, monorepo, or multi-package cleanup sweeps.
- Technical-debt, maintainability, or code-hygiene passes (e.g., before a release).
- A cleanup audit or survey before deciding what to edit.
- Broad multi-area cleanup inside one large app, package, or service.
- `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, or `/code-cleanup dry-run`.

## When Not to Use

- A single bugfix, feature, migration, or performance task.
- Pure formatting.
- Search-, explanation-, or review-only requests.
- A narrow change to one helper or one file. (Multi-area cleanup of one large package is still in scope.)

## How It Works

Preflight (record baseline, scope the work) → read-only research → tiered phases. Each phase freezes a queue, writes one change at a time in Safe Integration Order, validates after every write, then makes exactly one commit. Three tiers:

- **SAFE** — auto-applied in Phase 1.
- **REVIEW** — surfaced, then applied only after the queue is approved.
- **RISKY** — same gate, for high-risk restructures.

`/code-cleanup` runs SAFE only and reports the rest. The `review`/`risky` suffixes raise the ceiling; `dry-run` reports queues and writes nothing. Exact tier-selector semantics: `references/invocation-contract.md`.

## The Safety Floor (non-negotiable)

These are the load-bearing rules. **Violating the letter is violating the spirit.**

1. **Research is read-only.** No writes until the phase's research is done and its queue is frozen.
2. **Only SAFE auto-applies.** REVIEW and RISKY need a surfaced, frozen, *approved* queue. Vague wording — "do the risky stuff too", "commit everything", "no questions", "I trust you" — is never approval and never authorization to widen scope.
3. **Protect unrelated work.** Never stage or overwrite edits you did not make. A file carrying unrelated local edits (staged or unstaged) is **not** auto-SAFE: exclude it, or prove hunk-level isolation first (`references/hunk-isolation.md`). This overrides every other SAFE signal — e.g., an unused export living in a dirty file is not SAFE.
4. **Never fake green.** Do not weaken or delete tests, assertions, mocks, fixtures, or refresh snapshots/golden files to make validation pass. Any behavior-affecting test change is at least REVIEW.
5. **Validate after every write pass and at phase end.** Record baseline results first; only non-regression against that recorded set is allowed. A new or changed failure stops the phase — fix it within that pass, or revert/defer the pass. Never stack cleanup on a red tree.
6. **Re-check before you write.** Immediately before editing, re-diff each claimed file (`git diff HEAD -- <file>`); if it or a dependency changed since research, re-research. Findings are valid only for the tree they were made on.
7. **One writer, one commit per phase.** Freeze the queue and the validation matrix before writing. Write serially. Do cleanup on a dedicated branch (e.g., `chore/cleanup`), not directly on the default branch, unless told otherwise. The phase's committed diff must equal the frozen queue — nothing more. Commit subject: `chore: code cleanup phase <N> (<tier>)`; body lists the frozen queue and validation outcomes. Never create the phase commit until all its passes are written and validated; per-pass rollback uses scratch checkpoints, not extra commits (see Rollback).
8. **Boundary files are excluded by default.** Generated/IDL/FFI code (OpenAPI, gRPC/Protobuf, FFI bindings) carries external contracts. Exclude unless the user opts in, and even then downgrade any edit to REVIEW.

## Apply Tiers

| Tier | Auto-apply | Standard |
| --- | --- | --- |
| `SAFE` | Yes | Local, mechanical, evidence-backed, no public-behavior change, clear ownership, validation passes |
| `REVIEW` | No | Medium-risk, intent-sensitive, or needs judgment about behavior or reachability |
| `RISKY` | No | High-risk restructures, broad rewrites, speculative consolidation, behavior-sensitive cleanup |

`SAFE` requires **all** of:

1. Evidence is concrete and local to the affected files.
2. Public contracts and observable behavior are unchanged.
3. Dynamic, reflective, or string-based references are ruled out.
4. No unrelated local edits in the touched files (see safety floor 3).
5. The diff is minimal for the problem.
6. Validation passes with no new failures.
7. No snapshot/golden/fixture refresh and no behavior-affecting test change.
8. No boundary file touched.

If any item fails, downgrade.

**Dead-code boundary:** removing a symbol with no readers anywhere is `SAFE`; removing a still-referenced but provably-unreachable branch or path (e.g., behind a disabled feature flag) is `REVIEW` — the gate may be intended to be re-enabled, so the call is about intent, not just reachability.

**Tier gating:** run only tiers up to the approved maximum; SAFE always runs first. With explicit upfront tier (`review`/`risky`), continue into higher approved tiers after surfacing and freezing each queue — no extra round-trip. With default SAFE-only, stop after Phase 1 and report the deferred queues. A later explicit narrowing instruction wins for phases not yet started.

## Execution Model (scale to the repo)

Do not run a fixed heavyweight process. During preflight, scan which of the eight cleanup areas actually have signal (repo-local tooling or `rg`), then:

- **Small or serial** — roughly < 50 source files in scope, or a harness without parallel subagents: do the read-only research **inline**, covering each area that has signal. Research entangled areas together (circular deps, duplication, and type consolidation around the same modules are one investigation, not three). An inline run never needs `references/shared-context.md` or `references/subagent-schema.md` — skip them.
- **Larger, with parallel subagents:** spawn one read-only research agent per area-with-signal (merging kin areas), inject the Shared Context (`references/shared-context.md`) into each, and collect their reports (`references/subagent-schema.md`).
- **Full eight-way sweep** is available on request or for large repos; it is **not** mandatory. Cover every area with signal; an area with no signal needs no agent.

**Review independence:** when real subagents are used, a reviewer that did not write checks the REVIEW/RISKY phases. When research and writing are inline, there is no separate worker to cross-check — the orchestrator re-reviews the frozen queue against the diff with explicit skepticism, and a genuine second reviewer is recommended for RISKY work (especially on weaker models).

## Cleanup Areas & Safe Integration Order

Apply write passes in this order; each step's output feeds the next, so do not reorder. Full per-area guidance: `references/cleanup-areas.md`.

1. **Unused code** — shrink the search space first.
2. **Legacy / deprecated / fallback paths** — remove dead paths with clear reachability.
3. **Circular dependencies** — detect cycles on the real (post-removal) graph.
4. **Shared-type consolidation** — merge only semantically identical types.
5. **Weak-type strengthening** — strengthen against the consolidated type graph.
6. **DRY / deduplication** — merge true duplicates, not accidentally similar shapes.
7. **Error-handling audit** — classify control flow after the code settles.
8. **Stale / obsolete comments** — last, since every prior step leaves some.

Areas 3–6 frequently touch the same modules; when they do, research them as one cluster but still apply edits in this order.

## Phases

- **Phase 0 — Dry-run** (`dry-run`): preflight + research, report SAFE/REVIEW/RISKY queues with evidence and validation impact, write nothing (no commits, no checkpoints, no working-tree changes). A later write run re-runs research from scratch.
- **Phase 1 — SAFE:** freeze the SAFE queue, write in order, validate per pass, run a mechanical final review (diff == frozen queue, validation green, no excluded paths touched, no unrelated hunks, no faked green), one commit.
- **Phase 2 — REVIEW / Phase 3 — RISKY** (only if the tier is approved): re-research affected modules, freeze queue + matrix (may widen, never silently narrow), write serially, validate per pass, run independent review (see Execution Model), one commit.

For a compact end-to-end example, see `references/worked-example.md`.

## Preflight

Record: language/framework mix, package manager, entry points, files in scope, exclusions, boundary files, dirty files, staged hunks, and the validation matrix **with baseline results**. Scan which cleanup areas have signal. Repo-size guardrail: < 5K files proceed; 5K–20K warn; > 20K stop and ask for scoping (the token cost of a full sweep stops being worth it). Default exclusions: generated output, caches, vendored/third-party dirs, lockfiles (unless auditing deps), and boundary files. Prefer repo-local tools; report missing tools instead of auto-installing.

## Validation

Freeze the exact matrix in preflight. In a monorepo, list per-package/per-project commands explicitly — do not lean on one top-level command that may skip failing sub-projects. Run the full matrix after each write pass and at phase end. Record baseline failures losslessly; a baseline failure in one language does not block cleanup in another, but any new or changed failure is a regression that stops the phase. Each pass validates against its own language boundary. A flaky command: rerun once to confirm, then record the flakiness and stop — never rerun until it happens to go green. Full rules: `references/failure-recovery.md`.

## Rollback

Capture a checkpoint after each write pass so a failed pass can be undone mechanically — the reversible unit is a saved patch (`git diff > /tmp/pass-N.patch`). These checkpoints are scratch; they are not the phase commit (floor 7) and do not count as committing mid-phase. Because passes build on each other in Safe Integration Order, undoing a pass means restoring the checkpoint from *before* it (which also unwinds later passes that depended on it); redo from there. Unrelated local work stays safe because it was never staged or committed. Never hand-revert guesses on a dirty tree.

## Re-research & Ownership

Every finding in a queue comes from one research pass on one tree state. If the tree changed before the queue froze, re-research the affected areas. The active writer re-checks each claimed file immediately before editing and re-researches if it or an upstream/downstream dependency a reasonable reviewer would tie to the finding has changed. If two areas need the same file, serialize them and hand off only after validation. Details and the hunk-isolation proof: `references/hunk-isolation.md`.

## Commit Hooks

If a pre-commit hook mutates files, treat the post-hook tree as a new diff: every file in `git diff HEAD~1 HEAD` must be in the frozen queue, or reset the commit (`git reset --hard HEAD~1`) and stop. Maximum 2 commit→hook iterations. Never use `git commit --no-verify`. Details: `references/failure-recovery.md`.

## Final Report

End with:

1. Preflight assumptions used.
2. Baseline repo state, files-in-scope count, and validation results.
3. Files changed and why, grouped by phase.
4. Validation results after each write pass and each phase.
5. Commit SHAs created (one per phase).
6. Remaining `REVIEW` queue.
7. Remaining `RISKY` queue.
8. Residual risks and manual follow-ups.
9. Invocation mode: `requested_max_tier`, `approval_source`, `mode`, and which phases ran versus deferred.

## Notes

- Assumes a git repository.
- This is a **model-triggered skill**. The `/code-cleanup …` forms are conventions; they act as real slash commands only if your harness registers them, otherwise treat them as plain phrasing that sets the tier and mode.
- SKILL.md is harness-agnostic. With parallel subagents it fans out; without them it runs inline — the safety floor is identical either way.
- The Shared Context block, the subagent report shape, and the independent reviewer matter **only** when real subagents are used. They are scaffolding (most useful for weaker/open-weight models that drop rules on long runs), not ceremony to perform when running inline. On weaker models, restating the safety-floor rules in your own words before the first write is cheap drift insurance.
- Use `testing-scenarios.md` to pressure-test changes to this skill. It validates the skill; it does not define runtime behavior.
