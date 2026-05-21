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
