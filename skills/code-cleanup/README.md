# Code Cleanup Skill

Deep codebase cleanup using 8 specialized subagents with tiered execution.

## What It Does

This skill orchestrates a full-repo cleanup with 8 dedicated subagents:

1. **DRY / Deduplication** — Consolidate repeated logic where it reduces complexity
2. **Type Consolidation** — Merge duplicate/shared type definitions
3. **Unused Code Removal** — Remove dead code using `knip` (or language equivalents)
4. **Circular Dependency Resolution** — Break import cycles using `madge` (or equivalent)
5. **Type Strengthening** — Replace weak types (`any`/`unknown` equivalents) with concrete types
6. **Error Handling Audit** — Remove unnecessary defensive wrappers and error-hiding patterns
7. **Legacy Cleanup** — Remove deprecated, fallback, and obsolete paths
8. **Slop / Comment Cleanup** — Remove AI slop, dead stubs, and unhelpful comments

## Usage

Use either command-style invocation or natural language:

```
> /code-cleanup
> clean up my codebase
> refactor everything and remove unused code
> fix types and remove dead code
```

## Default Behavior

- Performs an auto-inferred preflight by inspecting the repo first.
- Uses a **full-repo sweep** by default (with explicit exclusions).
- Spawns **all 8 subagents** automatically.
- Allows subagents to research in parallel, but applies file changes **one at a time** in a safe integration order.
- Requires each subagent to provide:
  - detailed research,
  - critical assessment,
  - high-confidence recommendations,
  - applied high-confidence changes during its write turn.

## Apply Tiers

- **High-confidence (default auto-apply)**: Mechanical and low-risk changes only.
- **Recommended (opt-in)**: Medium-risk items held for explicit approval.
- **Aggressive (opt-in)**: High-risk restructures held for explicit approval.

After high-confidence completion, the skill reports recommended and aggressive queues and can execute either queue if explicitly requested.

## Safe Integration Order

The write phase runs in this order to avoid consolidating dead or unstable code too early:

`Types -> Unused -> Circular -> DRY -> Strengthen -> Legacy -> Errors -> Comments`

## Validation and Review

- Runs repo validation after each sequential integration pass (type/lint/test/build as available).
- Re-runs dead-code and cycle checks where applicable.
- Runs a mandatory final review pass after each phase.
- Stops on validation failure and reports what needs manual decisions.

## Tooling

- **TypeScript/JS**: `knip`, `madge --circular`, `tsc`/project checks
- **Go**: `go vet`, `staticcheck`, `deadcode`, `goda`
- **Python**: `vulture` and project test/lint checks
