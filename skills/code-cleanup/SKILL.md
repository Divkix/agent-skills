---
name: code-cleanup
description: Repo-wide or broad multi-area codebase cleanup using 8 subagents to remove dead code, duplicates, circular dependencies, weak types, legacy paths, and stale comments. Triggers on cleanup, audit, code hygiene, technical debt sweeps, or /code-cleanup.
---

# Code Cleanup Skill

Run a disciplined repo-wide cleanup without speculative rewrites. Auto-applies only clearly safe work and forces revalidation after every write pass. Designed for multi-agent harnesses with subagent support.

## When to Use

- Whole-repo, monorepo-wide, or broad multi-package cleanup passes.
- Broad multi-area technical-debt, maintainability, or code-hygiene sweeps.
- Repo-wide cleanup audit or survey before deciding what to edit.
- Broad multi-area cleanup inside one large app, package, or service.
- Explicit `/code-cleanup` invocation.

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

## Non-Negotiable Contract

1. Always use exactly 8 subagents, one per cleanup area.
2. Default to a full-repo sweep except explicit exclusions or an explicit broad user-specified subset scope.
3. The initial pass is read-only across all 8 subagents.
4. Only one subagent may mutate repo-tracked files at a time. The active writer must claim the exact files or modules it will edit.
5. If earlier write passes changed a claimed file or any dependency a reasonable reviewer could see as affecting the finding, the current writer must re-research before editing.
6. Record baseline repo state before any writes: branch, HEAD commit, dirty files, staged hunks, validation commands, and validation failures.
7. Protect unrelated changes: never overwrite unrelated local edits. If intent is unclear in overlapping files, stop and ask. Stage only files changed by the cleanup pass being reported. Never treat `commit everything` as permission to stage unrelated work. Do not commit cleanup hunks from a mixed file unless the unrelated edits are clearly separable and intentionally preserved. Verify that the staged diff matches the reported cleanup files before creating a commit.
8. Auto-apply only `HIGH_CONFIDENCE` work during Phase 1.
9. Run validation after each write pass and again at phase end.
10. If a pass introduces a new validation failure, fix it within that pass or revert or defer that pass. Do not stack more cleanup on a broken tree.
11. `RECOMMENDED` and `AGGRESSIVE` work require approval after the queue is surfaced. Broad wording like `do the aggressive cleanup too` does not count until the queued items or phase are shown and approved.
12. Freeze the selected item queue and claimed files for each phase before the first write pass starts. Final review compares the diff against that frozen queue, not against post-hoc reporting.
13. Freeze the exact validation matrix before writes start. In a monorepo, list the package-level or project-level commands explicitly instead of relying on one convenient top-level command.
14. Snapshot, golden-file, or approval-fixture updates are never automatically `HIGH_CONFIDENCE`. Treat them as `RECOMMENDED` unless the user explicitly asked for that refresh.
15. Files with pre-existing staged hunks or unrelated unstaged local edits: exclude the file from cleanup or prove hunk-level isolation before any write.
16. All 8 research subagents must complete with usable findings or an explicit `no high-confidence changes` result before queue integration starts. If any subagent cannot be launched, times out, or returns unusable output, stop the phase. Do not integrate a partial research set.
17. Each write pass must be captured as a reversible unit before handoff so that rollback can target that pass without touching unrelated local work.
18. Once a phase queue is frozen, newly discovered items are deferred to the next queue. Do not append them mid-phase.
19. Do not weaken tests, mocks, helpers, fixtures, or assertions just to make validation green. Any test-side change that affects behavioral verification is at least `RECOMMENDED`.
20. Final review for Phase 1: the orchestrator verifies the frozen queue checklist mechanically. For Phase 2 and Phase 3: spawn a dedicated review subagent that receives the frozen queue, the diff, and validation results but did not participate in any write pass for that phase.

## Apply Tiers

| Tier | Auto-apply | Standard |
| --- | --- | --- |
| `HIGH_CONFIDENCE` | Yes | Local, mechanical, evidence-backed, no public behavior change, no unclear ownership, validation passes |
| `RECOMMENDED` | No | Medium-risk, intent-sensitive, or requires judgment about behavior or reachability |
| `AGGRESSIVE` | No | High-risk restructures, broad rewrites, speculative consolidation, or behavior-sensitive cleanup |

`HIGH_CONFIDENCE` requires all of the following:

1. Evidence is concrete and local to the affected files.
2. Public contracts and observable behavior stay the same.
3. Dynamic references, plugin lookup, reflection, and string-based access are ruled out or untouched.
4. Dirty overlapping files are not involved.
5. The diff is minimal for the problem being solved.
6. Required validation passes with no new failures.
7. No snapshot, golden-file, or approval-fixture refresh is needed.

If any requirement fails, downgrade the item.

## Safe Integration Order

Do not reorder these write passes:

`Shared Types → Unused Code → Circular Dependencies → DRY Deduplication → Weak Type Strengthening → Legacy Cleanup → Error Handling Audit → Noise / Obsolete Comment Cleanup`

## Phase Flow

### Phase 1: High-Confidence Cleanup

1. Spawn all 8 subagents for read-only research.
2. Wait for all 8 to return usable findings or explicit no-change results.
3. If any required result is missing or unusable, stop the phase.
4. If the findings do not all reference the same baseline snapshot identifier, stop and re-run affected research.
5. Integrate findings and select only `HIGH_CONFIDENCE` items.
6. Freeze the approved Phase 1 queue and claimed files before the first mutation.
7. Run write passes in the safe integration order, one active writer at a time, and capture each pass as a reversible unit before handoff.
8. After each write pass, run validation before handing off to the next writer.
9. Defer any newly discovered items to the next queue instead of appending them mid-phase.
10. Run full end-of-phase validation.
11. Run final review: the orchestrator mechanically verifies that every applied change maps to a finding, no excluded paths changed, the diff matches the frozen queue, no unrelated changes were absorbed, the validation matrix ran and outcomes are recorded, no snapshot refreshes were absorbed, and deferred items are listed.
12. Report what changed and queue the deferred `RECOMMENDED` and `AGGRESSIVE` items.

### Phase 2: Recommended Cleanup

Run only if the user explicitly asks for recommended items.

- Only proceed after Phase 1 final review reports the recommended queue.
- Require approval of the recommended queue or phase after it is surfaced.
- Freeze the approved recommended queue and claimed files before mutation.
- Re-freeze the full validation matrix for this phase. It may widen, but must not narrow silently.
- Use one active writer at a time with reversible units before handoff.
- Re-research the affected modules before writing.
- Apply only the approved `RECOMMENDED` items.
- Run validation after each write pass before handoff.
- Run full validation and final review using a dedicated review subagent that did not write in this phase.

### Phase 3: Aggressive Cleanup

Run only if the user explicitly asks for aggressive items.

- Only proceed after the aggressive queue is reported and approved.
- Freeze the approved aggressive queue and claimed files before mutation.
- Re-freeze the full validation matrix. It may widen, but must not narrow silently.
- Use one active writer at a time with reversible units before handoff.
- Re-research and restate the risk before editing.
- Apply only the approved `AGGRESSIVE` items.
- Run validation after each write pass before handoff.
- Run full validation and final review using a dedicated review subagent that did not write in this phase.

## Validation Requirements

Validation means all strongest repo-available checks found in preflight, plus cleanup-specific checks where they exist.

Preferred order: typecheck, lint, tests, build or compile checks, dead-code analysis relevant to the current pass, cycle detection relevant to the current pass.

Rules:

- Freeze the exact validation matrix during preflight and run that matrix, not a reduced subset, after each write pass and at phase end.
- Record the exact baseline result for each command before writing, including the full failing set or a lossless normalized form that preserves every failing file, test, rule, and message when the command is already red.
- If a command already fails at baseline, the same failure may remain only if the recorded failure set is unchanged. Any new, changed, or newly failing command is a regression.
- A regression blocks the phase until the active pass fixes, reverts, or defers its own changes.
- Do not update snapshots, golden files, approval fixtures, or edit ordinary tests, assertions, mocks, helpers, or fixtures as a Phase 1 escape hatch.
- If a validation command is flaky or nondeterministic, do not fish for green by rerunning until it passes. Rerun once to confirm instability. If the second result differs from the first, record the command as flaky and stop instead of continuing.
- Do not claim success without actual command output.

## Preflight

Before spawning subagents, inspect the repo and record:

- language and framework mix
- monorepo vs single package and package manager
- entry points and major module boundaries
- baseline snapshot identifier: current `HEAD` commit plus recorded staged and unstaged worktree state
- explicit user-specified scope slices, if any
- generated, vendor, or do-not-touch paths
- strongest available validation commands
- exact validation matrix for every relevant package, service, or language boundary
- baseline validation status for each command
- staged hunks and dirty files already present in the worktree
- runtime trust boundaries where `unknown` or weak typing is intentional

Default exclusions unless the user overrides them explicitly: generated outputs and caches (`node_modules`, `dist`, `build`, `.next`, `.turbo`, `coverage`), vendor and third-party directories, lockfiles and dependency manifests unless auditing unused dependencies.

Tooling rules: prefer repo-local or already-installed tools. Do not install new tools automatically unless the environment or user policy allows it. If a preferred tool is unavailable, report that gap and continue with non-speculative evidence gathering.

## Write Ownership and Snapshot Invalidation

- All research findings are tied to the repo snapshot seen during that research pass. All findings integrated into one queue must reference the same snapshot identifier. If the repo state changes before queue freeze, re-run affected research.
- If the user scoped cleanup to a broad subset such as multiple packages, keep the sweep inside that slice instead of silently widening to the whole repo.
- Before editing, the active writer must re-check every claimed file and directly affected module boundary against the current tree.
- If another pass changed a claimed file or any upstream/downstream dependency a reasonable reviewer could see as affecting the finding, re-research before editing.
- If two areas need the same file, serialize them and hand off only after validation.
- If a file contains unrelated local edits, cleanup is no longer automatically high-confidence.

Key definitions:

- **Proof of hunk-level isolation**: a baseline diff plus a current diff showing unrelated hunks unchanged and cleanup hunks separately selectable for staging or rollback. Eyeballing is not enough.
- **Usable findings**: concrete evidence, affected files, and an actionable ranked recommendation, or an explicit `no high-confidence changes` result with evidence. Boilerplate without evidence is unusable.
- **Reversible unit**: a persisted patch or temporary commit that can be applied or reverted mechanically. A mental undo plan is not enough.
- **Frozen queue item**: one cleanup recommendation with all of the following: cleanup area, exact files or modules, evidence, intended edit scope, confidence tier, and validation impact. `Clean up module X` is not a valid queue item.

## Shared Context for Every Subagent

```text
CODEBASE CONTEXT:
- Scope: {cleanup_scope}
- Language/Framework: {language_framework}
- Package manager/workspace: {pkg_manager_or_workspace}
- Entry points: {entry_points}
- Do NOT touch: {exclusion_list}
- Dirty files before cleanup: {dirty_files}
- Baseline snapshot: {snapshot_id}
- Validation commands: {validation_commands}
- Baseline validation failures: {baseline_failures}
- Current apply tier: {HIGH_CONFIDENCE | RECOMMENDED | AGGRESSIVE}
- Write mode: {RESEARCH_ONLY | ACTIVE_WRITE_TURN}
- Active write owner: {cleanup_area_name | none}

REQUIRED OUTPUT FORMAT:
1) Research findings with evidence and file paths
2) Critical assessment
3) Ranked recommendations with confidence
4) Applied changes for the current tier
5) Risks, deferred items, and validation impact
```

## Subagent Map

### 1. DRY / Deduplication

- Merge repeated logic only when the abstraction clearly reduces complexity.
- Keep duplicated code when merging would create condition-heavy or domain-leaking abstractions.

### 2. Shared Type Consolidation

- Merge duplicate or near-duplicate types only when they are semantically the same.
- Do not merge accidentally similar shapes from different domains.

### 3. Unused Code Removal

- Prefer explicit tools where available: `knip` (JS/TS), `deadcode`/`staticcheck` (Go), `vulture` (Python), or the closest safe equivalent for the language.
- Pair tool output with manual verification.
- Do not remove code with unresolved dynamic reachability.

### 4. Circular Dependency Cleanup

- Build the actual dependency chain before proposing a fix.
- Prefer extraction, dependency inversion, or smaller shared modules over broad rewrites.
- Use `madge` (JS/TS), `go list`/`goda` (Go), or the closest equivalent for the language.

### 5. Weak Type Strengthening

- Replace weak types only when the source type is proven by usage, package types, or runtime validation.
- Language-specific targets: `any`/`unknown`/`object`/`{}`/`as any`/`@ts-ignore` (TS/JS), `interface{}`/`any` (Go), `Any` (Python), `Object`/raw types (Java), `dynamic` (C#/Dart).
- Keep `unknown` (or equivalent) at trust boundaries unless a validator or guard proves the shape.

### 6. Error Handling Audit

- Language-specific patterns: `try/catch` (JS/TS/Java/C#), `try/except` (Python), `if err != nil` (Go), `Result`/`unwrap`/`expect`/`panic` (Rust), `rescue` (Ruby).
- Classify each case: `BOUNDARY_KEEP` (external I/O, network, user input), `RECOVERY_KEEP` (retry, fallback with clear intent), `HIDDEN_ERROR_REVIEW` (swallowed, logged-only, or empty handler), `VALUELESS_WRAPPER_REVIEW` (re-throws/re-returns identically), or `SAFE_REMOVE` (wraps deterministic internal logic with no failure path).
- Auto-apply only `SAFE_REMOVE` items in `HIGH_CONFIDENCE`.

### 7. Legacy / Deprecated / Fallback Cleanup

- Remove deprecated, obsolete, or permanently-off code only when reachability and compatibility are clear.
- Defer anything that still has uncertain downstream behavior.

### 8. Noise / Obsolete Comment Cleanup

- Remove stale migration notes, dead stubs, leftover debug prints, and AI slop.
- Preserve comments that explain non-obvious intent, constraints, or tradeoffs.

If a subagent finds nothing worth changing, it must still report `no high-confidence changes` with evidence.

## Failure Recovery

- Missing tool: report it, lower confidence, and avoid speculative cleanup that depended on it.
- Dirty overlapping file: stop or downgrade unless ownership is clear.
- Stale research (including indirect invalidation through upstream/downstream module changes): re-research before writing.
- Validation regression: fix within the current pass or revert or defer that pass.
- Rollback must target only the active pass by using its reversible unit. Do not guess at manual partial reverts on a dirty tree.
- Snapshot or golden-file update required to make validation green: downgrade to `RECOMMENDED` unless the user explicitly requested that refresh.
- Uncertain dynamic reference: downgrade to `RECOMMENDED` or leave untouched.
- True conflict with concurrent human edits: stop and ask.
- Pre-existing staged hunks in a claimed file: do not absorb them silently. Either preserve them outside the cleanup commit or stop. Exclude the file or prove hunk-level isolation before writing.
- If commit hooks or formatter hooks mutate tracked files after review, treat the post-hook tree as a new diff: re-run validation and final review before considering the commit complete.

## Final Report Template

Always end with:

1. Preflight assumptions used
2. Baseline repo state and validation results
3. Files changed and why
4. Validation results after each phase
5. Remaining `RECOMMENDED` items
6. Remaining `AGGRESSIVE` items
7. Residual risks and manual follow-ups

## Notes

- This skill assumes a git repository.
- Designed for frontier instruction-following models (Claude Opus/Sonnet 4.6, GPT-5.4, Kimi K2.5, GLM-5.1). On weaker models, Phase 1 auto-apply may benefit from manual approval checkpoints.
- Use `testing-scenarios.md` to run RED/GREEN/REFACTOR checks against this skill. That file validates the skill; it does not define runtime behavior.
