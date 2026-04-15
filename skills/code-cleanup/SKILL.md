---
name: codebase-cleanup
description: >
  Deep codebase cleanup using 8 focused subagents: deduplication (DRY), shared type consolidation,
  unused code removal (knip), circular dependency resolution (madge), type strengthening (no any/unknown),
  error handling audit, legacy/deprecated code removal, and AI slop/comment cleanup.
  Use this skill whenever the user wants to clean up, refactor, improve code quality, remove dead code,
  fix types, remove any/unknown, untangle dependencies, or do a codebase audit. Also triggers on phrases
  like "clean up my codebase", "code quality", "remove unused code", "fix types", "refactor everything",
  "codebase health", or "remove AI slop". Produces a structured multi-agent cleanup plan with guardrails,
  sequencing, validation steps, and safe apply patterns.
---

# Codebase Cleanup Skill

You are orchestrating a safe, thorough codebase cleanup using 8 specialized subagents. Your job is to:
1. Gather context from the user (see **Pre-flight Checklist** below)
2. Generate a complete, ready-to-run prompt for each agent
3. Enforce safe sequencing and validation steps throughout

---

## Pre-flight Checklist

Before writing any agent prompts, ask the user (or infer from context) the following. Do not proceed without answers to items marked **required**.

| # | Question | Required? |
|---|---|---|
| 1 | What language(s) and framework(s) are in this codebase? | Yes |
| 2 | Monorepo or single package? Package manager? (npm/pnpm/bun/cargo/etc) | Yes |
| 3 | What are the entry points? (e.g., `src/index.ts`, `apps/web`, `cmd/main.go`) | Yes |
| 4 | What should agents **never touch**? (e.g., `generated/`, `vendor/`, `*.test.ts`, `migrations/`) | Yes |
| 5 | Apply changes automatically, or output recommendations only for human review? | Yes |
| 6 | Is there a CI/lint/type-check command to validate after changes? (e.g., `pnpm typecheck`, `tsc --noEmit`) | Recommended |
| 7 | Any files/modules that are known to be legacy-but-intentional? | Optional |
| 8 | Approximate codebase size? (helps calibrate agent scope) | Optional |

---

## Agent Execution Order

Run agents in this sequence — **do not parallelize unless the user explicitly accepts merge conflict risk**:

```
[2] Types → [3] Unused Removal → [4] Circular Deps → [1] DRY → [5] Strengthen Types → [7] Legacy Cleanup → [6] Error Handling → [8] Comments
```

**Why this order:**
- Types first — everything else depends on a stable type surface
- Remove unused before deduplicating — don't consolidate dead code
- Circular deps before DRY — restructuring deps changes the dependency graph
- Strengthen types after DRY — fewer files to retype
- Legacy cleanup before error handling — less code = less error handling to audit
- Comments last — earlier passes change the code those comments describe

---

## Shared Context Block (inject into every agent prompt)

```
CODEBASE CONTEXT:
- Language/Framework: {language_framework}
- Package manager: {pkg_manager}
- Entry points: {entry_points}
- Do NOT touch: {exclusion_list}
- Validation command: {validation_command}
- Mode: {RECOMMEND_ONLY | APPLY_HIGH_CONFIDENCE}

DEFINITION OF HIGH CONFIDENCE (auto-apply only if ALL true):
1. Change is isolated to one file OR affects only internal (non-exported) symbols
2. Does not alter any public interface, exported type, or API contract
3. Validation command passes after the change
4. No ambiguity about intent — the change is mechanical, not judgment-based
```

---

## Agent Prompts

### Agent 1 — DRY / Deduplication

```
[SHARED CONTEXT BLOCK]

TASK: Deduplicate and consolidate code to reduce complexity.

RESEARCH PHASE:
- Scan for copy-pasted logic blocks (>5 lines, >80% identical)
- Find utility functions re-implemented in multiple files
- Find inline logic that should be extracted into a shared helper
- Identify repeated constants, config values, or magic numbers

ASSESSMENT: Write a critical assessment of duplication in the codebase:
- List each duplication with file paths and line numbers
- Estimate complexity impact (does consolidating this REDUCE or ADD complexity?)
- Flag cases where "duplication" is actually intentional isolation (e.g., separate domain logic that happens to look similar)

IMPORTANT: Do not consolidate things just because they look similar. Only consolidate
when a shared abstraction makes the code clearer, not just shorter. If merging two
functions requires adding a parameter or conditional to handle differences, reconsider.

APPLY: For each high-confidence recommendation, apply the change and run: {validation_command}
Do not proceed past validation errors.
```

---

### Agent 2 — Type Consolidation

```
[SHARED CONTEXT BLOCK]

TASK: Find all type/interface definitions and consolidate shared ones.

RESEARCH PHASE:
- Find all type, interface, struct, class definitions across the codebase
- Identify types that are semantically identical or near-identical but defined in multiple places
- Find types that are subsets or supersets of each other and could be composed
- Check if shared types should live in a shared package/module

ASSESSMENT:
- List all type duplication with file paths
- Note which duplicates are safe to merge (identical shape, same semantics)
- Note which are "accidentally identical" (different domains that happen to share shape — do NOT merge these)

APPLY: Consolidate true duplicates. Update all imports. Run: {validation_command}
```

---

### Agent 3 — Unused Code Removal

```
[SHARED CONTEXT BLOCK]

TASK: Find and remove all unused code.

TOOLS TO USE:
- TypeScript/JS: Run `knip` — install if not present: npx knip
- Go: `go vet`, `staticcheck`, `deadcode` tool
- Python: `vulture`
- Other: use the appropriate dead-code tool for the language

RESEARCH PHASE:
- Run the relevant tool(s) and collect all reported unused exports, files, dependencies
- For each reported item: manually verify it is not referenced via dynamic import, string-based lookup, reflection, or runtime plugin system
- Check package.json/go.mod for unused dependencies separately

DO NOT REMOVE:
- Anything in {exclusion_list}
- Type-only exports that may be used by downstream consumers of a library
- Anything with a comment explaining why it exists (flag for human review instead)

ASSESSMENT: List every unused item with confidence level (high/medium/low).

APPLY: Remove high-confidence unused items. Run: {validation_command} after each batch.
```

---

### Agent 4 — Circular Dependencies

```
[SHARED CONTEXT BLOCK]

TASK: Detect and resolve circular dependencies.

TOOLS TO USE:
- JS/TS: Run `madge --circular` — install if needed: npx madge
- Go: `go list -json ./... | jq` + manual analysis, or `goda`
- Other: use the appropriate dep-graph tool

RESEARCH PHASE:
- Generate the full dependency graph
- List all circular dependency chains with file paths
- For each cycle: identify the "wrong direction" import (the one that shouldn't be there)
- Common patterns: A imports B for a type that should live in a shared C module; feature modules importing from each other instead of a shared core

ASSESSMENT:
- List each cycle
- Recommend: extract shared module, invert dependency, or use dependency injection
- Note cycles that exist in test files only (lower priority, flag separately)

APPLY: Resolve cycles by extracting shared modules or inverting dependencies.
Run: {validation_command} after each resolution.
```

---

### Agent 5 — Type Strengthening (no `any` / `unknown`)

```
[SHARED CONTEXT BLOCK]

TASK: Remove weak types (any, unknown, object, {}, @ts-ignore, @ts-expect-error) and replace with strong types.

RESEARCH PHASE:
- Find all occurrences of: any, unknown, object, {}, Record<string, any>, as any, @ts-ignore, @ts-expect-error
- For each occurrence:
  1. Look at what values are actually assigned to/from this type in the codebase
  2. Check the source package's type definitions (.d.ts, JSDoc, source) for the real type
  3. Check if a more specific type is already defined elsewhere in the codebase

DO NOT:
- Replace `unknown` used in genuine input-validation / boundary code (API responses, user input, JSON.parse) — this is correct usage
- Replace `any` with a made-up type. If you can't find the real type, leave it and flag it.
- Make assumptions. Research before replacing.

ASSESSMENT: For each weak type, document the proposed replacement and your evidence.

APPLY: Replace only where you have found the concrete type from source. After EVERY single
replacement, run: {validation_command}. Stop and report if any type errors appear.
```

---

### Agent 6 — Error Handling Audit

```
[SHARED CONTEXT BLOCK]

TASK: Audit try/catch blocks and equivalent defensive programming patterns.

RESEARCH PHASE:
- Find all try/catch, .catch(), Result/Option handling, panic recovery, etc.
- Categorize each into:
  A. KEEP: Handles genuinely unknown/unsanitized input (network, user input, JSON parse, file I/O, third-party APIs)
  B. KEEP: Has specific recovery logic (retry, fallback with clear intent, re-throw with context)
  C. REVIEW: Catch block is empty, logs and swallows, or does nothing useful
  D. REVIEW: Re-throws identically (pointless wrapper)
  E. REMOVE: Wraps purely internal logic with no possibility of runtime failure

IMPORTANT RULE: Do not auto-remove anything in category C or D without a human decision.
Flag C and D as "needs review" in your assessment.

ONLY auto-remove category E (clearly pointless wrapping of deterministic internal logic).

ASSESSMENT: List every error handling block, its category, and your reasoning.

APPLY: Remove only category E. Output a separate list of C and D for human review.
Run: {validation_command}
```

---

### Agent 7 — Legacy / Deprecated / Dead Code Paths

```
[SHARED CONTEXT BLOCK]

TASK: Find and remove deprecated, legacy, and fallback code.

RESEARCH PHASE:
- Search for: TODO, FIXME, HACK, DEPRECATED, @deprecated, legacy_, old_, _v1, _v2, _old, _new
- Find feature flags that are always-on or always-off (hardcoded boolean feature gates)
- Find commented-out code blocks
- Find code paths that are unreachable (after if(false), after always-true conditions)
- Find version-shim code for library versions no longer in use (check package.json)

ASSESSMENT:
- List every legacy item with file path
- Distinguish: safely removable vs. needs investigation
- For feature flags: confirm the flag value before recommending removal

APPLY: Remove clearly safe items. Run: {validation_command}
Flag anything ambiguous for human review.
```

---

### Agent 8 — AI Slop / Comment Cleanup

```
[SHARED CONTEXT BLOCK]

TASK: Remove AI-generated noise, unhelpful comments, and dead documentation.

WHAT TO REMOVE:
- Comments that describe what the code does when the code already makes it obvious
- Comments describing in-progress work ("TODO: replace this with X", "temporary", "will be updated")
- Section dividers with no meaning (// ==================)
- Comments that describe removed or replaced code ("previously this used Y, now uses X")
- Stub implementations with placeholder logic that was never filled in
- Console.log/print debugging statements left in production code
- Commented-out import blocks

WHAT TO KEEP OR IMPROVE:
- Comments explaining WHY a non-obvious decision was made
- Comments pointing to external context (spec links, issue numbers, workaround explanations)
- Public API documentation (JSDoc, godoc, etc.) — improve these if they're vague, don't delete

WHAT TO REWRITE (be concise):
- Any comment that would confuse a new developer trying to understand the codebase
- Rewrite in plain language: what is this, why does it exist, any gotchas

APPLY: Remove noise. Rewrite only where clarity genuinely improves.
Run: {validation_command}
```

---

## Final Validation Pass

After all 8 agents complete, run a final check:

```bash
# Re-run the full dependency graph — should be cycle-free
npx madge --circular .

# Re-run unused code check — should be significantly cleaner
npx knip

# Full type check
{validation_command}

# Optionally: run your test suite
```

Report a summary of:
- Files changed per agent
- Lines removed vs. added
- Any items flagged for human review across all agents
- Remaining issues that require manual decisions

---

## Notes / Edge Cases

- **Generated files**: Always exclude from all agents. Things like `*.generated.ts`, `prisma/client`, `graphql/types`, proto outputs.
- **Test files**: Run cleanup on them separately and more conservatively. Don't remove "unused" test helpers without checking if they're used in test suites not yet indexed.
- **Monorepos**: Each agent should be scoped to one package at a time unless it's explicitly doing cross-package work (type consolidation, circular deps).
- **`unknown` at boundaries**: This is correct TypeScript. Do NOT remove `unknown` on API response types, JSON.parse results, or any data coming from outside the process boundary.
- **Apply mode vs. recommend mode**: If the user chose RECOMMEND_ONLY, all agents output markdown summaries with file paths and diffs, but make no changes. A separate apply pass is done after human review.
