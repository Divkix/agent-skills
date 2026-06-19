## Subagent Report Shape

Applies **only on the parallel-subagent path**. Each research subagent returns one Markdown report in this shape so the orchestrator can integrate findings uniformly. On the inline/serial path the orchestrator does the research itself and records findings directly — there is no separate worker, so there is nothing to validate against this shape; do not perform it as ceremony.

```text
# SUBAGENT_REPORT

## status
<one of: SAFE_FINDINGS | REVIEW_FINDINGS | RISKY_FINDINGS | NO_CHANGES | BLOCKED>

## subagent
<exact cleanup area name, or the merged cluster name>

## findings
<one block per finding, or the literal word "none" if status is NO_CHANGES or BLOCKED>

### finding_1
- tier: <SAFE | REVIEW | RISKY>
- files: <absolute paths, one per line, indented>
- evidence: <concrete: symbol name, line numbers, tool output excerpt>
- proposed_change: <single sentence describing the edit>
- validation_impact: <which matrix commands this affects, or "none">
- blockers: <dynamic references, dirty overlap, boundary files, or "none">

### finding_2
<same structure>

## reason
<required only if status is NO_CHANGES or BLOCKED; one paragraph>
```

What the orchestrator checks before integrating a subagent's findings:

- `status` and `subagent` are present.
- For a `*_FINDINGS` status, at least one finding is present and every finding has all six fields.
- For `NO_CHANGES` or `BLOCKED`, `findings` is `none` and `reason` is present.
- Every `files` entry is an absolute path that exists in the current tree.
- Evidence is concrete, not boilerplate. `"code is unused"` is boilerplate; `"src/utils/format.ts:12 formatCurrency exported but knip reports 0 imports"` is evidence.
- A subagent that fails to launch, times out, or returns a malformed or evidence-free report is unusable: drop its output and re-run that area before integrating. Never integrate a partial research set as if it were complete.
