# Security Audit Skill

**Version 1.0.0**

Autonomous repo-wide security review for backend systems, APIs, web apps, serverless apps, and Cloudflare-style deployments. Runs available security scanners, performs manual vulnerability hunting, maps the attack surface, correlates evidence, and reports exploitable findings with exact files, attack paths, fixes, and verification steps.

Designed for OpenCode today, but the structure is portable to other multi-agent coding harnesses with skill/command support. Language-agnostic — works with TypeScript, JavaScript, Go, Python, Rust, Java, Ruby, C#, PHP, and mixed monorepos.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `security-audit/SKILL.md` | Main agent instructions. Defines the audit pipeline, safety rules, severity model, and final report format. | Yes |
| `security-audit/references/inventory.md` | Repo discovery commands for stack detection, important file discovery, package/deployment identification, and repository inventory. | On demand |
| `security-audit/references/scanners.md` | Scanner orchestration for `gitleaks`, `semgrep`, `osv-scanner`, `trivy`, plus dependency-audit fallbacks. | On demand |
| `security-audit/references/attack-surface.md` | Framework-specific route, handler, middleware, API, Worker, and controller discovery patterns. | On demand |
| `security-audit/references/vuln-patterns.md` | Manual vulnerability hunting playbook for auth, authz, secrets, injection, validation, XSS, CORS, uploads, SSRF, webhooks, and logging. | On demand |
| `security-audit/references/platform-checks.md` | Cloudflare, CI/CD, Docker, serverless, and supply-chain security checks. | On demand |
| `commands/security-audit.md` | OpenCode slash-command wrapper for `/security-audit`. | Yes, when command is invoked |
| `README.md` | Documentation for humans. You're reading it. | No |

`SKILL.md` is the main runtime entrypoint. The reference files are split out so the model can pull detailed commands only when needed instead of stuffing the whole security playbook into the first breath. Less token fog, more scalpel.

## Use It For

- Full-codebase security audits
- Backend/API security review
- Web app security review
- Cloudflare Workers, Pages, D1, R2, KV, and Durable Object security checks
- Pre-release security sweeps
- Monorepo security posture review
- Auth/authz and tenant-isolation review
- Dependency and supply-chain vulnerability review
- Secret exposure review
- CI/CD and deployment hardening review
- Explicit `/security-audit` invocation

## Do Not Use It For

- Active penetration testing against live systems
- Fuzzing, brute forcing, load testing, or DAST against production
- Exploit development
- Single-file style review
- Pure dependency update work
- General code cleanup
- Formatting-only passes
- Auto-fixing vulnerabilities without explicit permission

This skill is defensive and local-first. It reads, scans, correlates, and reports. It does **not** attack live targets or mutate your codebase by default.

## How It Works

1. **Repository Inventory**: Finds the repo root, inventories source files, detects frameworks, package managers, deployment targets, Cloudflare usage, CI/CD, Docker, auth libraries, database/storage, and security-sensitive modules.
2. **Scanner Execution**: Checks for `gitleaks`, `semgrep`, `osv-scanner`, and `trivy`. Runs every available scanner automatically. Missing tools do not block the audit — the skill falls back to manual review.
3. **Attack Surface Mapping**: Finds routes, controllers, handlers, middleware, API endpoints, Workers, Pages Functions, webhook routes, upload/download flows, background jobs, and external integration points.
4. **Manual Vulnerability Hunting**: Reviews high-risk areas scanners often miss: authorization, tenant isolation, auth/session logic, secrets, injection, input validation, mass assignment, XSS, CORS, CSRF, headers, uploads, SSRF, webhooks, and logging.
5. **Platform-Specific Review**: Performs deeper checks for Cloudflare, serverless, Docker, GitHub Actions, CI/CD, dependency supply chain, and deployment config.
6. **Scanner Triage & Correlation**: Deduplicates scanner results, ignores generated/test/vendor noise, checks whether findings are reachable in production code, and separates real vulnerabilities from tool noise.
7. **Final Security Report**: Produces a structured report with severity, evidence, realistic attack path, impact, recommended fix, verification steps, confidence, and source.

## Invocation

Use this canonical form inside OpenCode:

```text
/security-audit
```

Or ask directly:

```text
Use security-audit to audit this entire codebase. Do not modify files.
```

For Cloudflare-heavy apps:

```text
Use security-audit to audit this repo with extra focus on Cloudflare Workers, wrangler config, D1 queries, R2 exposure, KV usage, CORS, headers, auth middleware, and public API routes.
```

For backend/API-heavy apps:

```text
Use security-audit to audit this backend. Focus on auth, authorization, tenant isolation, API routes, database queries, webhooks, secrets, input validation, rate limits, logging, and dependency risk.
```

For a safer first pass:

```text
Use security-audit to perform a read-only security audit. Do not modify files, do not install tools, and do not call external production services.
```

## Installation

Install the skill globally for OpenCode:

```bash
mkdir -p ~/.config/opencode/skills/security-audit
cp -R security-audit/* ~/.config/opencode/skills/security-audit/

mkdir -p ~/.config/opencode/commands
cp commands/security-audit.md ~/.config/opencode/commands/security-audit.md
```

Install the scanners once, outside the skill:

```bash
brew install gitleaks semgrep osv-scanner trivy
```

The skill never installs tools on its own. It checks what is available, runs what exists, and falls back when something is missing.

## Scanner Behavior

| Tool | Purpose | If Available | If Missing |
|---|---|---|---|
| `gitleaks` | Secret scanning | Runs redacted secret scan | Manual secret pattern review |
| `semgrep` | Static vulnerability patterns | Runs auto + OWASP/CWE configs | Manual code-pattern review |
| `osv-scanner` | Dependency vulnerabilities | Runs recursive dependency scan | Package-manager audit fallback |
| `trivy` | Vuln, secret, misconfig scan | Runs filesystem scan | Manual infra/config review |

The skill treats scanners as signal, not truth. A scanner hit is not automatically a finding. The model must correlate it with reachable code, production impact, and realistic exploitability before reporting it.

## Security Coverage Areas

1. **Authorization & Tenant Isolation** — BOLA/IDOR, missing ownership checks, tenant ID trusted from client, admin routes protected only by login, unscoped reads/updates/deletes.
2. **Authentication & Session Security** — missing auth middleware, JWT validation gaps, insecure cookies, OAuth state/nonce issues, weak password reset flows, missing auth rate limits.
3. **Secrets & Sensitive Config** — hardcoded credentials, leaked tokens, secrets in frontend env vars, secrets in wrangler config, logged secrets, weak production placeholders.
4. **Injection & Unsafe Execution** — SQL/ORM raw query injection, command injection, eval/dynamic code, template injection, unsafe regex, unsafe parsing.
5. **Input Validation & Mass Assignment** — missing schemas, direct body-to-database writes, privileged field assignment, missing enum/size/pagination limits.
6. **XSS & Frontend Exposure** — unsafe HTML rendering, unsanitized markdown, tokens in browser storage, leaked internal fields, debug/source map exposure.
7. **CORS, CSRF & Headers** — wildcard CORS with credentials, reflected origins, missing CSRF protection, missing CSP/HSTS/frame/referrer policies.
8. **File Uploads & Storage** — missing size/MIME checks, user-controlled paths, executable uploads, public buckets, unprotected downloads, weak signed URLs.
9. **SSRF & Outbound Requests** — user-controlled URLs, missing allowlists, private IP access, unsafe redirects, cloud metadata exposure.
10. **Webhooks & Integrations** — missing signature verification, replay gaps, wrong raw-body verification, hardcoded webhook secrets.
11. **Logging & Privacy** — logging tokens, cookies, PII, stack traces, debug leakage, missing audit logs.
12. **Dependencies & Supply Chain** — vulnerable packages, risky lockfiles, unmaintained security libraries, suspicious scripts.
13. **CI/CD & Deployment** — unsafe `pull_request_target`, overbroad workflow permissions, secrets in PR workflows, unpinned actions, Docker `latest`, `curl | bash`.
14. **Cloudflare-Specific Checks** — `wrangler` secrets, Worker-generated headers, D1 bound parameters, public R2, KV consistency/auth misuse, workers.dev exposure, missing public API rate limits.

## Severity Model

| Severity | Meaning |
|---|---|
| **Critical** | Auth bypass, tenant isolation bypass, RCE, SQL injection with meaningful data impact, production secret exposure, arbitrary file read/write. |
| **High** | BOLA/IDOR, missing authz on sensitive endpoint, broken role check, session flaw enabling account compromise, sensitive data exposure, SSRF to internal/cloud, webhook forgery, reachable serious dependency CVE. |
| **Medium** | Weak CORS/headers, missing rate limits on sensitive endpoints, CSRF on cookie-auth mutations, debug leakage, missing audit logs, dependency CVE with uncertain reachability. |
| **Low** | Minor hardening gaps, best-practice misses, minor information disclosure, non-production-only issues. |

## Report Format

The skill returns a structured Markdown report:

```markdown
# Security Audit Report

## 1. Executive Summary
- Overall risk:
- Total findings:
- Biggest concern:
- Review coverage:
- Main limitation:

## 2. Stack & Attack Surface
- Stack:
- Package manager:
- Backend/API:
- Frontend:
- Auth/session:
- Database/storage:
- Deployment:
- Public entrypoints:
- Protected entrypoints:
- Admin/internal entrypoints:
- Webhook/integration entrypoints:
- Highest-risk files:

## 3. Tool Execution
| Tool | Status | Output Reviewed | Summary |
|---|---|---|---|

## 4. Findings
### [SEVERITY] Finding title
- Category:
- Evidence:
- Attack path:
- Impact:
- Recommended fix:
- Verification:
- Confidence:
- Source:

## 5. Scanner Noise Ignored

## 6. Missing Coverage

## 7. Prioritized Fix Plan

## 8. Recommended CI Security Gates
```

Every finding must have exact evidence. No file path, no finding. No realistic attack path, no finding. No scanner-noise confetti.

## Safety Guarantees

- **Read-only by default** — no code edits unless explicitly requested.
- **No tool installation** — uses available tools only; missing scanners trigger fallback review.
- **No live attack behavior** — no brute force, fuzzing, DAST, load testing, or production probing.
- **Secret redaction** — found secrets are reported without printing full values.
- **Evidence-backed findings only** — every vulnerability needs a file path, route/function/config evidence, and exploit path.
- **Scanner correlation required** — scanner output is triaged before it becomes a finding.
- **Generated/test/vendor noise filtering** — excludes irrelevant artifacts unless production impact exists.
- **Reachability-aware severity** — confirmed reachable issues rank higher; uncertain reachability is downgraded or listed as missing coverage.
- **Cloudflare-aware checks** — includes Worker, Pages, D1, R2, KV, Durable Objects, wrangler config, and security-header behavior.
- **Final report includes limitations** — missing tools, runtime-only behavior, external systems, and incomplete context are called out directly.

## Recommended CI Gates

Baseline commands:

```bash
gitleaks detect --source . --redact
semgrep scan --config auto .
osv-scanner -r .
trivy fs --scanners vuln,secret,misconfig .
```

For JavaScript/TypeScript projects, also consider:

```bash
npm audit --audit-level=high
pnpm audit --audit-level high
bun audit
```

For Python projects:

```bash
pip-audit
```

For Go projects:

```bash
govulncheck ./...
```

For GitHub Actions hardening, add explicit workflow permissions and pin critical third-party actions.

## Model Compatibility

Designed for strong instruction-following coding agents.

Works best with:
- Claude Opus/Sonnet class models
- GPT-5-class reasoning models
- Kimi K2.5-class coding models
- GLM-5-class coding/reasoning models

The skill is intentionally structured as a pipeline with reference files because weaker models do better when the workflow is staged: inventory first, scanners second, manual hunting third, triage fourth, report last.

## Harness Notes

This package is wired for OpenCode:

- Skill directory: `~/.config/opencode/skills/security-audit/`
- Command file: `~/.config/opencode/commands/security-audit.md`
- Invocation: `/security-audit`

If porting to another harness, preserve the split-file structure and keep the same audit phases. The important part is not the slash command — it is the audit contract:

```text
inventory → scanners → attack surface → manual vuln hunting → platform checks → triage → report
```

## Limitations

This skill is strong static review, not magic x-ray vision.

It cannot fully prove:
- Runtime-only authorization behavior
- Environment-specific production config
- External service permissions
- Cloud IAM state not present in repo
- Secrets that exist outside the repository
- Business-logic abuse that requires product context
- Vulnerabilities hidden behind unavailable generated code or private packages

The report must state these limitations instead of pretending the audit is complete.

## Quality Bar

Bad finding:

```text
Potential SQL injection.
```

Good finding:

```text
src/routes/users.ts:42 builds SQL using req.query.id:
db.query("SELECT * FROM users WHERE id = " + req.query.id)

This is reachable from GET /api/users?id=... and uses untrusted query input without parameter binding. An attacker can inject SQL through id. Fix by validating id as UUID and using a parameterized query.
```

The goal is not a big scary report. The goal is a small number of real, fixable vulnerabilities with receipts.
