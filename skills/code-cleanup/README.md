# Code Cleanup Skill

**Version 1.0.0**

Disciplined repo-wide cleanup for technical debt and maintainability work. Uses 8 specialized subagents to cover unused code, legacy paths, circular dependencies, shared types, weak types, duplication, error handling, and comment noise.

Designed for multi-agent coding harnesses (Claude Code, OpenCode, Factory Droid, Copilot CLI) with subagent support. Language-agnostic — works with TypeScript, Go, Python, Rust, Java, Ruby, C#, and others.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Agent instructions. This is what the model reads and follows during cleanup. | Yes |
| `testing-scenarios.md` | Pressure tests for validating the skill itself. Edge-case scenarios + known loopholes. | No |
| `README.md` | Documentation for humans. You're reading it. | No |

Only `SKILL.md` gets loaded into the agent's context when the skill triggers. The other files ship alongside it for development and documentation but have zero runtime cost.

## Use It For

- Repo-wide or monorepo cleanup passes
- Broad multi-package or multi-area cleanup sweeps
- Technical debt, code hygiene, or maintainability sweeps before release
- Repo-wide cleanup audits before editing
- Broad multi-area cleanup inside one large app, package, or service
- Explicit `/code-cleanup`, `/code-cleanup review`, `/code-cleanup risky`, or `/code-cleanup dry-run` invocation

## Do Not Use It For

- Single bugfixes or feature work
- Pure formatting
- Code search, explanation, or review-only requests
- Narrow single-file or single-helper fixes

## How It Works

1. **Preflight**: Inspects the repo — language mix, package structure, validation commands, dirty files, baseline snapshot ID, files-in-scope count, cross-language boundary files. Applies the repo-size guardrail (stop at >20K files unless scoped).
2. **Self-Check**: Orchestrator answers 5 anti-drift questions in its own words before spawning research. Catches dropped rules before they become bad writes.
3. **Research (read-only)**: All 8 subagents run in parallel (or serialized if the harness can't run 8 at once), each with the full Shared Context injected by the orchestrator. Every subagent returns a strict-schema Markdown report.
4. **Phase 0 (dry-run only)**: If invoked with `dry-run`, reports proposed SAFE/REVIEW/RISKY queues and exits without writing.
5. **Phase 1 (auto-apply)**: Only `SAFE` items get applied — local, mechanical, evidence-backed changes with no behavior change. Validated after each write pass. One commit at end of phase.
6. **Phase 2 (tier-gated)**: `REVIEW` items are surfaced, frozen, and applied only when the run is authorized through that tier. Separate review subagent verifies. One commit at end of phase.
7. **Phase 3 (tier-gated)**: `RISKY` items are surfaced, frozen, and applied only when the run is authorized through that tier. Separate review subagent verifies. One commit at end of phase.

## Invocation Modes

Use these canonical forms when the harness supports slash-style invocation:

- `/code-cleanup` — runs only `SAFE` work, then reports deferred queues
- `/code-cleanup review` — runs `SAFE`, then may continue into `REVIEW` once that queue is surfaced and frozen
- `/code-cleanup risky` — runs `SAFE`, then may continue through `REVIEW` and `RISKY` once each queue is surfaced and frozen
- `/code-cleanup dry-run` — reports proposed queues across all three tiers without writing, committing, or creating reversible units

Important behavior:

- The suffix sets the maximum tier for the run.
- `review` and `risky` count as structured upfront authorization — one-shot, no extra approval round-trip.
- Queue surfacing still happens before risky phases; the suffix removes the extra approval round-trip, not the safety checks.
- Vague phrasing such as `do the risky cleanup too` does not count as structured upfront authorization.
- `dry-run` never creates commits, reversible units, or file writes. A subsequent write run re-runs research from scratch.

## Safety Guarantees

- **24-rule non-negotiable contract** covering write ownership, validation, commit hygiene, queue freezing, cross-language boundaries, schema conformance, and context injection.
- **Strict Subagent Output Schema** — every subagent returns a Markdown document matching a validated template. Non-conforming output blocks queue integration. Schema scaffolding catches silent drops in weaker models.
- **Self-check step** — orchestrator answers 5 anti-drift questions before spawning research. Cheap insurance against rule erosion on long runs.
- **Never overwrites unrelated local changes** — exact `git diff` commands spelled out in SKILL.md prove hunk-level isolation before any write to a mixed file.
- **Validation after every write pass** — not just at the end.
- **Phase 1 mechanical checklist review; Phase 2/3 independent review subagent** — mechanical checks can be self-verified; judgment calls need fresh eyes to avoid confirmation bias.
- **Reversible units for every write pass** — `/tmp/pass-N.patch` captured before handoff so rollback targets only the offending pass.
- **One commit per phase** with subject format `chore: code cleanup phase <N> (<tier>)`; never commits mid-phase.
- **Commit hook protocol** — post-hook diff must match frozen queue; otherwise reset. Max 2 iterations, no `--no-verify` bypass.
- **Snapshot invalidation** forces re-research when earlier passes change claimed files.
- **Cross-language boundary files** (generated code, FFI, IDL stubs) are default-excluded; opt-in downgrades to `REVIEW`.
- **Polyglot validation**: each pass scoped to one language's matrix; baseline failure in one language doesn't block cleanup in another.
- **Repo-size guardrail**: warns at 5K files, stops and requires scoping at 20K.

## Cleanup Areas (Safe Integration Order)

1. **Unused Code Removal** — using `knip`, `deadcode`, `vulture`, or language equivalents
2. **Legacy / Deprecated / Fallback Cleanup** — remove dead paths with clear reachability
3. **Circular Dependency Cleanup** — using `madge`, `goda`, or language equivalents
4. **Shared Type Consolidation** — merge semantically identical types across the codebase
5. **Weak Type Strengthening** — replace `any`, `unknown`, `interface{}`, `Any`, `Object`, `dynamic` with proven types
6. **DRY / Deduplication** — merge repeated logic only when it reduces complexity
7. **Error Handling Audit** — classify and clean `try/catch`, `if err != nil`, `Result`/`unwrap`, `rescue`, etc.
8. **Noise / Obsolete Comment Cleanup** — remove AI slop, stubs, dead comments; preserve intent comments

Each step's output feeds the next. Do not reorder.

## Skill Testing

Use [`testing-scenarios.md`](./testing-scenarios.md) to pressure-test the skill with RED/GREEN/REFACTOR scenarios. It covers dirty worktrees, flaky validation, scope creep, stale findings, tiered invocation, dry-run isolation, self-check drift, polyglot matrices, cross-language boundaries, per-phase commit discipline, schema conformance, commit hook loops, repo-size scoping, and parallelism degradation, plus a common-loophole checklist to watch for. Run these after modifying `SKILL.md` to validate your changes.

## Model Compatibility

Designed for frontier instruction-following models (Claude Opus/Sonnet 4.6+, GPT-5.4+) and open-weight models (Kimi K2.5, GLM-5.1).

Two features specifically scaffold weaker models:

- The **Self-Check** forces the orchestrator to restate critical rules in its own words before any writes. Drift surfaces here, cheaply.
- The **Subagent Output Schema** gives weak models an unambiguous template to fill. Schema validation catches silent format drops that would otherwise contaminate the queue.

On weaker models, running two independent review subagents for Phase 2/3 final review (instead of one) further reduces false-accept rates. Each subagent invocation carries ~20K tokens of overhead, so budget accordingly on paid inference.

## Harness Notes

The skill ships identical SKILL.md content across Claude Code, OpenCode, Factory Droid, and Copilot CLI. Only the slash-command wiring differs per harness. Subagent context windows start fresh with nothing inherited from the orchestrator — Rule 24 makes this explicit and requires the orchestrator to inject the full Shared Context block into every subagent spawning prompt.
