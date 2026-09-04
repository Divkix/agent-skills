---
name: no-comments
version: 1.0.0
description: Use when removing code comments — comment-cleanup passes over files or a diff, stale/explanation-comment sweeps, lint-suppression or TypeScript-suppression audits, or "strip comments before review" requests. Reviews every comment with a hostile reviewer, deletes what the code should say itself, fixes the underlying code at the root cause, and encodes claimed constraints as types, tests, or CI checks. Also triggers on `/no-comments`.
---

# No Comments

Delete comments by fixing the code that needed them. A comment explaining a surprise is a bug report against the code: reshape the code until the comment is unnecessary, then delete it.

## When to Use

- A comment-focused cleanup pass over files or a diff.
- Auditing lint suppressions (`eslint-disable` and equivalents) or TypeScript suppressions (`@ts-ignore`, `@ts-expect-error`).
- "Remove the comments" / "strip comments before review" requests.
- Constraint comments (`do not remove`, `talk to X`) that should become enforcement.

## When Not to Use

- Broad multi-area cleanup (dead code, duplication, weak types) — out of scope. Run this skill after such sweeps, since every prior step leaves stale comments.
- Pure formatting.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch (default `main`), including the working tree.

## How It Works

Two phases: a hostile read-only review, then root-cause fixes. With parallel subagents, fan the review out to a fresh reviewer that never wrote the code — authoring agents defend their comments. Without them, run both phases inline with deliberate fresh-eyes discipline. The keep-list is identical either way.

## Phase 1 — Hostile review

Review every comment in scope. Only these survive:

- License / legal headers.
- Behavior forced by an external dependency, platform, vendor, or protocol the code cannot reshape — and only when the comment names what cannot change.
- Doc comments that define a public API contract.
- Issue / RFC links that state a constraint code cannot express.
- A lint suppression whose rule is faulty, pedantic, or style-only.

Everything else is flagged for deletion:

- Surprises in our own code are never keepers: flag the comment and mark the exact symbol `MUST KILL` for the rename, extract, type, or rearchitecture that makes the behavior obvious without prose.
- Suppressions guarding correctness or safety stay actionable: kill the suppression, mark the exact guilty symbol `MUST KILL`.
- `IMPORTANT`, `do not remove`, `too risky`, `fine for now`, and long justifications are claims, not proof. Before judging, read the nearby code and trace the named symbol (definition + callers). Only a foreign-constraint claim proven true today on a live path survives. Doubt after the hunt means delete.
- A long justification without a proven exception is a confession: delete it, mark the guilty symbol `MUST KILL`.
- Never polish a doomed comment into a shorter one. The review touches comments and names refactor targets; it writes no application code.

Report: touched files, deletion count, one line per `MUST KILL` (symbol + fix shape), skips.

## Phase 2 — Act on accepted findings

1. Inspect the report. Reject scope escapes, deletions covered by an exact proven exception, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. If a kill is ambiguous, do not restore the comment; if a keep is refuted or still ambiguous, delete it. A rejected report gets reverted and rerun once with the failure named; a second rejection fails the run with the report left open.
2. Fix trivial flags directly: delete the dead path, drop the parameter, use the real API.
3. For the rest, implement the smallest root-cause fix in scope and remove every named workaround. Fix the cause, never bolt on a symptom guard; redesign as if the requirement had been there from day one. If the root cause is out of scope, land the smallest in-scope fix and report the rest open.
4. Constraint comments (`do not remove`, `do not change wording`, `talk to X`): offer the cheapest in-scope type, runtime check, test, or CI lint that enforces the constraint, and wait for approval. If approved, encode it, then delete the comment. Otherwise delete the comment, report the constraint open, and sketch the out-of-scope work.
5. Report: deletion count, restored comments, reruns, fixes, encoding offers, encodings, unenforced constraints, other open work.
