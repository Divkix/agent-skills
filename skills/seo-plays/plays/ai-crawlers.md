# AI crawler check

## Goal

Answer one question per site: can ChatGPT, Claude and Perplexity reach it? Blocking their **search and user** bots keeps the site out of AI answers. Blocking their **training** bots is a separate, optional choice.

| Kind | User agents | Should be |
|---|---|---|
| Search and user bots | `OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User` | Allowed |
| Training bots | `GPTBot`, `ClaudeBot`, `CCBot`, `Google-Extended` | User's choice |

## Data

All read-only and free:

1. **robots.txt:** fetch `https://<domain>/robots.txt`. Note every rule that disallows a search or user bot, or `User-agent: *` with `Disallow: /`.
2. **Cloudflare zone settings** (Cloudflare MCP, `cloudflare.request`):
   - Find the zone: `GET /zones?name=<domain>`. If there is no zone, the site isn't on this Cloudflare account; check only robots.txt and say so.
   - `GET /zones/{zone_id}/bot_management`. Check `ai_bots_protection` (`block` blocks AI crawlers, including search bots) and `is_robots_txt_managed` (Cloudflare prepends its own rules to robots.txt).
3. **AI Crawl Control:** the Cloudflare dashboard page of that name shows which AI crawlers visited and which pages they hit. Point the user at it; raw access logs aren't on the free plan.

Don't test by sending requests with a faked bot user agent: Cloudflare can block fake bots, which gives false alarms.

## Output

Report the result as one row, then the fixes:

| Site | robots.txt | `ai_bots_protection` | Managed robots.txt | Verdict |
|---|---|---|---|---|

Never change Cloudflare settings or robots.txt without the user's OK. A robots.txt fix goes in the current repo per the shared rules in `SKILL.md`; a Cloudflare setting change is a dashboard toggle or one API call, shown to the user first.
