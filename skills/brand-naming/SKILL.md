---
name: brand-naming
version: 1.0.0
description: Generate viral, memorable brand names for companies, products, and features using Lexicon Branding's sound-symbolism methodology. Triggers on "name my brand", "brand naming", "product naming", "tagline help", "company name ideas", or /brand-naming.
---

# Brand Naming

A skill that replicates Lexicon Branding's methodology for generating viral, memorable brand names. Blends a brief strategic interview with high‑volume creative generation and iterative refinement. Covers company names, product names, taglines, and brand architecture naming patterns.

When this skill triggers, do not ask the user what to do — just start Phase 1.

## When to Use

- The user wants to name a company, product, or feature
- The user invokes `/brand-naming`
- The user says "name my brand", "help me name", "generate brand names", "naming help", "product naming", or similar phrasing
- The user wants taglines or brand architecture naming systems

## When Not to Use

- Renaming an existing brand with established equity (this is a repositioning task, not a naming task)
- Purely descriptive or functional naming requests without any strategic dimension
- Requests to evaluate existing names only (no generation)

## Invocation Contract

Use these slash commands as the canonical entry points:

- `/brand-naming` → Start the full naming process (Strategic Brief → Generate → Refine). The full auto‑mode experience.
- `/brand-naming quick` → Skip the strategic brief, user provides all context in one prompt.
- `/brand-naming refine` → User provides existing names they like and wants variations or improvements.

## Core Principles (Lexicon Methodology)

The skill should apply these principles at every generation phase. If a generated name violates a principle, stop and regenerate.

**1. "Surprising, but surprisingly familiar"**
Names should feel new but share structural DNA with words the brain already knows. Too familiar = forgettable. Too alien = unprocessable.

**2. Sound Symbolism**
Phonemes carry inherent meaning. Front vowels (i, e) suggest smallness, speed, lightness. Plosives (p, b, t, k) suggest strength, decisiveness, forward motion. Sibilants (s, z, sh) suggest smoothness, softness, sophistication. Open vowels (a, o) suggest size, openness, generosity.

**3. The "Brain Is Lazy" Principle**
Humans prefer processing fluency. Names that are easy to say are perceived as more credible and likable. Short, punchy, with familiar sound patterns.

**4. Global Safety**
Before treating a name as final, check it against:
- Does it sound like a common English/American/European slur?
- Does it sound like a bodily function or profanity in any major language?
- Would it be hard to pronounce for a non‑native speaker?
- Does it have a negative meaning in Spanish, French, German, Mandarin, Japanese, Hindi, or Arabic?

**5. Distinctiveness**
Names must pass the "bar test" — can someone overhear it across a noisy room and Google it later? Two to four syllables is ideal.

## Process

### Phase 1: Strategic Brief (Runs for `/brand-naming`)

The model should ask ALL of these questions, one at a time:

1. **What does this company or product do?** One‑line description.
2. **Who is the target audience?** Demographic and psychographic.
3. **What is the emotional territory?**
   - Bold/aggressive
   - Playful/fun
   - Premium/luxurious
   - Trustworthy/stable
   - Innovative/futuristic
   - Friendly/accessible
4. **What are 2‑3 reference brands or competitors?** (to map the naming landscape)
5. **Any constraints?** Syllable count preference? Starting or ending letter? Industry conventions to avoid?
6. **What type of name?**
   - Company/brand name
   - Product name
   - Feature name
   - Tagline or slogan
   - Sub‑brand or line extension
   - Naming architecture/system (e.g., Apple uses "i" prefix, BMW uses number series)

If the user invokes `/brand-naming quick`, they provide all answers in one prompt and the model proceeds directly to Phase 2.

### Phase 2: High‑Volume Creative Generation

Based on the brief, generate **30‑50 names** organized into creative territories. Each name must include a one‑line rationale connecting it to the brief.

**Creative Territories (exact categories):**

1. **Invented/Neological** — New word constructions using sound symbolism. Think: Vercel, Sonos, Swiffer, Febreze, Pentium, Dasani, Lucid, Impossible. These feel like real words but are coinages.
2. **Unexpected Compounds** — Juxtaposition of two words that create surprise. Think: BlackBerry, Outback, PowerBook, Impossible Burger, Cloudflare, SoundCloud, Instagram.
3. **Evocative Real Words** — Existing words used metaphorically, not literally. Think: Apple, Amazon, Chrome, Edge, Oracle, Safari, Raven, Atlas.
4. **Sound‑Symbolic Constructions** — Names engineered for how they hit the ear even if semantically empty. Think: Turo, Sonos (palindromic + mellifluous), Vercel, Pentium, Azure.
5. **Abstract/Visual/Structural** — Names that work structurally or visually. Think: Sonos (reads same upside down), WW (WW/Weight Watchers, visually minimal).

**Tagline pairing (if requested):** For the top 5 generated names, the model provides 2‑3 tagline options each. The tagline should feel like an extension of the name's emotional territory.

Cross‑check each name against the Global Safety rule. Flag high‑risk candidates with [RISK: potential issue in X language].

### Phase 3: Refinement Loop

This phase should always be offered. The user indicates favorites or says "more like X but more technical/short/fun/etc." The model narrows and generates 15‑20 new names in the favored territory.

Rules:
- The model should encourage the user to pick at least 2 directions before concluding refinement, but if the user is satisfied with one direction, proceed.
- Each refinement iteration should apply sound symbolism more explicitly than the prior round.
- If the user has chosen **Invented/Neological** or **Sound‑Symbolic**, the model should apply phoneme analysis on every new name.

### Phase 4: Vetting & Recommendations for final shortlist

For the user's shortlist (top 5‑10 names), the model should provide:

1. **Sound symbolism analysis** — What does this name subconsciously convey? Speed? Strength? Softness? Openness? Harshness? Link each phoneme cluster to its perceptual effect.
2. **Cross‑cultural risk flags** — Any potential negative meanings or pronunciations in major languages.
3. **Memorability assessment** — How easy to say, spell, and recall?
4. **Domain availability suggestions** — The user should check availability for `.com`, `.co`, `.io`, `.ai`, relevant TLDs. Model provides likely availability assessment (invented words are likely available; common real words are likely taken).
5. **Tagline pairings** — 2‑3 tagline suggestions per name.
6. **Brand architecture fit** — How this name works within broader naming systems (is it prefix‑able? Suffix‑able? Can it carry product lines?).
7. **Legal disclaimer** — A visible block stating: "This is not legal advice. Consult a trademark attorney for formal clearance and registration."

## Output Quality Bar

**Bad:** "Here are some names: TechFlow, ByteWave, CloudSync, DataNest, NetSpark."

**Bad:** Names that are generic compound words ("Data," "Tech," "Web," "Net" + suffix). These are lazy. They violate the "surprising but surprisingly familiar" principle.

**Good:** "Pentium — A neologism blending the Greek "pente" (five) with the "‑ium" suffix used in element names, suggesting precision science and forward progress. Plosive‑heavy, suggesting computational speed and strength."

**Good:** "Sonos — A constructed palindrome that reads the same upside down. Pure sound symbolism: the long 'o' vowels suggest openness and warmth, while the 's' sibilants suggest smoothness of motion. A name with no pre‑existing meaning to pollute the brand."

Every name must have a rationale. Every rationale must reference at least one of the core principles or sound‑symbolic patterns.

## Sound Symbolism Reference

Read `references/sound-symbolism.md` for the expanded phoneme‑to‑perception mapping table.

## Creative Territories Reference

Read `references/creative-territories.md` for the expanded creative territories with examples and generator heuristics.

## Naming Rules Reference

Read `references/naming-rules.md` for Lexicon's 8 essential rules for naming products. The model must generate names that do NOT violate any of these rules.

## Final Report Template

End every run with:

```markdown
## Naming Report

### Strategic Brief Summary
- Product:
- Audience:
- Emotional territory:
- Competitors mapped:
- Naming type:

### Names Delivered
(Grouped by territory)

### Final Shortlist Vetting
| Name | Sound Symbolism | Cross‑cultural Risk | Memorability | Domain Likely? | Architecture Fit |
|---|---|---|---|---|---|

### Recommended Next Steps
1. Conduct formal trademark and domain search for top 3 names.
2. Run informal "hallway test" — ask 5 people to say and spell the name.
3. Check visual appearance in logo contexts (all lowercase, all caps, mixed case).
4. Iterate further if needed.

### Legal Disclaimer
⚠️ This naming analysis is NOT legal advice. Consult a qualified trademark attorney before filing or using any name commercially.
```

## Notes
- This skill assumes the user is at the pre‑launch or rebrand stage and needs strategic naming help, not legal filing help.
- If the user has a domain already, ask if they want the name to "match" it or if they're open to changing domains.
- On every naming run, check for any naming trends that might make the name feel dated in 2‑3 years (e.g., overuse of "AI," "-ify," "me," "-ly" suffixes, "App" in names). Flag these as trend‑risky.
- Avoid names that rely on a single spelling that isn't intuitive. If a name can be spelled multiple ways, test the most likely misspellings.
- Likely trigger keywords: "brand naming", "name my brand", "product naming", "naming agency", "startup name", "company name ideas", "tagline ideas", "naming system", "brand architecture naming".
