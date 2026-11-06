# Internal linking

## Goal

Add links from existing posts to the pages Google almost ranks (positions 4-15), using the searches each target already ranks for as anchor text. These pages move the most and are already on the site.

## When to run

- First pass: once per site.
- After that: only when a new post is published, or when a page enters positions 4-15. Find the last `seo(links):` commit in the site repo; if no post was added or changed since, say so and stop. Re-linking with no new content just moves links around.

## Data

Free:

```json
{
  "projectId": "<matched project>",
  "dimensions": ["query", "page"],
  "dateRange": "last_3_months",
  "rowLimit": 1000,
  "maxPosition": 15,
  "minImpressions": 10
}
```

## Steps

1. **Targets:** for each page, its best 1-3 queries by impressions at positions 1-10 are its anchors. Pages at positions 4-15 get priority as link targets.
2. **Sources:** every published post and page in the repo.
3. Wherever a source's body text already mentions a target's anchor query, or a close variant, propose turning that phrase into a link.
4. Rules:
   - 3-5 new internal links per source at most, spread through the body.
   - No links in headings, the first sentence, or text that is already a link.
   - Never link a page to itself. Link each target at most once per source.
   - Anchor text must read naturally. Don't rewrite sentences to force a keyword in.
   - Hub pages (a calculator, a tool, a main guide) should be linked from every page on their topic, and link back to the most important of those pages.
   - If two pages rank for the same query, they compete with each other. Flag the pair, pick the stronger one (more clicks, better position) as the main page, and send links only to it.

## Output

Show this table and wait for OK:

| Source | Anchor text | Target URL | Target's query and position |
|---|---|---|---|

After approval, make the edits per the shared rules in `SKILL.md`. The commit message starts with `seo(links):` so the next run can find it. The changelog lists every link so each can be reverted.
