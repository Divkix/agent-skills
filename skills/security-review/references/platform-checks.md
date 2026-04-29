# Platform-Specific Security Checks

## Cloudflare Workers / Pages

### Find Cloudflare Config Files

```bash
find . -maxdepth 5 -type f \( \
  -name "wrangler.toml" -o \
  -name "wrangler.json" -o \
  -name "wrangler.jsonc" -o \
  -name "_headers" -o \
  -name "_redirects" \
\) -print
```

### Inspect Bindings and Config

```bash
rg -n -i "(vars|kv_namespaces|d1_databases|r2_buckets|durable_objects|services|queues|ai|vectorize|hyperdrive|env\.|compatibility_date|compatibility_flags|routes|workers_dev)" \
  -g '!node_modules' -g '!dist' -g '!build' . 2>/dev/null || true
```

### Inspect D1 Queries

```bash
rg -n "(\.prepare\(|\.exec\(|\.batch\(|\.run\(|\.all\(|\.first\(|\.raw\(|sql\`|d1)" \
  -g '!node_modules' -g '!dist' -g '!build' . 2>/dev/null || true
```

### What to Flag (Cloudflare)

- **Secrets in `[vars]`**: Secrets should use `[secrets]` binding or `wrangler secret put`, not plaintext `[vars]`
- **Missing environment separation**: Same secrets/config across dev/staging/prod
- **D1 without bound parameters**: String interpolation in `.prepare()` queries → SQL injection
- **Public R2 exposure**: R2 bucket accessible without auth when it shouldn't be
- **KV for auth state**: KV is eventually consistent — unsafe for mutable session/auth state that requires strong consistency
- **Overly permissive CORS**: Worker responding with `Access-Control-Allow-Origin: *` + credentials
- **Missing security headers**: Worker responses missing CSP, HSTS, X-Frame-Options, etc.
- **`workers_dev = true` in production**: Exposes `*.workers.dev` subdomain alongside custom domain, potentially bypassing WAF/access rules
- **Public admin/debug routes**: No auth on admin or debug endpoints in Worker
- **Missing rate limits**: No rate limiting on public API endpoints (consider Cloudflare Rate Limiting rules or in-Worker logic)
- **Missing request body limits**: No `Content-Length` check or body size enforcement
- **Durable Object state**: Sensitive state stored without encryption, or DO accessed without auth
- **Queue/Cron handlers**: Background handlers that process sensitive data without validation

---

## CI/CD & Supply Chain

### Find CI/CD Config Files

```bash
find . -maxdepth 5 -type f \( \
  -path "./.github/workflows/*" -o \
  -name ".gitlab-ci.yml" -o \
  -name "Jenkinsfile" -o \
  -name ".circleci/config.yml" -o \
  -name "Dockerfile" -o \
  -name "docker-compose.yml" -o \
  -name "compose.yml" \
\) -print
```

### Inspect GitHub Actions

```bash
rg -n "(permissions:|pull_request_target|secrets\.|GITHUB_TOKEN|id-token|write-all|contents: write|actions/checkout|curl.*\|.*bash|wget.*\|.*sh|npm install -g|@latest|@master|@main)" \
  .github/workflows/ 2>/dev/null || true
```

### Inspect Docker

```bash
rg -n "(FROM |RUN |COPY |ADD |ENV |EXPOSE |USER |latest|root|chmod 777|--no-cache|apt-get|apk add)" \
  Dockerfile docker-compose.yml compose.yml 2>/dev/null || true
```

### What to Flag (CI/CD)

- **Secrets in PR workflows**: `pull_request` or `pull_request_target` workflows accessing `secrets.*`
- **`pull_request_target` with checkout of PR code**: Allows arbitrary code execution with repo secrets
- **Overbroad `GITHUB_TOKEN` permissions**: `permissions: write-all` or `contents: write` when only `read` is needed
- **Unpinned third-party actions**: Using `@master`, `@main`, or `@latest` instead of SHA pin (e.g., `actions/checkout@v4` → pin to full SHA)
- **`curl | bash` or `wget | sh`**: Arbitrary code execution from remote URL during build
- **Docker images using `:latest`**: Unpinned base images, non-reproducible builds
- **Running as root in Docker**: No `USER` directive, container runs as root
- **Sensitive env vars in Docker**: `ENV` with secrets instead of runtime injection
- **CI deploying from untrusted branches**: Deploy pipeline triggered from non-protected branches
- **Build logs exposing secrets**: `echo $SECRET` or debug output leaking credentials
- **Missing OIDC**: Using long-lived deploy credentials instead of OIDC (`id-token: write`)

---

## Docker-Specific

```bash
# Check for running as root
grep -L "^USER " Dockerfile 2>/dev/null && echo "WARNING: No USER directive — container runs as root"

# Check for .dockerignore
[ ! -f .dockerignore ] && echo "WARNING: No .dockerignore — may copy secrets into image"

# Check what's being copied
rg -n "(COPY \.|ADD \.|COPY --from)" Dockerfile 2>/dev/null || true
```

### What to Flag (Docker)

- No `.dockerignore` file (`.env`, `.git`, `node_modules` may be copied into image)
- `COPY . .` without `.dockerignore` excludes
- `RUN npm install` without `--production` (dev dependencies in production image)
- Secrets in `ENV` instructions (visible in image layers)
- `chmod 777` or overly permissive file permissions
- No health check defined
- Exposed ports that shouldn't be public

---

## Kubernetes (if applicable)

```bash
find . -maxdepth 5 -type f \( -name "*.yaml" -o -name "*.yml" \) | xargs grep -l "apiVersion:" 2>/dev/null || true

rg -n "(securityContext|runAsRoot|privileged|hostNetwork|hostPID|allowPrivilegeEscalation|readOnlyRootFilesystem|capabilities)" \
  -g '*.yaml' -g '*.yml' . 2>/dev/null || true
```

### What to Flag (K8s)

- Containers running as root / privileged
- `hostNetwork: true` or `hostPID: true`
- Missing `securityContext` / `readOnlyRootFilesystem`
- Secrets in plaintext ConfigMaps instead of Secrets
- No network policies
- No resource limits
