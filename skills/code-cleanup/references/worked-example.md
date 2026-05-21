## Worked Example

Compact end-to-end run on a small TypeScript Cloudflare Workers repo.

**Preflight:**

- Language: TypeScript, framework: Hono on Cloudflare Workers, package manager: pnpm
- Validation matrix: `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm build`
- Baseline: all green
- Dirty files: none. Staged hunks: none.
- Baseline snapshot ID: `sha256(HEAD=abc123... + diff=empty + untracked=empty)` = `f9e2...`
- Files in scope: 142 (under 5K threshold)
- Boundary files: `src/types/generated/openapi.d.ts` (flagged, default-excluded)

**Self-check:** orchestrator answers 5 anti-drift questions. No contradictions.

**Research:** orchestrator injects full Shared Context into all 8 subagents in parallel.

Schema-conforming outputs:

- **Unused Code** returns `SAFE_FINDINGS`: `src/utils/format.ts:12` exports `formatCurrency`; knip reports 0 imports. Evidence: knip output excerpt attached. Proposed: remove lines 12-18. Validation impact: none (no callers).
- **Weak Types** returns `REVIEW_FINDINGS`: `src/api/user.ts:23` has `function fetchUser(id: any): Promise<any>`. 3 call sites all pass `string` and destructure `{id, name, email}`. Proposed: change to `(id: string): Promise<User>`. Tier: `REVIEW` because it changes a public contract.
- Other 6 subagents return `NO_CHANGES` with reasons.

All 8 outputs reference `snapshot_id: f9e2...`. Schema validation passes.

**Phase 1 queue frozen:** `[finding_1 from Unused Code]`. Claimed files: `[src/utils/format.ts]`.

**Write pass:** removes `formatCurrency` from `src/utils/format.ts`. Reversible unit: `/tmp/pass-1.patch` captured.

**Validation after pass:** `pnpm typecheck` green, `pnpm lint` green, `pnpm test` green, `pnpm build` green. No regression from baseline.

**Phase 1 final review:** orchestrator checklist — diff matches frozen queue ✓, no excluded paths touched ✓, validation matrix ran ✓, no snapshot refresh absorbed ✓, deferred items listed ✓.

**Phase 1 commit:**

```text
chore: code cleanup phase 1 (safe)

Frozen queue:
- Unused Code: remove unused export formatCurrency from src/utils/format.ts

Validation: pnpm typecheck pass, pnpm lint pass, pnpm test pass, pnpm build pass
```

Pre-commit hook reformats one line in `src/utils/format.ts`. Post-hook diff covers only files in the frozen queue → accept.

**Run invoked as `/code-cleanup`** so `requested_max_tier=SAFE`, `approval_source=DEFAULT_SAFE_ONLY`. Run ends after Phase 1.

**Final report:**

- Applied: 1 change (unused export removal)
- Deferred REVIEW queue: 1 item (weak type in fetchUser)
- Deferred RISKY queue: 0 items
- Residual risk: the REVIEW item changes a public contract; inspect before approving.
