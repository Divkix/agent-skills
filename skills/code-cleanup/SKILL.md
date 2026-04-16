---
name: code-cleanup
description: Use when the user wants a whole-repo, monorepo-wide, broad multi-package, or broad single-app, single-package, or single-service cleanup, audit, or survey pass, a multi-area code-hygiene or technical-debt sweep across the codebase, or invokes /code-cleanup.
---

# Code Cleanup Skill

## Overview

Run a disciplined repo-wide cleanup without speculative rewrites. This skill keeps cleanup evidence-based, auto-applies only clearly safe work, and forces revalidation after every write pass.

## When to Use

- The user asks for a whole-repo or monorepo-wide cleanup pass.
- The user asks for a broad multi-package cleanup sweep inside a monorepo.
- The user wants a broad multi-area technical-debt, maintainability, or code-hygiene sweep.
- The user wants a repo-wide cleanup audit or survey before deciding what to edit.
- The user wants a broad multi-area cleanup sweep inside one large app, package, or service.
- The user explicitly invokes `/code-cleanup`.

## When Not to Use

- A single bugfix, feature, migration, or performance task.
- Pure formatting requests.
- Search, explanation-only, or PR review requests.
- A narrow request such as removing one helper, one file, one warning, or one clearly local fix inside a package or service. Broad multi-area cleanup inside one large package or service is still in scope.

## Red Flags

- Dirty files overlap cleanup targets and ownership is unclear.
- Baseline validation already fails and the failures are not recorded first.
- Dynamic or string-based references cannot be ruled out.
- The user asks to `commit everything` or silently include medium-risk or high-risk cleanup.
- Later write passes want to reuse stale findings after earlier passes changed the same files.

When any red flag applies, downgrade confidence or stop.

## Non-Negotiable Contract

1. Always use exactly 8 subagents, one per cleanup area.
2. Default to a full-repo sweep except explicit exclusions or an explicit broad user-specified subset scope.
3. The initial pass is read-only across all 8 subagents.
4. Only one subagent may mutate repo-tracked files at a time.
5. The active writer must claim the exact files or modules it will edit.
6. If earlier write passes changed a claimed file, the current writer must re-research before editing.
7. Record baseline repo state before any writes: branch, dirty files, staged hunks, validation commands, and validation failures.
8. Never overwrite unrelated local changes. If intent is unclear in overlapping files, stop and ask.
9. Auto-apply only `HIGH_CONFIDENCE` work during Phase 1.
10. Run validation after each write pass and again at phase end.
11. Run a final review before declaring the phase complete.
12. If a pass introduces a new validation failure, fix it within that pass or revert or defer that pass. Do not stack more cleanup on a broken tree.
13. If the user asks for a commit, stage only files changed by the cleanup pass you are reporting. Never treat `commit everything` as permission to stage unrelated changes.
14. If the same file contains unrelated local edits, do not commit cleanup hunks from that file unless the unrelated edits are clearly separable and intentionally preserved.
15. `RECOMMENDED` and `AGGRESSIVE` work require approval after the queue is reported. Broad wording like `do the aggressive cleanup too` does not count until the queued items or phase are surfaced and approved.
16. If a commit is requested, verify that the staged diff matches the reported cleanup files before creating the commit.
17. Freeze the selected item queue and claimed files for each phase before the first write pass starts. Final review compares the diff against that frozen queue, not against post-hoc reporting.
18. Freeze the exact validation matrix before writes start. In a monorepo, list the package-level or project-level commands explicitly instead of relying on one convenient top-level command.
19. Snapshot, golden-file, or approval-fixture updates are never automatically `HIGH_CONFIDENCE`. Treat them as `RECOMMENDED` unless the user explicitly asked for that refresh.
20. If a claimed file already contains pre-existing staged hunks, exclude that file from cleanup or prove hunk-level isolation before any write.
21. If a claimed file already contains unrelated unstaged local edits, exclude that file from cleanup or prove hunk-level isolation before any write.
22. All 8 research subagents must complete with usable findings or an explicit `no high-confidence changes` result before queue integration starts.
23. Final review must be performed by a non-writing reviewer.
24. Each write pass must be captured as a reversible unit before handoff so that rollback can target that pass without touching unrelated local work.
25. If any required subagent cannot be launched, times out, or returns unusable output, stop the phase. Do not integrate a partial research set.
26. Once a phase queue is frozen, newly discovered items are deferred to the next queue. Do not append them mid-phase.
27. Do not weaken tests, mocks, helpers, fixtures, or assertions just to make validation green. Any test-side change that affects behavioral verification is at least `RECOMMENDED`.

## Preflight

Before spawning subagents, inspect the repo and record:

- language and framework mix
- monorepo vs single package and package manager
- entry points and major module boundaries
- baseline snapshot identifier for the phase
- explicit user-specified scope slices, if any
- generated, vendor, or do-not-touch paths
- strongest available validation commands
- exact validation matrix for every relevant package, service, or language boundary
- baseline validation status for each command
- staged hunks already present in the worktree
- runtime trust boundaries where `unknown` or weak typing is intentional
- dirty files already present in the worktree

Default exclusions unless the user overrides them explicitly:

- generated outputs and caches: `node_modules`, `dist`, `build`, `.next`, `.turbo`, `coverage`
- vendor and third-party directories
- lockfiles and dependency manifests unless the current pass is auditing unused dependencies

Tooling rules:

- Prefer repo-local or already-installed tools.
- Do not install new tools automatically unless the environment or user policy already allows it.
- If a preferred tool is unavailable, report that gap and continue with non-speculative evidence gathering.

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

## Write Ownership And Snapshot Invalidation

- All research findings are tied to the repo snapshot seen during that research pass.
- If the user scoped cleanup to a broad subset such as multiple packages, keep the sweep inside that slice instead of silently widening to the whole repo.
- Before editing, the active writer must re-check every claimed file and directly affected module boundary against the current tree.
- If another pass changed a claimed file or any dependency a reasonable reviewer could see as affecting the finding, re-research before editing.
- If two areas need the same file, serialize them and hand off only after validation.
- If a file contains unrelated local edits, cleanup is no longer automatically high-confidence.

Proof of hunk-level isolation means a baseline diff for the file plus a current diff showing the unrelated hunks unchanged and the cleanup hunks separately selectable for staging or rollback. Eyeballing is not enough.

Reviewer independence means a different agent or subagent that did not mutate files in the current phase.

Usable findings means concrete evidence, affected files, and an actionable ranked recommendation, or an explicit `no high-confidence changes` result with evidence. Boilerplate without evidence is unusable.

Reversible unit means a persisted patch or temporary commit that can be applied or reverted mechanically. A mental undo plan is not enough.

## Shared Context For Every Subagent

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

- Prefer explicit tools where available: `knip`, `deadcode`, `vulture`, or the closest safe equivalent.
- Pair tool output with manual verification.
- Do not remove code with unresolved dynamic reachability.

### 4. Circular Dependency Cleanup

- Build the actual dependency chain before proposing a fix.
- Prefer extraction, dependency inversion, or smaller shared modules over broad rewrites.

### 5. Weak Type Strengthening

- Replace weak types only when the source type is proven by usage, package types, or runtime validation.
- Keep `unknown` at trust boundaries unless a validator or guard proves the shape.

### 6. Error Handling Audit

- Classify cases as `BOUNDARY_KEEP`, `RECOVERY_KEEP`, `HIDDEN_ERROR_REVIEW`, `VALUELESS_WRAPPER_REVIEW`, or `SAFE_REMOVE`.
- Auto-apply only `SAFE_REMOVE` items in `HIGH_CONFIDENCE`.

### 7. Legacy / Deprecated / Fallback Cleanup

- Remove deprecated, obsolete, or permanently-off code only when reachability and compatibility are clear.
- Defer anything that still has uncertain downstream behavior.

### 8. Noise / Obsolete Comment Cleanup

- Remove stale migration notes, dead stubs, leftover debug prints, and AI slop.
- Preserve comments that explain non-obvious intent, constraints, or tradeoffs.

If a subagent finds nothing worth changing, it must still report `no high-confidence changes` with evidence.

## Safe Integration Order

Do not reorder these write passes:

`Shared Types -> Unused Code -> Circular Dependencies -> DRY Deduplication -> Weak Type Strengthening -> Legacy Cleanup -> Error Handling Audit -> Noise / Obsolete Comment Cleanup`

## Phase Flow

### Phase 1: High-Confidence Cleanup

1. Spawn all 8 subagents for read-only research.
2. Wait for all 8 subagents to return usable findings or explicit no-change results.
3. If any required result is missing or unusable, stop the phase.
4. Integrate findings and select only `HIGH_CONFIDENCE` items.
5. Freeze the approved Phase 1 queue and claimed files before the first mutation.
6. Run write passes in the safe order above, one active writer at a time, and capture each pass as a reversible unit before handoff.
7. After each write pass, run validation before handing off to the next writer.
8. Defer any newly discovered items to the next queue instead of appending them mid-phase.
9. Run full end-of-phase validation.
10. Run final review against the frozen queue using a non-writing reviewer.
11. Report what changed and queue the deferred `RECOMMENDED` and `AGGRESSIVE` items.

### Phase 2: Recommended Cleanup

Run only if the user explicitly asks for recommended items.

- Only proceed after Phase 1 final review reports the recommended queue.
- Require approval of the recommended queue or the recommended phase after it is surfaced.
- Freeze the approved recommended queue and claimed files before mutation.
- Re-freeze the full validation matrix for this phase before mutation. It may widen, but must not narrow silently.
- Use one active writer at a time and capture each write pass as a reversible unit before handoff.
- Re-research the affected modules.
- Apply only the approved `RECOMMENDED` items.
- Run validation after each write pass before handoff.
- Run full validation and final review again.

### Phase 3: Aggressive Cleanup

Run only if the user explicitly asks for aggressive items.

- Only proceed after the aggressive queue is reported.
- Require approval of the aggressive queue or the aggressive phase after it is surfaced.
- Freeze the approved aggressive queue and claimed files before mutation.
- Re-freeze the full validation matrix for this phase before mutation. It may widen, but must not narrow silently.
- Use one active writer at a time and capture each write pass as a reversible unit before handoff.
- Re-research and restate the risk before editing.
- Apply only the approved `AGGRESSIVE` items.
- Run validation after each write pass before handoff.
- Run full validation and final review again.

## Validation Requirements

Validation means all strongest repo-available checks found in preflight, plus cleanup-specific checks where they exist.

Preferred order:

1. typecheck
2. lint
3. tests
4. build or compile checks
5. dead-code analysis relevant to the current pass
6. cycle detection relevant to the current pass

Validation rules:

- Freeze the exact validation matrix during preflight and run that matrix, not a reduced subset, after each write pass and at phase end.
- Record the exact baseline result for each command before writing, including the full failing set or a lossless normalized form that preserves every failing file, test, rule, and message when the command is already red.
- If a command already fails at baseline, the same failure may remain only if that recorded failure set is unchanged.
- Any new failure, changed failure, or newly failing command is a regression.
- A regression blocks the phase until the active pass fixes, reverts, or defers its own changes.
- Do not update snapshots, golden files, or approval fixtures as a Phase 1 escape hatch.
- Do not edit ordinary tests, assertions, mocks, helpers, or fixtures as a Phase 1 escape hatch.
- If a validation command is flaky or nondeterministic, do not fish for green by rerunning until it passes. Record the instability, follow one documented rerun policy, and stop if results remain inconsistent.
- Do not claim success without actual command output.

## Failure Recovery

- Missing tool: report it, lower confidence, and avoid speculative cleanup that depended on it.
- Dirty overlapping file: stop or downgrade unless ownership is clear.
- Stale research: re-research before writing.
- If invalidation is indirect through an upstream or downstream module change, re-research anyway.
- Validation regression: fix within the current pass or revert or defer that pass.
- Rollback must target only the active pass by using its reversible unit. Do not guess at manual partial reverts on a dirty tree.
- Snapshot or golden-file update required to make validation green: downgrade to `RECOMMENDED` unless the user explicitly requested that refresh.
- Uncertain dynamic reference: downgrade to `RECOMMENDED` or leave untouched.
- True conflict with concurrent human edits: stop and ask.
- Pre-existing staged hunks in a claimed file: do not absorb them silently. Either preserve them outside the cleanup commit or stop.
- Pre-existing staged hunks in a claimed file before writing: exclude the file or prove hunk-level isolation first.
- Pre-existing unstaged unrelated edits in a claimed file before writing: exclude the file or prove hunk-level isolation first.

## Common Mistakes

- Treating `full-repo sweep` as permission to touch unrelated dirty files.
- Treating `commit everything` as permission to stage unrelated changes.
- Treating snapshot or golden-file refreshes as a mechanical cleanup fix.
- Using `HIGH_CONFIDENCE` as a feeling instead of a checklist.
- Reusing stale findings after earlier passes changed the same file.
- Running only fast checks and calling that full validation.
- Hiding critical execution rules in a support file instead of `SKILL.md`.

## Final Review

The final review must be owned by a non-writing reviewer and must verify all of the following:

1. Every applied change maps to a reported finding.
2. No excluded paths changed.
3. The diff matches the frozen queue for that phase.
4. No unrelated local changes or pre-existing staged hunks were overwritten or absorbed silently.
5. Mixed files use hunk-level staging, or they stay out of the cleanup commit.
6. The frozen validation matrix actually ran and its outcomes are recorded.
7. No snapshot, golden-file, or approval-fixture refresh was silently absorbed into Phase 1.
8. Deferred `RECOMMENDED` and `AGGRESSIVE` items are listed clearly.
9. Residual risks and manual follow-ups are explicit.

## Final Report Template

Always end with:

1. Preflight assumptions used
2. Baseline repo state and validation results
3. Files changed and why
4. Validation results after each phase
5. Remaining `RECOMMENDED` items
6. Remaining `AGGRESSIVE` items
7. Residual risks and manual follow-ups

## Skill Testing

Use `testing-scenarios.md` to run RED/GREEN/REFACTOR checks against this skill. That file validates the skill; it does not define runtime behavior.
