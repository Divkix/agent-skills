## Write Ownership and Snapshot Invalidation

- All research findings are tied to the repo snapshot seen during that research pass. All findings integrated into one queue must reference the same snapshot identifier. If the repo state changes before queue freeze, re-run affected research.
- If the user scoped cleanup to a broad subset such as multiple packages, keep the sweep inside that slice instead of silently widening to the whole repo.
- Before editing, the active writer must re-check every claimed file and directly affected module boundary against the current tree.
- If another pass changed a claimed file or any upstream/downstream dependency a reasonable reviewer could see as affecting the finding, re-research before editing.
- If two areas need the same file, serialize them and hand off only after validation.
- If a file contains unrelated local edits, cleanup is no longer automatically SAFE.

Key definitions:

- **Baseline snapshot ID**: the sha256 computed in Preflight. Two findings that reference different IDs cannot be integrated into the same queue.
- **Usable findings**: output that passes the Subagent Output Schema, with concrete evidence and an actionable ranked recommendation, or an explicit `NO_CHANGES` status with a reason. Boilerplate without evidence is unusable.
- **Reversible unit**: a persisted patch (`git diff > /tmp/pass-N.patch`) or temporary commit on a feature branch that can be applied or reverted mechanically. A mental undo plan is not enough.
- **Frozen queue item**: one cleanup recommendation with all of the following: cleanup area, exact files or modules, evidence, intended edit scope, confidence tier, and validation impact. `Clean up module X` is not a valid queue item.
- **Cross-language boundary file**: any file whose content is generated from or binds to a different language's type system. Includes OpenAPI/Swagger generated types, gRPC/Protobuf stubs, FFI bindings, and IDL-generated code.

**Proof of hunk-level isolation** (exact commands, not eyeballing):

```sh
# Step 1 — capture baseline diffs BEFORE any cleanup edit
git diff HEAD -- <file> > /tmp/baseline-unstaged.diff
git diff --cached -- <file> > /tmp/baseline-staged.diff

# Step 2 — apply the cleanup edit

# Step 3 — capture current diff
git diff HEAD -- <file> > /tmp/current.diff

# Step 4 — verify isolation
# /tmp/current.diff MUST contain every hunk from /tmp/baseline-unstaged.diff
# unchanged, plus only new cleanup hunks. If any baseline hunk is missing
# or modified, isolation failed.

# Step 5 — to commit only cleanup hunks
git add -p <file>                  # interactively select only cleanup hunks
git diff --cached -- <file>        # must show only cleanup changes
git diff -- <file>                 # must equal /tmp/baseline-unstaged.diff exactly
```

If step 4 fails, the cleanup edit absorbed unrelated work. Revert via the reversible unit and exclude the file from cleanup.
