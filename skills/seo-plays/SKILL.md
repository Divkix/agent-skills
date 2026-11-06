---
name: seo-plays
description: Run small, free, repeatable SEO plays on the website repo you're in, using its OpenSEO project's Search Console data. Use when asked to mine Search Console queries (long queries, questions, FAQ ideas), add internal links, check whether AI crawlers (ChatGPT, Claude, Perplexity) are blocked, or to "run an SEO play".
---

# SEO plays

Small, free, repeatable SEO jobs on pages that already exist. Each play lives in its own file under `plays/`. Research workflows (keyword research, competitors, audits) belong to the OpenSEO skills, not here.

## Before any play

1. **Find the site's domain from the current repo.** Look for the production URL in: `site:` in `astro.config.*`; site URL variables (`*_SITE_URL`, `APP_URL`, `BASE_URL`) or custom domains in `wrangler.json*` / `alchemy.run.ts`; the `Sitemap:` line or base URL in robots.txt (`public/robots.txt` or a robots route); `homepage` in `package.json`; `public/CNAME`; the README. If the current folder isn't a website repo, stop and ask which repo to run in.
2. **Match it to an OpenSEO project.** Call `list_projects` and pick the project whose `domain` equals the site's domain, ignoring scheme and `www.`. If no domain matches, fall back to a project whose name matches the repo name. If nothing matches, or more than one does, ask the user; never guess. If there is no project, point them at `seo-project-setup`.
3. **Load what the project knows.** Call `get_project_context` (free) for the business, audience and key pages. The project's `locationCode` from step 2 is its market.
4. **Pick the play** from the menu and read its file. Read only that file.

Every play here is free: never call a tool that spends DataForSEO credit. If a play seems to need one, stop and say so. If Search Console isn't connected on the project, tell the user to connect it on the project's Integrations page and stop.

## Menu

| Play | File | Use when | Cadence |
|---|---|---|---|
| Query mining | `plays/query-mining.md` | Find long or question-style searches a page already shows up for, and what to answer on it | Monthly |
| Internal linking | `plays/internal-linking.md` | Point links from existing posts at pages stuck at positions 4-15 | Once, then after each new post |
| AI crawler check | `plays/ai-crawlers.md` | Confirm ChatGPT, Claude and Perplexity can reach the site | Once, then after Cloudflare or robots.txt changes |

## Rules shared by every play

- Show the plan as a table and wait for the user's OK before editing any file.
- Edits happen in the current repo, on a branch named `seo/<play>-<yyyy-mm-dd>`, as one commit. Read the repo's `AGENTS.md` first and follow its conventions.
- To find the file behind a URL, match the URL path to the repo's routes, then confirm by searching the repo for the page's title.
- Google needs 2-8 weeks to react. Don't re-run a play on a page edited in the last 4 weeks (check `git log` for that file); say when it is next due instead.
- End with a short changelog: file, what changed, why.

## Adding a play

Create `plays/<name>.md` with four sections: **Goal**, **Data** (which tools, which parameters), **Steps**, **Output**. Add one row to the menu above. Nothing else changes.
