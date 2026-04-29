# Attack Surface Mapping

## General Route/Handler Discovery

```bash
if command -v rg >/dev/null 2>&1; then
  rg -n "router\.|app\.|server\.|route|routes|controller|middleware|handler|GET|POST|PUT|PATCH|DELETE|export async function|Request|Response|fetch\(" \
    -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' -g '!coverage' -g '!.git' -g '!*.test.*' -g '!*.spec.*' .
else
  grep -RInE "router\.|app\.|server\.|route|routes|controller|middleware|handler|GET|POST|PUT|PATCH|DELETE|export async function|Request|Response|fetch\(" . \
    --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=coverage --exclude-dir=.git \
    2>/dev/null || true
fi
```

## Framework-Specific Patterns

### Next.js (App Router + Pages Router)

```bash
find . -type f \( \
  -path "*/app/api/*/route.*" -o \
  -path "*/pages/api/*" -o \
  -path "*/middleware.*" \
\) -not -path "*/node_modules/*" -not -path "*/.next/*" -print
```

### Cloudflare Workers / Hono / Pages Functions

```bash
find . -type f \( \
  -name "worker.ts" -o -name "worker.js" -o \
  -name "index.ts" -o -name "index.js" -o \
  -path "*/functions/*" \
\) -not -path "*/node_modules/*" -print

rg -n "new Hono|app\.get|app\.post|app\.put|app\.patch|app\.delete|app\.all|app\.use|fetch\(request|export default|D1Database|KVNamespace|R2Bucket|DurableObject|DurableObjectState|Queue|ScheduledEvent" \
  -g '!node_modules' -g '!dist' -g '!build' . 2>/dev/null || true
```

### Express / Fastify / Koa / NestJS

```bash
rg -n "express\(|fastify\(|new Koa|@Controller|@Get|@Post|@Put|@Patch|@Delete|app\.(get|post|put|patch|delete|use|all)|router\.(get|post|put|patch|delete|use)" \
  -g '!node_modules' -g '!dist' -g '!build' . 2>/dev/null || true
```

### Django / Flask / FastAPI

```bash
rg -n "urlpatterns|path\(|re_path\(|@app\.route|@app\.(get|post|put|patch|delete)|@router\.(get|post|put|patch|delete)|APIRouter|include_router|Blueprint" \
  -g '!venv' -g '!.venv' -g '!__pycache__' . 2>/dev/null || true
```

### Go (stdlib / Gin / Chi / Echo / Fiber)

```bash
rg -n "http\.HandleFunc|http\.Handle|mux\.(HandleFunc|Handle)|r\.(Get|Post|Put|Patch|Delete|Group)|e\.(GET|POST|PUT|PATCH|DELETE)|app\.(Get|Post|Put|Patch|Delete)" \
  -g '!vendor' . 2>/dev/null || true
```

### Java / Spring / Spring Boot

```bash
rg -n "@(RestController|Controller|RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|Secured|PreAuthorize|RolesAllowed)" \
  -g '!build' -g '!target' -g '!.gradle' . 2>/dev/null || true
```

### Ruby on Rails

```bash
rg -n "resources |resource |get |post |put |patch |delete |root |namespace |scope |authenticate|before_action|skip_before_action" \
  -g '!vendor' -g '!tmp' config/routes.rb app/controllers/ 2>/dev/null || true
```

### GraphQL

```bash
rg -n "typeDefs|resolvers|gql\`|@Query|@Mutation|@Subscription|graphqlHTTP|ApolloServer|makeExecutableSchema|buildSchema" \
  -g '!node_modules' -g '!dist' . 2>/dev/null || true
```

## Middleware Discovery

```bash
rg -n "middleware|use\(|before|after|guard|interceptor|pipe|filter|authenticate|authorize|requireAuth|requireRole|requirePermission|isAuthenticated|isAuthorized|checkAuth|verifyToken|validateToken|rateLimiter|rateLimit|cors\(" \
  -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!.next' . 2>/dev/null || true
```

## What to Map

For every route/handler/endpoint found, record:

1. **Route** — URL path
2. **Method** — GET, POST, PUT, PATCH, DELETE, ALL
3. **File** — source file and line number
4. **Auth required?** — is auth middleware applied? Is it enforced server-side?
5. **Role/permission** — what authorization checks exist
6. **Inputs** — body fields, query params, path params, headers consumed
7. **Database access** — what queries/mutations run, are they scoped?
8. **Sensitive output** — does the response include tokens, PII, internal fields?
9. **External calls** — outbound HTTP requests, webhook dispatches
10. **File/storage** — uploads, downloads, signed URLs, R2/S3 access

Prioritize routes that: accept user input, access databases, handle auth, manage files, or interact with external services.
