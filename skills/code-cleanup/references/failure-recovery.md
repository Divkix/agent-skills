## Failure Recovery

- **Missing tool**: report it, lower confidence, and avoid speculative cleanup that depended on it.
- **Dirty overlapping file**: stop or downgrade unless ownership is clear.
- **Stale research** (including indirect invalidation through upstream/downstream module changes): re-research before writing.
- **Validation regression**: fix within the current pass or revert or defer that pass.
- **Rollback**: must target only the active pass by using its reversible unit. Do not guess at manual partial reverts on a dirty tree.
- **Snapshot or golden-file update required to make validation green**: downgrade to `REVIEW` unless the user explicitly requested that refresh.
- **Uncertain dynamic reference**: downgrade to `REVIEW` or leave untouched.
- **True conflict with concurrent human edits**: stop and ask.
- **Pre-existing staged hunks in a claimed file**: do not absorb them silently. Either preserve them outside the cleanup commit or stop. Exclude the file or prove hunk-level isolation before writing.
- **Cross-language boundary file in the proposed diff**: exclude the file or downgrade the entire item to `REVIEW`.
- **Subagent failed to launch, timed out, or returned non-conforming output**: stop the phase. Never integrate a partial research set.
- **Repo size exceeds 20,000 files in scope**: stop and require explicit scoping from the user before proceeding.

### Commit Hook Handling

Pre-commit hooks (formatters, linters, auto-fix tools) may mutate tracked files after the cleanup commit is staged. This creates a divergence between the reviewed diff and the committed artifact.

Protocol:

1. After the cleanup commit lands, compute the post-hook diff: `git diff HEAD~1 HEAD`.
2. Compare against the frozen queue. Every file in the post-hook diff must be in the frozen queue.
3. If any file in the post-hook diff is outside the frozen queue, revert the commit (`git reset --hard HEAD~1`) and stop. Do not amend — hook-introduced changes outside the frozen queue are a signal that the hook is doing cleanup the skill did not approve.
4. If all files match the frozen queue, accept the commit.
5. Maximum 2 iterations of "commit → hook mutates → re-review". If the hook keeps mutating files after 2 iterations, stop and report — something is looping.
6. Never use `git commit --no-verify` to sidestep hooks. That disables the team's quality gates.
