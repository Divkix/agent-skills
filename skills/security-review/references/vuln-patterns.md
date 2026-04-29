# Vulnerability Hunting Patterns

All commands use `rg` (ripgrep). If unavailable, substitute with `grep -RInE` and equivalent exclude flags.

Standard excludes for all commands:
```
-g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' -g '!.git'
```

---

## 1. Authorization & Tenant Isolation (HIGHEST PRIORITY)

```bash
rg -n -i "(role|permission|authorize|authorized|admin|tenant|orgId|organizationId|workspaceId|teamId|userId|ownerId|accountId|isAdmin|requireAuth|requireUser|currentUser|session\.user|ctx\.user|req\.user|c\.get\(.*user)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- IDOR/BOLA: routes that read/write by ID without verifying the authenticated user owns the object
- Missing ownership check: `findUnique({ where: { id } })` without tenant/user filter
- Missing role check: admin functions protected only by login, not by role
- Tenant ID from client: `tenantId` or `orgId` taken from request body/query instead of session
- Unscoped queries: `UPDATE`/`DELETE` by ID without `AND user_id = ?` or equivalent
- Horizontal privilege escalation: user A can access user B's data by changing an ID

---

## 2. Authentication

```bash
rg -n -i "(auth|session|jwt|cookie|login|logout|register|signup|signin|password|oauth|callback|middleware|csrf|token|verify|bcrypt|argon|scrypt|pbkdf)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- Routes that should require auth but don't have auth middleware
- Auth enforced only in frontend (client-side redirect, no server check)
- JWT accepted without verifying signature, issuer, audience, or expiry
- JWT secret that's weak, hardcoded, or shared across environments
- Insecure cookie flags: missing `HttpOnly`, `Secure`, `SameSite`
- OAuth missing `state` or `nonce` parameter
- Password reset token without expiry or single-use enforcement
- Login/register/reset endpoints without rate limiting
- Identity derived from request body/header instead of verified session
- Passwords stored in plaintext or weak hash (MD5, SHA1, unsalted)

---

## 3. Secrets

```bash
rg -n -i "(api[_-]?key|secret|token|password|passwd|private[_-]?key|client[_-]?secret|jwt[_-]?secret|database_url|db_url|auth[_-]?secret|stripe|github_pat|bearer|BEGIN RSA|BEGIN OPENSSH|BEGIN PRIVATE KEY|AKIA[A-Z0-9])" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' -g '!.git' -g '!*.lock' -g '!*-lock.*' .
```

**What to flag:**
- Real secrets hardcoded in source files (not just env variable names)
- Secrets in frontend-exposed env prefixes: `NEXT_PUBLIC_`, `VITE_`, `PUBLIC_`, `REACT_APP_`, `EXPO_PUBLIC_`
- Secrets in `wrangler.toml` under `[vars]` instead of `[secrets]`
- Secrets committed in `.env` files (check `.gitignore` for `.env`)
- Secrets in CI config files (`.github/workflows/*.yml`, `.gitlab-ci.yml`)
- Secrets logged via `console.log`, `logger.info`, or equivalent
- Weak placeholder secrets used in production code paths (e.g., `secret123`, `changeme`, `test`)
- AWS access keys (pattern: `AKIA[A-Z0-9]{16}`)

---

## 4. Injection & Unsafe Execution

```bash
rg -n "(rawQuery|queryRaw|executeRaw|\$queryRaw|\$executeRaw|createQuery|sql\`|SELECT |INSERT |UPDATE |DELETE |exec\(|spawn\(|execSync\(|spawnSync\(|execFile\(|eval\(|new Function|child_process|Runtime\.getRuntime|ProcessBuilder|os\.system|subprocess\.(call|run|Popen)|shell=True)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- SQL string concatenation or template literal interpolation with user input
- ORM raw queries with interpolated variables instead of bound parameters
- `child_process.exec/spawn` with user-controlled arguments
- `eval()`, `new Function()`, `vm.runInNewContext()` with user input
- Unsafe template rendering (server-side template injection)
- LDAP injection, NoSQL injection (`$where`, `$regex` in MongoDB)
- GraphQL injection (deeply nested queries, introspection enabled in prod)
- Regex DoS: user-controlled regex patterns or catastrophic backtracking

---

## 5. Input Validation & Mass Assignment

```bash
rg -n "(req\.body|request\.json|request\.formData|searchParams|params|\.body\b|zod|yup|joi|valibot|superstruct|class-validator|create\(|update\(|insert\(|save\(|upsert\()" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- No schema validation on request body (no zod, joi, yup, etc.)
- Request body spread directly into DB create/update: `prisma.user.create({ data: req.body })`
- Client can set privileged fields: `role`, `permissions`, `isAdmin`, `ownerId`, `tenantId`, `price`, `status`, `verified`, `emailVerified`
- Missing enum validation on status/type fields
- No `Content-Length` or body size limit on file/JSON endpoints
- No pagination limit (unbounded `take`/`limit`/`page_size`)
- Missing type coercion (string ID where number expected, etc.)

---

## 6. XSS & Frontend Exposure

```bash
rg -n "(dangerouslySetInnerHTML|innerHTML|outerHTML|insertAdjacentHTML|document\.write|v-html|bypassSecurityTrust|\[innerHTML\]|marked\(|markdown|sanitize|DOMPurify|localStorage|sessionStorage|window\.location)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- `dangerouslySetInnerHTML` or `innerHTML` with unsanitized user content
- Markdown rendered without sanitizer (marked, remark without rehype-sanitize)
- Angular `bypassSecurityTrust*` usage
- Vue `v-html` with user-controlled content
- Auth tokens stored in `localStorage`/`sessionStorage` (prefer httpOnly cookies)
- API responses leaking internal fields: password hashes, internal IDs, admin flags, secrets
- Source maps served in production (if app contains sensitive logic)
- Stack traces or error details returned to users in production
- Open redirect: `window.location = userInput` or redirect URL from query param

---

## 7. CORS, CSRF & Security Headers

```bash
rg -n -i "(cors|Access-Control-Allow-Origin|Access-Control-Allow-Credentials|csrf|sameSite|secure:|httpOnly|Content-Security-Policy|Strict-Transport-Security|X-Frame-Options|frame-ancestors|Referrer-Policy|Permissions-Policy|helmet|X-Content-Type-Options)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- `Access-Control-Allow-Origin: *` combined with `credentials: true`
- Origin reflected from request header without allowlist
- Missing `Vary: Origin` header when CORS origin varies
- State-changing endpoints (POST/PUT/DELETE) using cookie auth without CSRF protection
- Missing `Content-Security-Policy` on apps serving user content
- Missing `Strict-Transport-Security` (HSTS)
- Missing `X-Frame-Options` or `frame-ancestors` (clickjacking)
- Missing `X-Content-Type-Options: nosniff`
- Missing `Referrer-Policy`
- Overly permissive CSP (`unsafe-inline`, `unsafe-eval`, `*`)

---

## 8. File Uploads & Downloads

```bash
rg -n -i "(upload|multipart|formData|file|filename|mime|content-type|bucket|s3|r2|storage|signedUrl|presigned|blob|download|getObject|putObject)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- No file size limit on uploads
- No MIME type or file extension validation
- User-controlled filename used in filesystem path (path traversal: `../../../etc/passwd`)
- Executable file types accepted (`.js`, `.php`, `.sh`, `.exe`, `.html`)
- Storage bucket publicly accessible by default
- File downloads served without authorization check
- Signed URLs without expiry or with very long expiry
- Predictable object keys allowing cross-tenant access (e.g., `uploads/{userId}/{filename}` where userId is guessable)

---

## 9. SSRF & Outbound Requests

```bash
rg -n "(fetch\(|axios\.|got\(|request\(|http\.get|https\.get|urllib|httpx|new URL\(|callbackUrl|redirectUrl|importUrl|remoteUrl|webhookUrl|imageUrl|avatarUrl|proxyUrl)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- Server fetching arbitrary user-supplied URLs without validation
- No URL allowlist for outbound requests
- No blocking of private IPs (127.0.0.1, 10.x, 172.16-31.x, 192.168.x, 169.254.169.254, fd00::, ::1)
- Following redirects to internal addresses
- Cloud metadata endpoint accessible (169.254.169.254, metadata.google.internal)
- User-controlled webhook URLs without domain/protocol validation

---

## 10. Webhooks & Integrations

```bash
rg -n -i "(webhook|stripe-signature|svix|x-hub-signature|x-signature|hmac|timing.safe|timingSafe|rawBody|verify.*signature|signature.*verify)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- Webhook endpoint without signature verification
- Signature verified against parsed body instead of raw body
- Missing timestamp tolerance (replay attacks)
- No replay protection (idempotency key or seen-event tracking)
- Webhook secret hardcoded in source instead of environment variable
- Trusting webhook body payload without server-side verification (e.g., trusting `amount` from Stripe webhook instead of fetching from API)
- Missing constant-time comparison for signature verification

---

## 11. Logging & Privacy

```bash
rg -n "(console\.log|console\.error|console\.warn|logger\.|log\.(info|warn|error|debug)|logging\.|Authorization|Cookie|password|token|secret|stack|debug|audit|pino|winston|bunyan)" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' .
```

**What to flag:**
- Logging secrets, auth tokens, cookies, API keys, passwords
- Logging PII (email, phone, SSN, address) without redaction
- Stack traces or error internals returned to users in HTTP responses
- `debug: true` or verbose logging enabled in production config
- Missing audit logs for: admin actions, permission changes, data exports, account deletion, auth events
- `console.log` statements with sensitive data left in production code
