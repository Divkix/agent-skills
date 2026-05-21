## Shared Context for Every Subagent

The orchestrator injects this full block into every subagent spawning prompt. Subagent context windows start empty — nothing is inherited from the parent. On every subagent invocation, pass this entire block in the prompt string.

```text
CODEBASE CONTEXT:
- Scope: {cleanup_scope}
- Language/Framework: {language_framework}
- Package manager/workspace: {pkg_manager_or_workspace}
- Entry points: {entry_points}
- Do NOT touch: {exclusion_list}
- Cross-language boundary files: {boundary_files}
- Dirty files before cleanup: {dirty_files}
- Baseline snapshot ID: {snapshot_id}
- Files in scope: {files_in_scope_count}
- Validation commands: {validation_commands}
- Baseline validation failures: {baseline_failures}
- Current apply tier: {SAFE | REVIEW | RISKY}
- Write mode: {RESEARCH_ONLY | ACTIVE_WRITE_TURN | DRY_RUN}
- Active write owner: {cleanup_area_name | none}

REQUIRED OUTPUT:
Return a single Markdown document matching the Subagent Output Schema in SKILL.md.
Non-conforming output blocks queue integration.
```
