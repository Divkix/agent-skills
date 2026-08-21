# Brand Naming Skill

**Version 1.0.0**

Generates viral, memorable brand names for companies, products, and features using Lexicon Branding's sound-symbolism methodology. Blends a strategic interview with high-volume creative generation and iterative refinement, then vets the shortlist for sound symbolism, cross-cultural risk, and memorability.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Main agent instructions. Defines the core principles, the four-phase process, and the final report format. | Yes |
| `references/naming-rules.md` | The 8 essential naming rules every candidate must pass. | Before generation |
| `references/creative-territories.md` | The five creative territories, selection patterns, and generator heuristics. | Before generation |
| `references/sound-symbolism.md` | Expanded phoneme-to-perception mapping table for phoneme analysis. | Before refinement |
| `README.md` | Documentation for humans. You're reading it. | No |

## Use It For

- Naming a company, product, or feature
- Taglines and slogans
- Brand architecture naming systems (prefix/suffix/series patterns)
- Refining or generating variations on names you already like

## Do Not Use It For

- Renaming a brand with established equity (that's repositioning, not naming)
- Evaluating existing names with no generation
- Purely descriptive/functional naming with no strategic dimension
- Trademark or legal clearance (the skill explicitly disclaims this)

## How It Works

1. **Strategic Brief** — Asks about the product, audience, emotional territory, competitors, constraints, and naming type. Skipped in `quick` mode.
2. **High-Volume Creative Generation** — Produces 30–50 names across five creative territories (Invented/Neological, Unexpected Compounds, Evocative Real Words, Sound-Symbolic Constructions, Abstract/Visual/Structural), each with a rationale tied to the methodology. Every name is cross-checked against global-safety rules.
3. **Refinement Loop** — You pick favorites or a direction; the skill generates 15–20 new names in that territory with progressively more explicit sound-symbolic analysis.
4. **Vetting & Recommendations** — The final shortlist gets phoneme analysis, cross-cultural risk flags, memorability assessment, domain-availability guidance, tagline pairings, and brand-architecture fit.

## Invocation

```text
/brand-naming          # Full process: Strategic Brief → Generate → Refine
/brand-naming quick    # Skip the brief; provide all context in one prompt
/brand-naming refine   # You provide names you like; get variations/improvements
```

Or just ask naturally: "help me name my startup", "product name ideas", "tagline help".

## Output

Every run ends with a structured naming report: strategic brief summary, names grouped by territory, a shortlist vetting table (sound symbolism, cross-cultural risk, memorability, domain likelihood, architecture fit), recommended next steps, and a legal disclaimer.

## Notes

- Quality bar is explicit: generic compounds ("TechFlow", "DataNest") are rejected by design. Every name must carry a rationale grounded in sound symbolism or a core principle.
- The skill flags trend-risky patterns (overused "AI", "-ify", "-ly" suffixes) and tests likely misspellings.
- Domain availability is assessed heuristically — always verify with a registrar. Trademark clearance requires an attorney.
