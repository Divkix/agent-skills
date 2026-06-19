## Shared Context for Research Subagents

Used **only on the parallel-subagent path**. Subagent context windows start empty — nothing is inherited from the orchestrator — so when you spawn research agents, inject this entire block into every spawning prompt, on every invocation. On the inline/serial path there are no subagents and nothing to inject; the orchestrator already holds this context.

```text
CODEBASE CONTEXT:
- Scope: {cleanup_scope}
- Language/Framework: {language_framework}
- Package manager/workspace: {pkg_manager_or_workspace}
- Entry points: {entry_points}
- Do NOT touch: {exclusion_list}
- Cross-language boundary files: {boundary_files}
- Dirty files before cleanup: {dirty_files}
- Files in scope: {files_in_scope_count}
- Validation commands: {validation_commands}
- Baseline validation failures: {baseline_failures}
- Current apply tier: {SAFE | REVIEW | RISKY}
- Write mode: {RESEARCH_ONLY | ACTIVE_WRITE_TURN | DRY_RUN}
- Active write owner: {cleanup_area_name | none}

REQUIRED OUTPUT:
Return a single Markdown document matching the report shape in references/subagent-schema.md.
```
