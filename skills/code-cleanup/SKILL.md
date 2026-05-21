---
name: code-cleanup
version: 1.0.0
description: Repo-wide or broad multi-area codebase cleanup using 8 subagents to remove dead code, duplicates, circular dependencies, weak types, legacy paths, and stale comments. Triggers on cleanup, audit, code hygiene, technical debt sweeps, remove dead code, codebase hygiene, maintenance sweep, refactor (repo-wide or multi-area), `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, or `/code-cleanup dry-run`.
---

# Code Cleanup Skill

Run a disciplined repo-wide cleanup without speculative rewrites. Auto-applies only clearly safe work and forces revalidation after every write pass. Designed for multi-agent harnesses with subagent support (Claude Code, OpenCode, Factory Droid, Copilot CLI).

## When to Use

- Whole-repo, monorepo-wide, or broad multi-package cleanup passes.
- Broad multi-area technical-debt, maintainability, or code-hygiene sweeps.
- Repo-wide cleanup audit or survey before deciding what to edit.
- Broad multi-area cleanup inside one large app, package, or service.
- Explicit `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, or `/code-cleanup dry-run` invocation.

## When Not to Use

- A single bugfix, feature, migration, or performance task.
- Pure formatting requests.
- Search, explanation-only, or PR review requests.
- A narrow request such as removing one helper, one file, or one clearly local fix. Broad multi-area cleanup inside one large package or service is still in scope.

## Red Flags

Stop or downgrade confidence when any of these apply:

- Dirty files overlap cleanup targets and ownership is unclear.
- Baseline validation already fails and the failures are not recorded first.
- Dynamic or string-based references cannot be ruled out.
- The user asks to `commit everything` or silently include medium-risk or high-risk cleanup.
- Later write passes want to reuse stale findings after earlier passes changed the same files.
- Cleanup would touch a cross-language boundary file (generated code, FFI, IDL stubs).
- Repo size exceeds the scoping threshold in Preflight.

## Invocation Contract

For exact invocation rules and tier selectors, read `references/invocation-contract.md`.

## Non-Negotiable Contract

### Write Safety

1. **always** use exactly 8 subagents, one per cleanup area. If the harness cannot run 8 workers in parallel, serialize the research pass into 8 sequential read-only passes — **never** merge, combine, or skip cleanup areas.
   Rationale: Merging areas loses focused evidence and increases the chance of cross-area interference.

2. Default to a full-repo sweep except explicit exclusions or an explicit broad user-specified subset scope.
   Rationale: Keeps the cleanup comprehensive unless the user deliberately narrows it.

3. The initial pass is read-only across all 8 subagents.
   Rationale: Prevents write-before-research and ensures all decisions are evidence-based.

4. Only one subagent may mutate repo-tracked files at a time. The active writer **must** claim the exact files or modules it will edit.
   Rationale: Serial writes prevent conflicting mutations and make rollback tractable.

5. If earlier write passes changed a claimed file or any dependency a reasonable reviewer could see as affecting the finding, the current writer **must** re-research before editing.
   Rationale: Stale findings on a changed tree are likely wrong.

6. Record baseline repo state before any writes: branch, HEAD commit, dirty files, staged hunks, validation commands, validation failures, files-in-scope count, and a computed baseline snapshot ID (see Preflight).
   Rationale: Without a recorded baseline, regressions are impossible to distinguish from pre-existing issues.

7. Protect unrelated changes: **never** overwrite unrelated local edits. If intent is unclear in overlapping files, stop and ask. Stage only files changed by the cleanup pass being reported. **never** treat `commit everything` as permission to stage unrelated work. Do not commit cleanup hunks from a mixed file unless the unrelated edits are clearly separable and intentionally preserved. Verify that the staged diff matches the reported cleanup files before creating a commit.
   Rationale: Silently absorbing human work into an automated commit destroys local state.

### Validation

8. Auto-apply only `SAFE` work during Phase 1.
   Rationale: Higher tiers involve judgment calls that an auto-apply policy cannot safely make.

9. Run validation after each write pass and again at phase end.
   Rationale:Immediate detection prevents error propagation across passes.

10. If a pass introduces a new validation failure, fix it within that pass or revert or defer that pass. Do not stack more cleanup on a broken tree.
    Rationale: A broken tree invalidates all later findings.

11. `REVIEW` and `RISKY` work require an approved queue after it is surfaced. Approval may come from explicit upfront tier invocation or from a later post-queue confirmation. Broad wording like `do the risky cleanup too` does not count as upfront tier authorization.
    Rationale: Approval gates prevent unreviewed risky edits.

### Queue Management

12. Freeze the selected item queue and claimed files for each phase before the first write pass starts. Final review compares the diff against that frozen queue, not against post-hoc reporting.
    Rationale: A frozen queue is the contract; post-hoc reporting invites scope creep.

13. Freeze the exact validation matrix before writes start. In a monorepo, list the package-level or project-level commands explicitly instead of relying on one convenient top-level command.
    Rationale: Top-level commands may skip failing sub-projects.

14. Snapshot, golden-file, or approval-fixture updates are **never** automatically `SAFE`. Treat them as `REVIEW` unless the user explicitly asked for that refresh.
    Rationale: Snapshot updates change test expectations and can mask regressions.

15. Files with pre-existing staged hunks or unrelated unstaged local edits: exclude the file from cleanup or prove hunk-level isolation before any write (see Key Definitions for exact git commands).
    Rationale: Mixed hunks risk absorbing unrelated work.

16. All 8 research subagents **must** complete with usable findings or an explicit `NO_CHANGES` status before queue integration starts. If any subagent cannot be launched, times out, or returns output that fails schema validation, stop the phase. Do not integrate a partial research set. Subagents fail silently; trust the schema, not the subagent's self-report of success.
    Rationale: Partial research leads to incomplete and potentially inconsistent queues.

17. Each write pass **must** be captured as a reversible unit before handoff so that rollback can target that pass without touching unrelated local work.
    Rationale: Reversible units make per-pass rollback mechanical and safe.

18. Once a phase queue is frozen, newly discovered items are deferred to the next queue. Do not append them mid-phase.
    Rationale: Mid-phase additions bypass review and validation gates.

### Review Independence

19. Do not weaken tests, mocks, helpers, fixtures, or assertions just to make validation green. Any test-side change that affects behavioral verification is at least `REVIEW`.
    Rationale: Weakening tests to pass is a regression in verification quality.

20. Final review for Phase 1: the orchestrator verifies the frozen queue checklist mechanically. For Phase 2 and Phase 3: the orchestrator spawns a dedicated review subagent that receives the frozen queue, the diff, and validation results but did not participate in any write pass for that phase. The asymmetry is intentional: Phase 1 items are mechanically checklist-verifiable (diff matches queue, validation passes, no excluded paths touched, no unrelated changes absorbed), while Phase 2 and Phase 3 items are judgment calls about abstraction, reachability, and error semantics, and having a writer review their own judgment invites confirmation bias.
    Rationale: Independence prevents confirmation bias on judgment-call review work.

21. Commit granularity is one commit per phase. Each phase produces exactly one commit covering all write passes integrated in that phase. Commit subject: `chore: code cleanup phase <N> (<tier>)`. Commit body lists the frozen queue items and validation outcomes. **never** commit mid-phase.
    Rationale: Mid-phase commits break the all-or-nothing contract of a phase.

### Cross-Boundary Safety

22. Cross-language boundary files (OpenAPI-generated types, gRPC/Protobuf stubs, FFI bindings, IDL-generated code) are default-excluded unless the user explicitly opts in. If a proposed cleanup touches one of these files, downgrade to `REVIEW` regardless of other evidence.
    Rationale: Generated/boundary files have external contracts that cleanup must not violate silently.

### Subagent Integrity

23. Every subagent output **must** conform to the Subagent Output Schema. Non-conforming output is unusable under Rule 16 and blocks queue integration. The orchestrator validates the schema before integrating findings.
    Rationale: Schema enforcement is the only reliable signal that a subagent actually succeeded.

24. The orchestrator owns all subagent context injection. Subagent context windows start fresh with nothing inherited from the parent; the full Shared Context block **must** be passed in the spawning prompt string for every subagent, on every invocation.
    Rationale: Inherited context drifts across long runs and leaks state between areas.

## Self-Check Before Phase 1

Before spawning the 8 research subagents, the orchestrator must answer each of the following in one line, in its own words, as an anti-drift check:

1. What does the agent do if a claimed file already has unrelated unstaged edits?
2. What does the agent do if validation was already failing at baseline?
3. What does the agent do if it finds a new cleanup item after the phase queue is frozen?
4. What counts as a reversible unit?
5. What is the exact `requested_max_tier`, `approval_source`, and `mode` for this run?

If any answer contradicts the Non-Negotiable Contract, stop and re-read the contract before continuing. This step exists because weaker instruction-following models silently drop rules across long runs; catching drift here is cheaper than catching it after a bad write pass.

## Apply Tiers

| Tier | Auto-apply | Standard |
| --- | --- | --- |
| `SAFE` | Yes | Local, mechanical, evidence-backed, no public behavior change, no unclear ownership, validation passes |
| `REVIEW` | No | Medium-risk, intent-sensitive, or requires judgment about behavior or reachability |
| `RISKY` | No | High-risk restructures, broad rewrites, speculative consolidation, or behavior-sensitive cleanup |

Phase entry rule:

- Run only tiers up to `requested_max_tier`.
- `SAFE` **always** runs first when any cleanup tier is approved.
- If `approval_source=EXPLICIT_UPFRONT_TIER`, the agent may continue into later approved tiers after surfacing and freezing that queue.
- If `approval_source=DEFAULT_SAFE_ONLY`, stop after Phase 1 and report the deferred queues unless the user later approves more.
- If `approval_source=POST_QUEUE_APPROVAL`, continue only through the tier the user approved after queue surfacing.

`SAFE` requires all of the following:

1. Evidence is concrete and local to the affected files.
2. Public contracts and observable behavior stay the same.
3. Dynamic references, plugin lookup, reflection, and string-based access are ruled out or untouched.
4. Dirty overlapping files are not involved.
5. The diff is minimal for the problem being solved.
6. Required validation passes with no new failures.
7. No snapshot, golden-file, or approval-fixture refresh is needed.
8. No cross-language boundary file is touched.

If any requirement fails, downgrade the item.

## Safe Integration Order

Do not reorder these write passes. Each step's output is the next step's input:

1. **Unused Code** — shrink the search space before anything else operates on it.
2. **Legacy / Deprecated / Fallback Cleanup** — more removals on the same logic; strike while dead-code tooling signal is fresh.
3. **Circular Dependency Cleanup** — detect cycles on the real graph, not one polluted with unused exports that were masking cycles.
4. **Shared Type Consolidation** — consolidate only types attached to code that survived removal.
5. **Weak Type Strengthening** — strengthen against a clean, consolidated type graph.
6. **DRY / Deduplication** — merge logic once types are strong enough to distinguish true duplicates from accidentally similar shapes.
7. **Error Handling Audit** — classify control flow after the code it governs has settled.
8. **Noise / Obsolete Comment Cleanup** — every prior step leaves stale comments, so go last.

## Subagent Output Schema

For the full subagent output schema and validation rules, read `references/subagent-schema.md`.

## Shared Context

For the full Shared Context template injected into every subagent, read `references/shared-context.md`.

## Subagent Map

For the full description of all 8 cleanup areas, read `references/cleanup-areas.md`.

## Phase Flow

### Phase 0: Dry-Run (mode=DRY_RUN only)

Triggered by `/code-cleanup dry-run`. Run preflight, self-check, spawn all 8 subagents for read-only research, integrate findings across tiers, and report queues. Do not write, commit, or create reversible units. For a full walkthrough, see `references/worked-example.md`.

### Phase 1: Safe Cleanup

Run self-check, spawn 8 parallel research subagents, validate schema, freeze only `SAFE` items, then execute write passes one at a time in Safe Integration Order. Capture each pass as a reversible unit, validate after every pass, run end-of-phase validation and mechanical final review, then produce exactly one commit. If commit hooks mutate files, apply Commit Hook Handling. For full details, see `references/worked-example.md`.

### Phase 2: Review Cleanup

Run only if `requested_max_tier` allows `REVIEW` and the queue is approved. Re-research affected modules, freeze queue and validation matrix (may widen, **must** not narrow silently), write one at a time, validate after each, spawn independent review subagent, then commit. See `references/worked-example.md`.

### Phase 3: Risky Cleanup

Run only if `requested_max_tier` allows `RISKY` and the queue is approved. Re-research and restate risk, freeze queue and validation matrix, write one at a time, validate after each, spawn independent review subagent, then commit. See `references/worked-example.md`.

## Validation Requirements

Freeze the exact validation matrix during preflight and run the full matrix after each write pass and at phase end. Record baseline results losslessly; any new or changed failure is a regression that blocks the phase. Do not update snapshots or weaken tests as an escape hatch. If a command is flaky, rerun once to confirm, then record it and stop. Each pass validates only against its own language boundary. For full rules and polyglot guidance, read `references/failure-recovery.md`.

## Preflight

Record: language/framework mix, package manager, entry points, baseline snapshot ID, files in scope, exclusions, boundary files, validation matrix with baseline results, dirty files, and staged hunks. Repo-size guardrail: < 5K files proceed; 5K–20K warn; > 20K stop and ask for scoping. Default exclusions: generated outputs, caches, third-party dirs, lockfiles (unless auditing deps), and cross-language boundary files. Prefer repo-local tools; report gaps instead of auto-installing.

## Write Ownership and Snapshot Invalidation

All findings are tied to one snapshot ID; mismatches require re-research. The active writer must re-check claimed files before editing, and re-research if any upstream/downstream dependency changed. If two areas need the same file, serialize them. A file with unrelated local edits is no longer automatically `SAFE`. For the complete hunk-level isolation proof and key definitions, read `references/hunk-isolation.md`.

## Failure Recovery

For failure recovery protocols and commit hook handling, read `references/failure-recovery.md`.

## Worked Example

For a compact end-to-end worked example, read `references/worked-example.md`.

## Final Report Template

**always** end with:

1. Preflight assumptions used
2. Baseline repo state, baseline snapshot ID, files-in-scope count, and validation results
3. Files changed and why, grouped by phase
4. Validation results after each write pass and each phase
5. Commit SHAs created (one per phase)
6. Remaining `REVIEW` items
7. Remaining `RISKY` items
8. Residual risks and manual follow-ups
9. Invocation mode used: `requested_max_tier`, `approval_source`, and `mode`
10. Which phases executed versus deferred
11. Self-check answers given before Phase 1
12. Any schema validation failures encountered during research

## Notes

- This skill assumes a git repository.
- Registered as a slash command across Claude Code, OpenCode, Factory Droid, and Copilot CLI. SKILL.md content is identical across harnesses; only the invocation wiring differs.
- Tested on frontier instruction-following models (Claude Opus/Sonnet 4.6+, GPT-5.4+) and open-weight models (Kimi K2.5, GLM-5.1). The Self-Check step and the strict Subagent Output Schema are primarily scaffolding for open-weight models, which tend to silently drop rules across long runs. On weaker models, running two independent review subagents for Phase 2/3 final review (instead of one) further reduces false-accept rates.
- Each subagent invocation carries ~20k tokens of overhead before any findings. Budget accordingly on paid inference.
- Use `testing-scenarios.md` to run RED/GREEN/REFACTOR checks against this skill. That file validates the skill; it does not define runtime behavior.
