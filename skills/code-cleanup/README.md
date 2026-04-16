# Code Cleanup Skill

Disciplined repo-wide cleanup for technical debt and maintainability work. Uses 8 specialized subagents to cover deduplication, type consolidation, unused code, circular dependencies, weak types, error handling, legacy paths, and comment noise.

Designed for multi-agent coding harnesses (Claude Code, OpenCode, Copilot CLI, Droid, etc.) with subagent support. Language-agnostic — works with TypeScript, Go, Python, Rust, Java, Ruby, C#, and others.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Agent instructions. This is what the model reads and follows during cleanup. | Yes |
| `testing-scenarios.md` | Pressure tests for validating the skill itself. 20 edge-case scenarios + 26 known loopholes. | No |
| `README.md` | Documentation for humans. You're reading it. | No |

Only `SKILL.md` gets loaded into the agent's context when the skill triggers. The other files ship alongside it for development and documentation but have zero runtime cost.

## Use It For

- Repo-wide or monorepo cleanup passes
- Broad multi-package or multi-area cleanup sweeps
- Technical debt, code hygiene, or maintainability sweeps before release
- Repo-wide cleanup audits before editing
- Broad multi-area cleanup inside one large app, package, or service
- Explicit `/code-cleanup` invocation

## Do Not Use It For

- Single bugfixes or feature work
- Pure formatting
- Code search, explanation, or review-only requests
- Narrow single-file or single-helper fixes

## How It Works

1. **Preflight**: Inspects the repo — language mix, package structure, validation commands, dirty files, baseline state.
2. **Research (read-only)**: All 8 subagents run in parallel, producing findings with evidence.
3. **Phase 1 (auto-apply)**: Only `HIGH_CONFIDENCE` items get applied — local, mechanical, evidence-backed changes with no behavior change. Validated after each write pass.
4. **Phase 2 (opt-in)**: `RECOMMENDED` items are surfaced and require explicit approval before application.
5. **Phase 3 (opt-in)**: `AGGRESSIVE` items are surfaced and require explicit approval before application.

## Safety Guarantees

- 20-rule non-negotiable contract covering write ownership, validation, commit hygiene, and queue freezing.
- Never overwrites unrelated local changes or absorbs pre-existing staged hunks.
- Validation after every write pass — not just at the end.
- Phase 1 uses mechanical checklist review; Phase 2/3 use independent review agents.
- Reversible units for every write pass so rollback targets only the offending pass.
- Snapshot invalidation forces re-research when earlier passes change claimed files.

## Cleanup Areas

1. **DRY / Deduplication** — merge repeated logic only when it reduces complexity
2. **Shared Type Consolidation** — merge semantically identical types across the codebase
3. **Unused Code Removal** — using `knip`, `deadcode`, `vulture`, or language equivalents
4. **Circular Dependency Cleanup** — using `madge`, `goda`, or language equivalents
5. **Weak Type Strengthening** — replace `any`, `unknown`, `interface{}`, `Any`, `Object`, `dynamic` with proven types
6. **Error Handling Audit** — classify and clean `try/catch`, `if err != nil`, `Result`/`unwrap`, `rescue`, etc.
7. **Legacy / Deprecated / Fallback Cleanup** — remove dead paths with clear reachability
8. **Noise / Obsolete Comment Cleanup** — remove AI slop, stubs, dead comments; preserve intent comments

## Skill Testing

Use [`testing-scenarios.md`](./testing-scenarios.md) to pressure-test the skill with RED/GREEN/REFACTOR scenarios. It contains 20 edge-case execution scenarios (dirty worktrees, flaky validation, scope creep, stale findings, etc.) and 26 common loopholes to watch for. Run these after modifying `SKILL.md` to validate your changes.

## Model Compatibility

Designed for frontier instruction-following models: Claude Opus/Sonnet 4.6, GPT-5.4, Kimi K2.5, GLM-5.1. On weaker models, Phase 1 auto-apply may benefit from manual approval checkpoints.
