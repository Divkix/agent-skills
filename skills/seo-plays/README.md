# SEO Plays Skill

Small, free, repeatable SEO jobs for pages that already exist: find searches a page should answer, add internal links to pages that almost rank, and check that AI search bots can reach the site. Each tip ("play") is one file, so new tips slot in without touching the others.

It works on any website repo whose domain has a project in [OpenSEO](https://github.com/every-app/open-seo) (hosted or self-hosted) with Google Search Console connected. You run it from inside the site's repo, and it works out which OpenSEO project to use from the site's domain. No project IDs or config files.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | The menu of plays and the rules every play follows. | Yes |
| `plays/query-mining.md` | Long (8+ word), question and price/cost searches a page already shows up for, and what to answer on it. | When that play runs |
| `plays/internal-linking.md` | Links from existing posts to pages ranking 4-15, using their own searches as anchor text. | When that play runs |
| `plays/ai-crawlers.md` | Checks robots.txt and Cloudflare settings for blocked ChatGPT, Claude and Perplexity bots. | When that play runs |
| `README.md` | Documentation for humans. You're reading it. | No |

## Setup

1. **Install the skill.** Either:

   ```bash
   npx skills add divkix/agent-skills --skill seo-plays
   ```

   or, to keep it updating with this repo, symlink it:

   ```bash
   ln -s ~/GitHub/agent-skills/skills/seo-plays ~/.agents/skills/seo-plays
   ```

2. **Connect the OpenSEO MCP server** in your agent (`https://app.openseo.so/mcp`, or `https://<your-openseo>/mcp` if you self-host).
3. **In OpenSEO, give the site a project** with its domain set and Google Search Console connected on the project's Integrations page.
4. **Connect the Cloudflare MCP server** if you want the AI crawler check to read zone settings. Without it, that play checks robots.txt only.

## How to use it

Open your agent **inside the site's repo** and ask in plain words:

```text
run query mining
do an internal linking pass
check if AI bots are blocked on this site
```

The skill finds the site's domain in the repo (Astro or Wrangler config, `package.json`, `robots.txt`, README) and matches it to your OpenSEO projects. If it finds no match, or more than one, it asks you instead of guessing.

Or start it by name: `/seo-plays` (Claude Code, OpenCode) or `/skill:seo-plays` (omp).

Every play follows the same loop:

1. Pulls the last 3 months of Search Console data (free, no DataForSEO credit).
2. Shows you a table of proposed changes and **waits for your OK**.
3. Edits the repo on a `seo/<play>-<date>` branch, as one commit.
4. Ends with a changelog so you can revert anything.

## How often to run each play

| Play | When | Time |
|---|---|---|
| AI crawler check | Once. Again only after changing Cloudflare or robots.txt | ~10 min |
| Internal linking | Once. Then after each new post | ~20 min |
| Query mining | Monthly | ~20 min |

Google takes 2-8 weeks to react to a change, so the skill won't re-edit a page changed in the last 4 weeks. Make the change, then leave the page alone for a month.

## Adding a new play

1. Create `plays/<name>.md` with four sections: **Goal**, **Data** (which tools, which parameters), **Steps**, **Output**.
2. Add one row to the menu table in `SKILL.md`.
3. Add it to the file table and the cadence table in this README.

## Notes

- None of the plays spend DataForSEO credit. Research that does (keyword research, competitors, audits) belongs to OpenSEO's own skills.
- To leave a site alone, just don't run the skill in its repo.
- Search Console hides rare searches, so small sites return a handful of rows per play, not hundreds. That's expected.
