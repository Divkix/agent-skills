# Repository Inventory Commands

## Find Repo Root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
pwd
```

## List All Files

```bash
if command -v rg >/dev/null 2>&1; then
  rg --files \
    -g '!node_modules' \
    -g '!vendor' \
    -g '!dist' \
    -g '!build' \
    -g '!.next' \
    -g '!coverage' \
    -g '!.git' \
    | sed 's#^\./##' \
    | sort
else
  find . -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/vendor/*' \
    -not -path '*/dist/*' \
    -not -path '*/build/*' \
    -not -path '*/.next/*' \
    -not -path '*/coverage/*' \
    -not -path '*/.git/*' \
    | sort
fi
```

## Find Config and Security-Sensitive Files

```bash
find . -maxdepth 5 -type f \( \
  -name "package.json" -o \
  -name "pnpm-lock.yaml" -o \
  -name "package-lock.json" -o \
  -name "yarn.lock" -o \
  -name "bun.lock" -o \
  -name "bun.lockb" -o \
  -name "requirements.txt" -o \
  -name "pyproject.toml" -o \
  -name "go.mod" -o \
  -name "pom.xml" -o \
  -name "build.gradle" -o \
  -name "build.gradle.kts" -o \
  -name "Cargo.toml" -o \
  -name "composer.json" -o \
  -name "Gemfile" -o \
  -name "wrangler.toml" -o \
  -name "wrangler.json" -o \
  -name "wrangler.jsonc" -o \
  -name "Dockerfile" -o \
  -name "docker-compose.yml" -o \
  -name "compose.yml" -o \
  -name ".env" -o \
  -name ".env.*" -o \
  -name "_headers" -o \
  -name "_redirects" \
\) -print
```

## What to Determine

After running the inventory, identify:

- **App type**: monolith, microservice, serverless, static site, fullstack
- **Frontend framework**: React, Vue, Svelte, Astro, Next.js, Nuxt, SvelteKit, etc.
- **Backend/API framework**: Express, Fastify, Hono, Koa, Django, Flask, FastAPI, Spring, Go stdlib, etc.
- **Auth/session library**: next-auth, lucia, clerk, supabase-auth, passport, jose, jsonwebtoken, etc.
- **Database**: PostgreSQL, MySQL, SQLite, D1, MongoDB, Redis, etc.
- **ORM/query layer**: Prisma, Drizzle, TypeORM, Sequelize, SQLAlchemy, raw SQL, etc.
- **Package manager**: npm, pnpm, yarn, bun, pip, cargo, go modules, etc.
- **Deployment platform**: Cloudflare Workers/Pages, Vercel, AWS Lambda, Railway, Fly.io, Docker, etc.
- **Cloudflare usage**: Workers, Pages, D1, R2, KV, Durable Objects, Queues, etc.
- **CI/CD**: GitHub Actions, GitLab CI, CircleCI, etc.
- **Route categories**: public, protected (auth required), admin/internal, webhook, upload/download, background jobs
