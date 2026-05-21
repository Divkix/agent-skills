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
