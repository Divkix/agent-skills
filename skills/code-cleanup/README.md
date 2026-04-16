# Code Cleanup Skill

Deep codebase cleanup using 8 specialized subagents working in sequence.

## What It Does

This skill orchestrates a comprehensive codebase cleanup:

1. **Type Consolidation** — Merge duplicate type/interface definitions
2. **Unused Code Removal** — Remove dead code using `knip` (or language equivalents)
3. **Circular Dependency Resolution** — Break import cycles using `madge`
4. **DRY / Deduplication** — Consolidate repeated logic blocks
5. **Type Strengthening** — Replace `any`/`unknown` with concrete types
6. **Legacy Cleanup** — Remove deprecated code, feature flags, TODOs
7. **Error Handling Audit** — Review try/catch blocks and defensive patterns
8. **Comment Cleanup** — Remove AI slop and unhelpful comments

## Usage

Trigger the skill by describing cleanup needs:

```
> clean up my codebase
> refactor everything and remove unused code
> fix types and remove dead code
```

## Pre-flight Requirements

The skill will ask you:
- Language/framework
- Entry points
- Files/directories to exclude
- Validation command (e.g., `tsc --noEmit`)
- Apply changes or recommend only?

## Tools Used

- **TypeScript/JS**: `knip`, `madge`, `tsc`
- **Go**: `go vet`, `staticcheck`, `goda`
- **Python**: `vulture`

## Execution Order

Agents run sequentially to avoid conflicts:
```
Types → Unused → Circular → DRY → Strengthen → Legacy → Errors → Comments
```

## Validation

Each agent runs the validation command after changes. The skill stops on any failure.
