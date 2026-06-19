## Write Ownership and Hunk Isolation

- Every finding in one queue comes from one research pass on one tree state. If the tree changes before the queue freezes, re-research the affected areas.
- If the user scoped cleanup to a subset (e.g., specific packages), keep the sweep inside that slice; do not silently widen to the whole repo.
- Before editing, the active writer re-checks every claimed file and directly affected module boundary against the current tree (`git diff HEAD -- <file>`).
- If another pass changed a claimed file or any upstream/downstream dependency a reasonable reviewer could tie to the finding, re-research before editing.
- If two areas need the same file, serialize them and hand off only after validation.
- A file with unrelated local edits is no longer automatically `SAFE`.

Key definitions:

- **Usable finding**: concrete evidence plus an actionable, tier-tagged recommendation, or an explicit `NO_CHANGES` with a reason. Boilerplate without evidence is unusable.
- **Checkpoint (reversible unit)**: a saved patch (`git diff > /tmp/pass-N.patch`) taken after each write pass so the pass can be undone mechanically. A mental undo plan is not enough. These checkpoints are scratch — the phase still produces exactly one retained commit. Because passes stack, undoing pass N means restoring the checkpoint taken before it.
- **Frozen queue item**: a recommendation carrying all of: cleanup area, exact files or modules, evidence, intended edit scope, confidence tier, and validation impact. `Clean up module X` is not a valid item.
- **Cross-language boundary file**: any file generated from or binding to another language's type system — OpenAPI/Swagger types, gRPC/Protobuf stubs, FFI bindings, IDL-generated code.

**Default for a file with unrelated edits: exclude it from this cleanup pass.** That is almost always the right call. Only if removing that file's cleanup item would clearly lose value should you prove hunk-level isolation first — with commands, not eyeballing:

```sh
# 1. Capture the baseline diff BEFORE any cleanup edit.
git diff HEAD -- <file> > /tmp/baseline.diff

# 2. Apply the cleanup edit, then re-diff.
git diff HEAD -- <file> > /tmp/current.diff

# 3. /tmp/current.diff MUST contain every hunk from /tmp/baseline.diff
#    unchanged, plus only new cleanup hunks. If any baseline hunk is
#    missing or altered, the cleanup edit absorbed unrelated work —
#    revert via the checkpoint and exclude the file.
```

Committing only the cleanup hunks from a mixed file requires hunk-level staging (`git add -p`), which is error-prone for an automated agent and unavailable in some harnesses. **Prefer excluding the file.** If you must split hunks, after staging verify that `git diff --cached -- <file>` shows only cleanup changes and `git diff -- <file>` still equals `/tmp/baseline.diff` exactly.
