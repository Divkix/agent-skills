# No Comments Skill

**Version 1.0.0**

Adapted from [`cursor/plugins`](https://github.com/cursor/plugins) (`pstack` → `no-comments` skill + Comment Sicko reviewer), rewritten as a self-contained skill: the reviewer rules, root-cause fix intent, and constraint-encoding flow are inlined in `SKILL.md` instead of depending on Cursor subagent types (`Comment Sicko`), slash commands (`/how`, `/why`, `/architect`), or plugin-local principle skills.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Main agent instructions. Scope, hostile-review keep-list, `MUST KILL` flag rules, root-cause fix flow, constraint-encoding flow, and output contract. | Yes |
| `README.md` | Documentation for humans. You're reading it. | No |

## Use It For

- Comment-cleanup passes over files or a diff ("remove the comments", "strip comments before review")
- Stale / explanatory-comment sweeps after a refactor
- Lint-suppression audits (`eslint-disable` and equivalents)
- TypeScript-suppression audits (`@ts-ignore`, `@ts-expect-error`)
- Turning constraint comments (`do not remove`, `talk to X`) into real enforcement

## Do Not Use It For

- Broad multi-area cleanup (dead code, duplication, weak types) — out of scope; run this skill after such sweeps
- Pure formatting
- Writing documentation — this skill deletes prose, it never adds it

## Requirements

- A git repository (default scope is the diff against `main`, working tree included)
- No other dependencies; runs inline or fans the review out to subagents where the harness supports them

## How It Works

1. **Hostile review** — Every comment in scope is guilty until it matches a five-item keep-list (license headers, unchangeable foreign constraints, public-API doc contracts, constraint links, faulty/pedantic/style-only suppressions). Our-code surprises become `MUST KILL` refactor flags, not keepers. Thin authority claims (`IMPORTANT`, `do not remove`) must be proven against the live code; doubt means delete.
2. **Act on accepted findings** — Trivial flags are fixed directly; the rest get the smallest root-cause fix in scope, never a symptom guard. Claimed constraints are offered back as the cheapest enforcing type, check, test, or CI lint; encoded on approval, otherwise reported open.
3. **Final report** — Deletion count, restored comments, reruns, fixes, encoding offers, encodings, unenforced constraints, other open work.

## Safety Guarantees

- **Scope-fenced** — only the caller's files/diff or the base-branch diff; root-cause fixes outside the fence are reported open, never widened into.
- **No symptom guards** — fixes land at the cause or stay reported; workarounds are removed, not added.
- **Constraints need approval** — nothing is encoded as a type, test, or CI check without an explicit yes.
