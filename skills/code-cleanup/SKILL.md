---
name: code-cleanup
description: >
  Deep codebase cleanup skill that automatically launches 8 specialized subagents for DRY deduplication,
  shared type consolidation, dead code removal, circular dependency cleanup, weak-type replacement,
  error-handling audits, legacy/fallback removal, and AI-slop/comment cleanup. Use whenever the user asks
  to clean up a codebase, improve code quality, remove dead code, fix types, untangle dependencies,
  simplify code paths, or invokes /code-cleanup. Runs a full-repo sweep by default, auto-applies only
  high-confidence changes, then offers recommended and aggressive follow-up phases with full validation
  and a final review pass.
---

# Codebase Cleanup Skill

Run an end-to-end cleanup with 8 specialized subagents. This skill must preserve the original cleanup intent:
1. Deduplicate and consolidate code where DRY reduces complexity.
2. Consolidate shared type definitions.
3. Remove truly unused code and deps (tool-assisted + manual verification).
4. Untangle circular dependencies.
5. Replace weak types (`any`, `unknown`, equivalents) with strong types using evidence.
6. Remove unnecessary defensive/error-handling wrappers.
7. Remove deprecated, legacy, fallback, and duplicate code paths.
8. Remove AI slop, stubs, and unhelpful comments.

Each subagent must do detailed research, write a critical assessment, and implement high-confidence recommendations during its assigned write turn.

## Non-Negotiable Contract

1. Always use exactly 8 subagents, one per cleanup area above.
2. Default to a full-repo sweep, excluding only explicit do-not-touch paths.
3. Subagents may research in parallel, but only one subagent may mutate repo-tracked files at a time unless the user explicitly accepts merge-conflict risk.
4. Integrate write passes in the safe order defined below.
5. Every subagent must produce:
   - research findings with concrete evidence (files/lines/tool output),
   - critical assessment and recommendations,
   - applied changes for high-confidence items when it is the active write owner.
6. After each integration pass, run validation. Stop and report on failure.
7. After each phase, run a final review pass before closing.

## Phase 0: Auto-Infer Preflight

Before spawning agents, inspect the repo and infer:
- language/framework(s),
- monorepo vs single package and package manager,
- entry points and major module boundaries,
- generated/vendor/do-not-touch paths,
- strongest available validation commands (typecheck/lint/test/build),
- any known runtime boundary modules where `unknown` is intentional.

Ask follow-up questions only when missing data would make changes risky. Otherwise proceed.

Default exclusions (unless user overrides):
- generated outputs and package caches (`node_modules`, `dist`, `build`, `.next`, `.turbo`, `coverage`),
- third-party/vendor directories,
- lock files and dependency manifests unless the pass explicitly targets unused dependencies.

## Apply Tiers

Use 3 explicit tiers:

- `HIGH_CONFIDENCE`:
  - auto-apply by default.
  - must be mechanical and low ambiguity.
  - must preserve behavior and public contracts.
  - validation must pass after the change batch.
- `RECOMMENDED`:
  - medium-risk or intent-sensitive improvements.
  - do not auto-apply in the first pass.
  - present as opt-in queue after high-confidence completion.
- `AGGRESSIVE`:
  - high-risk restructures, broader rewrites, and subjective cleanup.
  - never auto-apply by default.
  - only run when explicitly requested.

When the user opts into `RECOMMENDED` or `AGGRESSIVE`:
- re-research affected areas (do not do a lazy pass),
- produce a mini plan for that phase,
- implement thoroughly,
- run full validation and final review again.

## Safe Integration Order (Do Not Reorder)

Keep the 8 subagents mapped to the original cleanup areas above, but integrate their write passes in this sequence:

`2 Types -> 3 Unused -> 4 Circular -> 1 DRY -> 5 Strengthen Types -> 7 Legacy -> 6 Error Handling -> 8 Slop/Comments`

## Shared Context (Inject Into Every Subagent Prompt)

```text
CODEBASE CONTEXT:
- Scope: full-repo sweep except exclusions
- Language/Framework: {language_framework}
- Package manager/workspace: {pkg_manager_or_workspace}
- Entry points: {entry_points}
- Do NOT touch: {exclusion_list}
- Validation commands: {validation_commands}
- Current apply tier: {HIGH_CONFIDENCE | RECOMMENDED | AGGRESSIVE}
- Write mode: {RESEARCH_ONLY | ACTIVE_WRITE_TURN}

REQUIRED OUTPUT FORMAT:
1) Research findings (evidence + file paths)
2) Critical assessment
3) Ranked recommendations with confidence (high/medium/low)
4) Applied changes for in-scope tier
5) Risks and deferred items
```

## Subagent Instructions

### 1) DRY / Deduplication
- Find copy-pasted logic, repeated helper logic, repeated constants/config branches.
- Merge only when abstraction reduces complexity and improves readability.
- Keep intentionally duplicated domain-isolated logic when merging would add condition-heavy abstractions.

### 2) Shared Type Consolidation
- Find duplicate/near-duplicate types, interfaces, structs, schemas, and DTO shapes.
- Merge only semantically equivalent types.
- Do not merge accidentally identical shapes from different domains.

### 3) Unused Code Removal
- Use explicit tools where applicable:
  - TypeScript/JS: run `knip` (install with `npx knip` if needed)
  - Go: run `go vet`, `staticcheck`, and `deadcode`
  - Python: run `vulture`
  - Other languages: use the closest equivalent dead-code tool
- Pair tool output with manual verification.
- Verify no runtime/dynamic references (reflection, plugin lookup, string-based access).
- Include unused dependencies in the audit.
- Never remove excluded paths or uncertain downstream API exports without explicit confirmation.

### 4) Circular Dependency Cleanup
- Use explicit tools where applicable:
  - TypeScript/JS: run `madge --circular` (install with `npx madge` if needed)
  - Go: use `goda` or `go list`-based dependency graph inspection
  - Other languages: use the closest equivalent dep-graph tool
- Build dependency graph and list cycles with full chains.
- Resolve via shared module extraction, dependency inversion, or DI.
- Prioritize production cycles before test-only cycles.

### 5) Weak Type Strengthening
- Replace weak types (`any`, `unknown`, `object`, `{}`, ignores) with concrete types when evidence exists.
- Research source types from local code, package typings, and usage flow.
- Keep `unknown` at true trust boundaries (external input, parse boundaries).
- Narrow boundary `unknown` only when the code already has, or this pass introduces, a runtime validator, parser, or type guard that proves the shape. Passing compile validation alone is not enough.
- Never invent speculative types.

### 6) Error Handling and Defensive Pattern Audit
- Audit `try/catch`, `.catch`, fallback wrappers, and equivalent patterns.
- Categorize each case:
  - `A KEEP`: boundary handling for unknown or unsanitized input
  - `B KEEP`: specific recovery logic, retries, or rethrows with added context
  - `C REVIEW`: empty catch, log-and-swallow, or otherwise unhelpful error hiding
  - `D REVIEW`: identical rethrow or wrapper with no added value
  - `E REMOVE`: deterministic internal wrapper with no recovery value
- Auto-apply only category `E` in `HIGH_CONFIDENCE`.
- Hold `C` and `D` for `RECOMMENDED` or `AGGRESSIVE` review unless the user explicitly asks for more aggressive cleanup.

### 7) Legacy / Deprecated / Fallback Cleanup
- Find deprecated tags, legacy/versioned branches, always-on/off feature flags, commented-out code, obsolete shims.
- Remove cleanly when safe.
- Keep or defer when uncertainty exists about behavior compatibility.

### 8) AI Slop / Stub / Comment Cleanup
- Remove noise comments, stale migration notes, dead stubs/placeholders, leftover debug prints.
- Preserve and improve comments that explain non-obvious intent, constraints, or tradeoffs.
- Rewrite confusing comments concisely for newcomers.

## Phase Flow

### Phase 1: High-Confidence Cleanup (Default)
1. Spawn all 8 subagents for research + assessment.
2. Keep the initial research pass read-only across all 8 subagents.
3. Integrate and apply only `HIGH_CONFIDENCE` recommendations in the safe integration order above, with one active write owner at a time.
4. After each write owner finishes, run validation before handing write access to the next owner.
5. Run a full end-of-phase validation pass.
6. Run a final review pass and summarize:
   - what changed,
   - what remains in `RECOMMENDED`,
   - what remains in `AGGRESSIVE`,
   - any manual decision points.

### Phase 2: Recommended Cleanup (Opt-In)
Run only if user explicitly asks to proceed with recommended items.
- Re-research affected modules,
- apply `RECOMMENDED` items thoroughly,
- run full validation,
- run final review pass.

### Phase 3: Aggressive Cleanup (Opt-In)
Run only if user explicitly asks to proceed with aggressive items.
- Re-research and explicitly state risk/tradeoff,
- apply `AGGRESSIVE` items thoroughly,
- run full validation,
- run final review pass.

## Validation Requirements

Use the strongest repo-available checks. Prefer:
1. typecheck
2. lint
3. tests
4. build or compile checks

Also run cleanup-specific checks where applicable:
- dead-code tool (`knip`, `vulture`, etc.),
- cycle detection (`madge` or equivalent).

Do not declare completion until validation passes for the active phase and the final review pass is done.

## Final Report Template

Always end with:
1. Preflight assumptions used
2. Files changed and why
3. Validation results (all commands + outcome)
4. Remaining `RECOMMENDED` items
5. Remaining `AGGRESSIVE` items
6. Residual risks and manual follow-ups
