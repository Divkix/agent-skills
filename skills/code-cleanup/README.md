# Code Cleanup Skill

Disciplined repo-wide cleanup for technical debt and maintainability work.

## Use It For

- repo-wide or monorepo cleanup passes
- broad multi-package cleanup sweeps inside a monorepo
- dead code, duplication, circular dependencies, weak types, legacy paths, and stale comments
- code hygiene or maintainability sweeps before release
- repo-wide cleanup audits before editing
- explicit `/code-cleanup` invocation

## Do Not Use It For

- single bugfixes
- feature work
- pure formatting
- code search, explanation, or review-only requests

## Default Behavior

- runs 8 cleanup areas with an initial read-only research pass
- auto-applies only `HIGH_CONFIDENCE` changes in Phase 1
- keeps `RECOMMENDED` and `AGGRESSIVE` work opt-in after Phase 1 reports the queue
- uses one active writer at a time in a fixed integration order
- re-researches stale findings before later write passes touch changed files or affected modules
- records baseline validation and blocks on regressions

## Cleanup Areas

1. DRY / deduplication
2. Shared type consolidation
3. Unused code removal
4. Circular dependency cleanup
5. Weak type strengthening
6. Error handling audit
7. Legacy / deprecated / fallback cleanup
8. Noise / obsolete comment cleanup

## Safety Rules

- excludes generated and vendor paths by default
- does not overwrite unrelated local changes
- does not treat `commit everything` as permission to stage unrelated files
- requires final review before completion

## Skill Testing

Use [`testing-scenarios.md`](./testing-scenarios.md) to pressure-test the skill with RED/GREEN/REFACTOR scenarios. That file validates the skill and is not required for normal runtime use.
