## Worked Example

Compact end-to-end run on a small TypeScript Cloudflare Workers repo (~140 files).

**Preflight:**

- Language: TypeScript; framework: Hono on Cloudflare Workers; package manager: pnpm.
- Validation matrix: `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm build`. Baseline: all green.
- Dirty files: none. Staged hunks: none. Files in scope: 142 (< 5K → proceed).
- Boundary files: `src/types/generated/openapi.d.ts` (flagged, default-excluded).
- Area scan: unused code, weak types, and comments show signal; the other areas show none.

**Execution model:** small repo → research **inline**. The orchestrator investigates the areas with signal directly (no subagent fan-out); no-signal areas are skipped, not spawned.

**Findings:**

- **Unused code** (`SAFE`): `src/utils/format.ts:12` exports `formatCurrency`; knip reports 0 imports and no dynamic references. Proposed: remove lines 12–18. Validation impact: none.
- **Weak types** (`REVIEW`): `src/api/user.ts:23` has `fetchUser(id: any): Promise<any>`; 3 call sites all pass `string` and destructure `{id, name, email}`. Proposed: `(id: string): Promise<User>`. `REVIEW` because it changes a public contract.
- **Comments** (`SAFE`): one stale `TODO(2021)` block, now obsolete.

**Phase 1 (SAFE) queue frozen:** remove `formatCurrency`; remove the stale TODO. Claimed file: `src/utils/format.ts`.

**Write passes:** remove `formatCurrency` → checkpoint → validate (typecheck/lint/test/build all green). Remove TODO → checkpoint → validate green.

**Phase 1 final review (mechanical):** diff == frozen queue ✓, no excluded paths touched ✓, validation green ✓, no faked green ✓, deferred items listed ✓.

**Phase 1 commit:**

```text
chore: code cleanup phase 1 (safe)

Frozen queue:
- Unused code: remove unused export formatCurrency (src/utils/format.ts)
- Comments: remove stale TODO(2021) (src/utils/format.ts)

Validation: pnpm typecheck/lint/test/build all pass
```

A pre-commit hook reformats one line in `src/utils/format.ts`; the post-hook diff covers only frozen-queue files → accept.

**Invoked as `/code-cleanup`** → `requested_max_tier=SAFE`, `approval_source=DEFAULT_SAFE_ONLY`. Run ends after Phase 1.

**Final report:** applied 2 SAFE changes; deferred `REVIEW` queue: 1 item (weak type in `fetchUser`, changes a public contract — inspect before approving); `RISKY` queue: empty.
