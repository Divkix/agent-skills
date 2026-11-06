# Query mining

## Goal

Find the specific searches a page already shows up for but doesn't clearly answer, then answer them near the top of that page. No new articles: Google already shows these pages to these people.

## Data

One call per site, free:

```json
{
  "projectId": "<matched project>",
  "dimensions": ["query", "page"],
  "dateRange": "last_3_months",
  "rowLimit": 1000,
  "dataState": "final"
}
```

Page with `startRow` while `hasMore` is true. The tool has no regex filter, so filter the rows yourself with these patterns (case-insensitive):

```text
# Long searches (8+ words), all sites
^(?:\S+\s+){7,}\S+$

# Questions, all sites
^(who|what|when|where|why|how|which|can|does|is|should)\s

# Money words, all sites
\b(price|cost|subsidy|vs|best|calculator|per (sq|square)|lakh)\b
```

Many searchers don't phrase questions ("solar subsidy in gujarat 2026"), especially outside the US, so the money-words filter often finds more than the question filter. Add words that fit the business from its project context (for example a local currency unit).

## Steps

1. Keep rows matching any filter with **impressions >= 10** and **position <= 20**. Google hides rare searches, so a small site returns a handful of rows, not hundreds. On a big site, raise the impressions floor.
2. Group the rows by page. Merge near-duplicates and misspellings into one question ("asu class seach" and "asu clas search" are the same need).
3. Read each page's source in the repo. Drop questions the page already answers in its first screen.
4. For each page, keep at most **5** questions, ranked by impressions. Prefer low-CTR rows: high impressions with few clicks means the result doesn't look like the answer.
5. Draft the change for each question: a direct 1-3 sentence answer, placed in the intro or in a short FAQ section near the top. Use real numbers from the page or the repo; never invent prices, subsidy amounts or dates. If a number isn't available, mark it `[NEEDS NUMBER]` for the user.
6. If the page title or meta description doesn't promise the answer, draft a new one too.

## Output

A table per site, then wait for OK:

| Page | Search (impressions, position, CTR) | Answered now? | Proposed change |
|---|---|---|---|

After approval, make the edits per the shared rules in `SKILL.md`. FAQ sections are for readers and AI answers; don't promise the expanded FAQ result in Google, which it no longer shows for most sites.
