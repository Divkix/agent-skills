# Scanner Execution Commands

This skill uses scanners only when they are already installed. Do not install tools automatically. If a tool is missing, record it and continue with manual fallback review.

## Create Output Directory

```bash
AUDIT_OUT="/tmp/security-audit-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$AUDIT_OUT"
echo "$AUDIT_OUT"
```

## Check Scanner Availability

```bash
for tool in gitleaks semgrep osv-scanner trivy; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "AVAILABLE: $tool -> $(command -v "$tool")"
  else
    echo "MISSING: $tool"
  fi
done
```

## Collect Versions

```bash
gitleaks version 2>/dev/null || true
semgrep --version 2>/dev/null || true
osv-scanner --version 2>/dev/null || true
trivy --version 2>/dev/null | head -20 || true
```

## Run Gitleaks

Purpose: hardcoded secrets, API keys, tokens, credentials, and private keys.

```bash
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect \
    --source . \
    --no-banner \
    --redact \
    --report-format json \
    --report-path "$AUDIT_OUT/gitleaks.json" || true
  echo "Gitleaks complete: $AUDIT_OUT/gitleaks.json"
else
  echo "gitleaks unavailable; manual secret review required" > "$AUDIT_OUT/gitleaks-missing.txt"
fi
```

Manual secret fallback:

```bash
rg -n -i "(api[_-]?key|secret|token|password|passwd|private[_-]?key|client[_-]?secret|jwt[_-]?secret|database_url|db_url|auth[_-]?secret|bearer|BEGIN RSA|BEGIN OPENSSH|BEGIN PRIVATE KEY|AKIA[A-Z0-9])" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' -g '!.git' -g '!*.lock' . 2>/dev/null || true
```

## Run Semgrep

Purpose: code-level vulnerability patterns, OWASP/CWE checks, injection, XSS, auth issues, SSRF, path traversal, and insecure crypto.

```bash
if command -v semgrep >/dev/null 2>&1; then
  semgrep scan \
    --config auto \
    --json \
    --output "$AUDIT_OUT/semgrep-auto.json" \
    . || true

  semgrep scan \
    --config p/owasp-top-ten \
    --config p/cwe-top-25 \
    --json \
    --output "$AUDIT_OUT/semgrep-owasp-cwe.json" \
    . || true
  echo "Semgrep complete"
else
  echo "semgrep unavailable; manual code-pattern review required" > "$AUDIT_OUT/semgrep-missing.txt"
fi
```

If registry configs fail because network access is unavailable, continue with manual review.

## Run OSV Scanner

Purpose: dependency vulnerabilities and known advisories.

```bash
if command -v osv-scanner >/dev/null 2>&1; then
  osv-scanner -r . \
    --format json \
    --output "$AUDIT_OUT/osv-scanner.json" || true
  echo "OSV Scanner complete: $AUDIT_OUT/osv-scanner.json"
else
  echo "osv-scanner unavailable; dependency fallback required" > "$AUDIT_OUT/osv-scanner-missing.txt"
fi
```

## Run Trivy

Purpose: filesystem vulnerabilities, IaC/config misconfigurations, Dockerfile issues, and secondary secret scanning.

```bash
if command -v trivy >/dev/null 2>&1; then
  trivy fs \
    --scanners vuln,secret,misconfig \
    --format json \
    --output "$AUDIT_OUT/trivy-fs.json" \
    . || true
  echo "Trivy complete: $AUDIT_OUT/trivy-fs.json"
else
  echo "trivy unavailable; manual infra/config review required" > "$AUDIT_OUT/trivy-missing.txt"
fi
```

## Dependency Audit Fallbacks

Run only when the relevant lockfile and tool exist:

```bash
if [ -f package-lock.json ] && command -v npm >/dev/null 2>&1; then
  npm audit --json > "$AUDIT_OUT/npm-audit.json" 2>/dev/null || true
fi

if [ -f pnpm-lock.yaml ] && command -v pnpm >/dev/null 2>&1; then
  pnpm audit --json > "$AUDIT_OUT/pnpm-audit.json" 2>/dev/null || true
fi

if [ -f yarn.lock ] && command -v yarn >/dev/null 2>&1; then
  yarn npm audit --json > "$AUDIT_OUT/yarn-audit.json" 2>/dev/null || true
fi

if { [ -f bun.lock ] || [ -f bun.lockb ]; } && command -v bun >/dev/null 2>&1; then
  bun audit > "$AUDIT_OUT/bun-audit.txt" 2>/dev/null || true
fi

if { [ -f requirements.txt ] || [ -f pyproject.toml ]; } && command -v pip-audit >/dev/null 2>&1; then
  pip-audit -f json -o "$AUDIT_OUT/pip-audit.json" 2>/dev/null || true
fi

if [ -f go.mod ] && command -v govulncheck >/dev/null 2>&1; then
  govulncheck ./... > "$AUDIT_OUT/govulncheck.txt" 2>/dev/null || true
fi

if [ -f Cargo.toml ] && command -v cargo-audit >/dev/null 2>&1; then
  cargo audit --json > "$AUDIT_OUT/cargo-audit.json" 2>/dev/null || true
fi
```

## Scanner Triage Rules

- Read scanner output files from `$AUDIT_OUT`.
- Do not paste raw JSON.
- Deduplicate findings across scanners.
- Ignore generated files, vendored dependencies, tests, fixtures, examples, and build output unless production impact exists.
- Confirm whether the affected code is reachable.
- Downgrade findings with uncertain reachability.
- Upgrade only when exploitability is clear.
- Always include the scanner source for confirmed findings.
