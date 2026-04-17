---
name: code-cleanup
version: 1.0.0
description: Repo-wide or broad multi-area codebase cleanup using 8 subagents to remove dead code, duplicates, circular dependencies, weak types, legacy paths, and stale comments. Triggers on cleanup, audit, code hygiene, technical debt sweeps, `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, or `/code-cleanup dry-run`.
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

Use these slash commands as the canonical tier selectors:

- `/code-cleanup` -> `requested_max_tier=SAFE`, `approval_source=DEFAULT_SAFE_ONLY`, `mode=WRITE`
- `/code-cleanup review` -> `requested_max_tier=REVIEW`, `approval_source=EXPLICIT_UPFRONT_TIER`, `mode=WRITE`
- `/code-cleanup risky` -> `requested_max_tier=RISKY`, `approval_source=EXPLICIT_UPFRONT_TIER`, `mode=WRITE`
- `/code-cleanup dry-run` -> `mode=DRY_RUN`, surfaces all three tier queues without writing.

Space-separated syntax is canonical. If the user writes a close natural-language equivalent that clearly names the same tier, normalize it to the matching invocation mode. A trailing colon is tolerated but not required.

Interpretation rules:

1. `requested_max_tier` is the highest cleanup tier the run may execute.
2. `approval_source=EXPLICIT_UPFRONT_TIER` counts as approval for later risky phases only after that phase queue is surfaced and frozen.
3. Queue surfacing is still mandatory for `REVIEW` and `RISKY` work. Upfront authorization removes the extra approval round-trip; it does not remove queue freeze, re-research, validation, or final review requirements.
4. Vague wording such as `do the risky cleanup too` does not count as structured upfront tier authorization. Treat it as a normal request that still needs post-queue approval.
5. If the user later narrows or expands the tier explicitly, the most explicit later instruction wins for phases that have not started yet.
6. `mode=DRY_RUN` must not create any reversible units, commits, or file writes anywhere in the run. Dry-run never holds queue freeze for a later write run; a subsequent write run re-runs research from scratch.

## Non-Negotiable Contract

1. Always use exactly 8 subagents, one per cleanup area. If the harness cannot run 8 workers in parallel, serialize the research pass into 8 sequential read-only passes — never merge, combine, or skip cleanup areas.
2. Default to a full-repo sweep except explicit exclusions or an explicit broad user-specified subset scope.
3. The initial pass is read-only across all 8 subagents.
4. Only one subagent may mutate repo-tracked files at a time. The active writer must claim the exact files or modules it will edit.
5. If earlier write passes changed a claimed file or any dependency a reasonable reviewer could see as affecting the finding, the current writer must re-research before editing.
6. Record baseline repo state before any writes: branch, HEAD commit, dirty files, staged hunks, validation commands, validation failures, files-in-scope count, and a computed baseline snapshot ID (see Preflight).
7. Protect unrelated changes: never overwrite unrelated local edits. If intent is unclear in overlapping files, stop and ask. Stage only files changed by the cleanup pass being reported. Never treat `commit everything` as permission to stage unrelated work. Do not commit cleanup hunks from a mixed file unless the unrelated edits are clearly separable and intentionally preserved. Verify that the staged diff matches the reported cleanup files before creating a commit.
8. Auto-apply only `SAFE` work during Phase 1.
9. Run validation after each write pass and again at phase end.
10. If a pass introduces a new validation failure, fix it within that pass or revert or defer that pass. Do not stack more cleanup on a broken tree.
11. `REVIEW` and `RISKY` work require an approved queue after it is surfaced. Approval may come from explicit upfront tier invocation or from a later post-queue confirmation. Broad wording like `do the risky cleanup too` does not count as upfront tier authorization.
12. Freeze the selected item queue and claimed files for each phase before the first write pass starts. Final review compares the diff against that frozen queue, not against post-hoc reporting.
13. Freeze the exact validation matrix before writes start. In a monorepo, list the package-level or project-level commands explicitly instead of relying on one convenient top-level command.
14. Snapshot, golden-file, or approval-fixture updates are never automatically `SAFE`. Treat them as `REVIEW` unless the user explicitly asked for that refresh.
15. Files with pre-existing staged hunks or unrelated unstaged local edits: exclude the file from cleanup or prove hunk-level isolation before any write (see Key Definitions for exact git commands).
16. All 8 research subagents must complete with usable findings or an explicit `NO_CHANGES` status before queue integration starts. If any subagent cannot be launched, times out, or returns output that fails schema validation, stop the phase. Do not integrate a partial research set. Subagents fail silently; trust the schema, not the subagent's self-report of success.
17. Each write pass must be captured as a reversible unit before handoff so that rollback can target that pass without touching unrelated local work.
18. Once a phase queue is frozen, newly discovered items are deferred to the next queue. Do not append them mid-phase.
19. Do not weaken tests, mocks, helpers, fixtures, or assertions just to make validation green. Any test-side change that affects behavioral verification is at least `REVIEW`.
20. Final review for Phase 1: the orchestrator verifies the frozen queue checklist mechanically. For Phase 2 and Phase 3: the orchestrator spawns a dedicated review subagent that receives the frozen queue, the diff, and validation results but did not participate in any write pass for that phase. The asymmetry is intentional: Phase 1 items are mechanically checklist-verifiable (diff matches queue, validation passes, no excluded paths touched, no unrelated changes absorbed), while Phase 2 and Phase 3 items are judgment calls about abstraction, reachability, and error semantics, and having a writer review their own judgment invites confirmation bias.
21. Commit granularity is one commit per phase. Each phase produces exactly one commit covering all write passes integrated in that phase. Commit subject: `chore: code cleanup phase <N> (<tier>)`. Commit body lists the frozen queue items and validation outcomes. Never commit mid-phase.
22. Cross-language boundary files (OpenAPI-generated types, gRPC/Protobuf stubs, FFI bindings, IDL-generated code) are default-excluded unless the user explicitly opts in. If a proposed cleanup touches one of these files, downgrade to `REVIEW` regardless of other evidence.
23. Every subagent output must conform to the Subagent Output Schema. Non-conforming output is unusable under Rule 16 and blocks queue integration. The orchestrator validates the schema before integrating findings.
24. The orchestrator owns all subagent context injection. Subagent context windows start fresh with nothing inherited from the parent; the full Shared Context block must be passed in the spawning prompt string for every subagent, on every invocation.

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
- `SAFE` always runs first when any cleanup tier is approved.
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

Every subagent MUST return a response that exactly matches this Markdown template. The orchestrator validates each output before queue integration. Non-conforming output is unusable and blocks the phase under Rule 16.

```text
# SUBAGENT_REPORT

## status
<one of: SAFE_FINDINGS | REVIEW_FINDINGS | RISKY_FINDINGS | NO_CHANGES | BLOCKED>

## subagent
<exact name of this cleanup area, one of the 8>

## snapshot_id
<baseline snapshot ID from Shared Context; must match exactly>

## findings
<one block per finding, or the literal word "none" if status is NO_CHANGES or BLOCKED>

### finding_1
- tier: <SAFE | REVIEW | RISKY>
- files: <absolute paths, one per line, indented>
- evidence: <concrete: symbol name, line numbers, tool output excerpt>
- proposed_change: <single sentence describing the edit>
- validation_impact: <which commands from the matrix this affects, or "none">
- blockers: <dynamic references, dirty overlap, boundary files, or "none">

### finding_2
<same structure>

## blocker_reason
<required only if status is BLOCKED; one paragraph explaining why research could not proceed>

## reason
<required only if status is NO_CHANGES; one paragraph explaining why nothing was found>
```

Schema validation rules the orchestrator enforces:

- `status`, `subagent`, and `snapshot_id` are always required.
- `snapshot_id` must equal the value provided in Shared Context. Mismatch triggers Rule 5 re-research.
- If `status` is one of `SAFE_FINDINGS | REVIEW_FINDINGS | RISKY_FINDINGS`, at least one finding must be present and every finding must have all six fields.
- If `status` is `NO_CHANGES`, `findings` must be `none` and `reason` must be present.
- If `status` is `BLOCKED`, `findings` must be `none` and `blocker_reason` must be present.
- Every `files` entry must be an absolute path that exists in the repo snapshot.
- `evidence` cannot be boilerplate. `"code is unused"` is boilerplate; `"src/utils/format.ts:12 formatCurrency exported but knip reports 0 imports"` is evidence.

## Phase Flow

### Phase 0: Dry-Run (mode=DRY_RUN only)

Triggered only by `/code-cleanup dry-run`.

1. Run preflight.
2. Run the self-check above.
3. Spawn all 8 subagents for read-only research with the full Shared Context block.
4. Wait for all 8 to return schema-conforming findings or explicit `NO_CHANGES` results.
5. Integrate findings across all tiers.
6. Report the proposed SAFE, REVIEW, and RISKY queues with evidence, claimed files, and validation impact for each item.
7. Exit. Do not write, commit, or create any reversible units.

### Phase 1: Safe Cleanup

1. Run the self-check above.
2. Spawn all 8 subagents for read-only research with the full Shared Context block.
3. Wait for all 8 to return schema-conforming findings or explicit `NO_CHANGES` results.
4. If any required result is missing, unusable, or fails schema validation, stop the phase.
5. If the findings do not all reference the same baseline snapshot identifier, stop and re-run affected research.
6. Integrate findings and select only `SAFE` items.
7. Freeze the approved Phase 1 queue and claimed files before the first mutation.
8. Run write passes in the Safe Integration Order, one active writer at a time, and capture each pass as a reversible unit before handoff.
9. After each write pass, run validation before handing off to the next writer.
10. Defer any newly discovered items to the next queue instead of appending them mid-phase.
11. Run full end-of-phase validation.
12. Run final review: the orchestrator mechanically verifies that every applied change maps to a finding, no excluded paths changed, the diff matches the frozen queue, no unrelated changes were absorbed, the validation matrix ran and outcomes are recorded, no snapshot refreshes were absorbed, and deferred items are listed.
13. Create exactly one Phase 1 commit covering all Phase 1 write passes.
14. If commit hooks mutate files after the commit, apply the Commit Hook Handling protocol in Failure Recovery.
15. Report what changed and queue the deferred `REVIEW` and `RISKY` items.

### Phase 2: Review Cleanup

Run only if `requested_max_tier` allows `REVIEW` work and the review queue is approved.

- Only proceed after Phase 1 final review reports the review queue.
- Require approval of the review queue or phase after it is surfaced, unless explicit upfront tier invocation already supplied that approval.
- Freeze the approved review queue and claimed files before mutation.
- Re-freeze the full validation matrix for this phase. It may widen, but must not narrow silently.
- Use one active writer at a time with reversible units before handoff.
- Re-research the affected modules before writing.
- Apply only the approved `REVIEW` items.
- Run validation after each write pass before handoff.
- The orchestrator spawns a dedicated review subagent (not a writer from this phase) to run full validation and final review.
- Create exactly one Phase 2 commit covering all Phase 2 write passes.
- Apply commit hook handling if hooks mutate files after commit.

### Phase 3: Risky Cleanup

Run only if `requested_max_tier` allows `RISKY` work and the risky queue is approved.

- Only proceed after the risky queue is reported and approved.
- Freeze the approved risky queue and claimed files before mutation.
- Re-freeze the full validation matrix. It may widen, but must not narrow silently.
- Use one active writer at a time with reversible units before handoff.
- Re-research and restate the risk before editing.
- Apply only the approved `RISKY` items.
- Run validation after each write pass before handoff.
- The orchestrator spawns a dedicated review subagent (not a writer from this phase) to run full validation and final review.
- Create exactly one Phase 3 commit covering all Phase 3 write passes.
- Apply commit hook handling if hooks mutate files after commit.

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

Polyglot rule:

- Each cleanup pass is scoped to one language's files and validates against that language's matrix only.
- A baseline failure in language X does not block cleanup in language Y, provided no file edited in this pass crosses a language boundary.
- Cross-language boundary files follow Rule 22 and are default-excluded.
- The frozen validation matrix must explicitly list which language's commands run for which pass. A top-level monorepo command is not a substitute.

## Preflight

Before spawning subagents, inspect the repo and record:

- language and framework mix
- monorepo vs single package and package manager
- entry points and major module boundaries
- **baseline snapshot ID**: `sha256(git rev-parse HEAD || git diff HEAD || git ls-files --others --exclude-standard | sort)`. Store the three components themselves too so re-research can diff against each of them.
- **files in scope**: `git ls-files | grep -vE '<exclusion-regex>' | wc -l`
- explicit user-specified scope slices, if any
- generated, vendor, or do-not-touch paths
- cross-language boundary files (OpenAPI/Swagger, gRPC/Protobuf, FFI bindings, IDL-generated code)
- strongest available validation commands
- exact validation matrix for every relevant package, service, or language boundary
- baseline validation status for each command
- staged hunks and dirty files already present in the worktree
- runtime trust boundaries where `unknown` or weak typing is intentional

Repo-size guardrail:

- **< 5,000 files in scope**: proceed normally.
- **5,000 – 20,000 files**: proceed but include a "large repo" warning in the preflight report. Token burn will be significant at ~20k tokens overhead per subagent plus findings; flag it.
- **> 20,000 files**: stop and ask the user to scope the run to specific packages or directories. Do not spawn research subagents at this size without explicit scoping.

Default exclusions unless the user overrides them explicitly: generated outputs and caches (`node_modules`, `dist`, `build`, `.next`, `.turbo`, `coverage`, `target`, `vendor`), third-party directories, lockfiles and dependency manifests unless auditing unused dependencies, and all cross-language boundary files.

Tooling rules: prefer repo-local or already-installed tools. Do not install new tools automatically unless the environment or user policy allows it. If a preferred tool is unavailable, report that gap and continue with non-speculative evidence gathering.

## Write Ownership and Snapshot Invalidation

- All research findings are tied to the repo snapshot seen during that research pass. All findings integrated into one queue must reference the same snapshot identifier. If the repo state changes before queue freeze, re-run affected research.
- If the user scoped cleanup to a broad subset such as multiple packages, keep the sweep inside that slice instead of silently widening to the whole repo.
- Before editing, the active writer must re-check every claimed file and directly affected module boundary against the current tree.
- If another pass changed a claimed file or any upstream/downstream dependency a reasonable reviewer could see as affecting the finding, re-research before editing.
- If two areas need the same file, serialize them and hand off only after validation.
- If a file contains unrelated local edits, cleanup is no longer automatically SAFE.

Key definitions:

- **Baseline snapshot ID**: the sha256 computed in Preflight. Two findings that reference different IDs cannot be integrated into the same queue.
- **Usable findings**: output that passes the Subagent Output Schema, with concrete evidence and an actionable ranked recommendation, or an explicit `NO_CHANGES` status with a reason. Boilerplate without evidence is unusable.
- **Reversible unit**: a persisted patch (`git diff > /tmp/pass-N.patch`) or temporary commit on a feature branch that can be applied or reverted mechanically. A mental undo plan is not enough.
- **Frozen queue item**: one cleanup recommendation with all of the following: cleanup area, exact files or modules, evidence, intended edit scope, confidence tier, and validation impact. `Clean up module X` is not a valid queue item.
- **Cross-language boundary file**: any file whose content is generated from or binds to a different language's type system. Includes OpenAPI/Swagger generated types, gRPC/Protobuf stubs, FFI bindings, and IDL-generated code.

**Proof of hunk-level isolation** (exact commands, not eyeballing):

```sh
# Step 1 — capture baseline diffs BEFORE any cleanup edit
git diff HEAD -- <file> > /tmp/baseline-unstaged.diff
git diff --cached -- <file> > /tmp/baseline-staged.diff

# Step 2 — apply the cleanup edit

# Step 3 — capture current diff
git diff HEAD -- <file> > /tmp/current.diff

# Step 4 — verify isolation
# /tmp/current.diff MUST contain every hunk from /tmp/baseline-unstaged.diff
# unchanged, plus only new cleanup hunks. If any baseline hunk is missing
# or modified, isolation failed.

# Step 5 — to commit only cleanup hunks
git add -p <file>                  # interactively select only cleanup hunks
git diff --cached -- <file>        # must show only cleanup changes
git diff -- <file>                 # must equal /tmp/baseline-unstaged.diff exactly
```

If step 4 fails, the cleanup edit absorbed unrelated work. Revert via the reversible unit and exclude the file from cleanup.

## Shared Context for Every Subagent

The orchestrator injects this full block into every subagent spawning prompt. Subagent context windows start empty — nothing is inherited from the parent. On every subagent invocation, pass this entire block in the prompt string.

```text
CODEBASE CONTEXT:
- Scope: {cleanup_scope}
- Language/Framework: {language_framework}
- Package manager/workspace: {pkg_manager_or_workspace}
- Entry points: {entry_points}
- Do NOT touch: {exclusion_list}
- Cross-language boundary files: {boundary_files}
- Dirty files before cleanup: {dirty_files}
- Baseline snapshot ID: {snapshot_id}
- Files in scope: {files_in_scope_count}
- Validation commands: {validation_commands}
- Baseline validation failures: {baseline_failures}
- Current apply tier: {SAFE | REVIEW | RISKY}
- Write mode: {RESEARCH_ONLY | ACTIVE_WRITE_TURN | DRY_RUN}
- Active write owner: {cleanup_area_name | none}

REQUIRED OUTPUT:
Return a single Markdown document matching the Subagent Output Schema in SKILL.md.
Non-conforming output blocks queue integration.
```

## Subagent Map

The 8 areas below are listed in Safe Integration Order. Each subagent owns exactly one area and returns output matching the Subagent Output Schema.

### 1. Unused Code Removal

- Prefer explicit tools where available: `knip` (JS/TS), `deadcode`/`staticcheck` (Go), `vulture` (Python), or the closest safe equivalent for the language.
- Pair tool output with manual verification.
- Do not remove code with unresolved dynamic reachability.

### 2. Legacy / Deprecated / Fallback Cleanup

- Remove deprecated, obsolete, or permanently-off code only when reachability and compatibility are clear.
- Defer anything that still has uncertain downstream behavior.

### 3. Circular Dependency Cleanup

- Build the actual dependency chain before proposing a fix.
- Prefer extraction, dependency inversion, or smaller shared modules over broad rewrites.
- Use `madge` (JS/TS), `go list`/`goda` (Go), or the closest equivalent for the language.

### 4. Shared Type Consolidation

- Merge duplicate or near-duplicate types only when they are semantically the same.
- Do not merge accidentally similar shapes from different domains.

### 5. Weak Type Strengthening

- Replace weak types only when the source type is proven by usage, package types, or runtime validation.
- Language-specific targets: `any`/`unknown`/`object`/`{}`/`as any`/`@ts-ignore` (TS/JS), `interface{}`/`any` (Go), `Any` (Python), `Object`/raw types (Java), `dynamic` (C#/Dart).
- Keep `unknown` (or equivalent) at trust boundaries unless a validator or guard proves the shape.

### 6. DRY / Deduplication

- Merge repeated logic only when the abstraction clearly reduces complexity.
- Keep duplicated code when merging would create condition-heavy or domain-leaking abstractions.

### 7. Error Handling Audit

- Language-specific patterns: `try/catch` (JS/TS/Java/C#), `try/except` (Python), `if err != nil` (Go), `Result`/`unwrap`/`expect`/`panic` (Rust), `rescue` (Ruby).
- Classify each case: `BOUNDARY_KEEP` (external I/O, network, user input), `RECOVERY_KEEP` (retry, fallback with clear intent), `HIDDEN_ERROR_REVIEW` (swallowed, logged-only, or empty handler), `VALUELESS_WRAPPER_REVIEW` (re-throws/re-returns identically), or `SAFE_REMOVE` (wraps deterministic internal logic with no failure path).
- Auto-apply only `SAFE_REMOVE` items in `SAFE` tier.

### 8. Noise / Obsolete Comment Cleanup

- Remove stale migration notes, dead stubs, leftover debug prints, and AI slop.
- Preserve comments that explain non-obvious intent, constraints, or tradeoffs.

If a subagent finds nothing worth changing, it must still return a schema-conforming output with `status: NO_CHANGES` and a `reason`.

## Failure Recovery

- **Missing tool**: report it, lower confidence, and avoid speculative cleanup that depended on it.
- **Dirty overlapping file**: stop or downgrade unless ownership is clear.
- **Stale research** (including indirect invalidation through upstream/downstream module changes): re-research before writing.
- **Validation regression**: fix within the current pass or revert or defer that pass.
- **Rollback**: must target only the active pass by using its reversible unit. Do not guess at manual partial reverts on a dirty tree.
- **Snapshot or golden-file update required to make validation green**: downgrade to `REVIEW` unless the user explicitly requested that refresh.
- **Uncertain dynamic reference**: downgrade to `REVIEW` or leave untouched.
- **True conflict with concurrent human edits**: stop and ask.
- **Pre-existing staged hunks in a claimed file**: do not absorb them silently. Either preserve them outside the cleanup commit or stop. Exclude the file or prove hunk-level isolation before writing.
- **Cross-language boundary file in the proposed diff**: exclude the file or downgrade the entire item to `REVIEW`.
- **Subagent failed to launch, timed out, or returned non-conforming output**: stop the phase. Never integrate a partial research set.
- **Repo size exceeds 20,000 files in scope**: stop and require explicit scoping from the user before proceeding.

### Commit Hook Handling

Pre-commit hooks (formatters, linters, auto-fix tools) may mutate tracked files after the cleanup commit is staged. This creates a divergence between the reviewed diff and the committed artifact.

Protocol:

1. After the cleanup commit lands, compute the post-hook diff: `git diff HEAD~1 HEAD`.
2. Compare against the frozen queue. Every file in the post-hook diff must be in the frozen queue.
3. If any file in the post-hook diff is outside the frozen queue, revert the commit (`git reset --hard HEAD~1`) and stop. Do not amend — hook-introduced changes outside the frozen queue are a signal that the hook is doing cleanup the skill did not approve.
4. If all files match the frozen queue, accept the commit.
5. Maximum 2 iterations of "commit → hook mutates → re-review". If the hook keeps mutating files after 2 iterations, stop and report — something is looping.
6. Never use `git commit --no-verify` to sidestep hooks. That disables the team's quality gates.

## Worked Example

Compact end-to-end run on a small TypeScript Cloudflare Workers repo.

**Preflight:**

- Language: TypeScript, framework: Hono on Cloudflare Workers, package manager: pnpm
- Validation matrix: `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm build`
- Baseline: all green
- Dirty files: none. Staged hunks: none.
- Baseline snapshot ID: `sha256(HEAD=abc123... + diff=empty + untracked=empty)` = `f9e2...`
- Files in scope: 142 (under 5K threshold)
- Boundary files: `src/types/generated/openapi.d.ts` (flagged, default-excluded)

**Self-check:** orchestrator answers 5 anti-drift questions. No contradictions.

**Research:** orchestrator injects full Shared Context into all 8 subagents in parallel.

Schema-conforming outputs:

- **Unused Code** returns `SAFE_FINDINGS`: `src/utils/format.ts:12` exports `formatCurrency`; knip reports 0 imports. Evidence: knip output excerpt attached. Proposed: remove lines 12-18. Validation impact: none (no callers).
- **Weak Types** returns `REVIEW_FINDINGS`: `src/api/user.ts:23` has `function fetchUser(id: any): Promise<any>`. 3 call sites all pass `string` and destructure `{id, name, email}`. Proposed: change to `(id: string): Promise<User>`. Tier: `REVIEW` because it changes a public contract.
- Other 6 subagents return `NO_CHANGES` with reasons.

All 8 outputs reference `snapshot_id: f9e2...`. Schema validation passes.

**Phase 1 queue frozen:** `[finding_1 from Unused Code]`. Claimed files: `[src/utils/format.ts]`.

**Write pass:** removes `formatCurrency` from `src/utils/format.ts`. Reversible unit: `/tmp/pass-1.patch` captured.

**Validation after pass:** `pnpm typecheck` green, `pnpm lint` green, `pnpm test` green, `pnpm build` green. No regression from baseline.

**Phase 1 final review:** orchestrator checklist — diff matches frozen queue ✓, no excluded paths touched ✓, validation matrix ran ✓, no snapshot refresh absorbed ✓, deferred items listed ✓.

**Phase 1 commit:**

```text
chore: code cleanup phase 1 (safe)

Frozen queue:
- Unused Code: remove unused export formatCurrency from src/utils/format.ts

Validation: pnpm typecheck pass, pnpm lint pass, pnpm test pass, pnpm build pass
```

Pre-commit hook reformats one line in `src/utils/format.ts`. Post-hook diff covers only files in the frozen queue → accept.

**Run invoked as `/code-cleanup`** so `requested_max_tier=SAFE`, `approval_source=DEFAULT_SAFE_ONLY`. Run ends after Phase 1.

**Final report:**

- Applied: 1 change (unused export removal)
- Deferred REVIEW queue: 1 item (weak type in fetchUser)
- Deferred RISKY queue: 0 items
- Residual risk: the REVIEW item changes a public contract; inspect before approving.

## Final Report Template

Always end with:

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
