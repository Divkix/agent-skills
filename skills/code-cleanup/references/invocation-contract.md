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
