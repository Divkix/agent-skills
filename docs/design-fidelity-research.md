# How others check that built code matches a design

Research date: 2026-11-07. Question: when an agent rebuilds a Doop frame with the app's own React/Tailwind components, how do other tools and teams prove the result matches, instead of an agent eyeballing two screenshots? Desk research from primary sources (docs, source code, papers); nothing was installed or bought. One claim was run locally and is marked **tested**.

## Short answer

Nobody ships a finished "does the app match the design" checker for this case: not Doop, not pen.dev, not Figma. What practitioners and tool makers converge on is the same three-layer loop:

1. **Pixel diff first.** Render the design and the app in the same browser at the same size, compute the differing pixels, and give the agent the number and a highlighted diff image. Different source code is fine: browser vendors have compared separately written pages this way for years.
2. **Measure the parts that lit up.** Read real numbers (box, font, colour) from both pages for matching elements, instead of estimating them from a picture.
3. **AI eyes last.** The model reviews only the highlighted crops, for things numbers miss (wrong image, clipping, overlap). It may not overrule a measured failure.

We already have everything needed for this: `agent-browser`, which `doop-to-code` already uses, does layers 1 and 2.

## What exists

### Doop (official)

- The official handoff is what `doop-to-code` already does: `get_frame` gives the full HTML and the coding agent **translates it into the codebase's components**; there's a ready-for-dev approval flow. [Handoff docs](https://doop.design/docs/handoff)
- `get_tokens` exports the canvas tokens as JSON, CSS (one block per theme), a Tailwind v4 `@theme` block, or markdown; `GET /api/canvases/<id>/styleguide.md` exports tokens plus style guides. Dark tokens use `data-doop-theme="dark"`, not the app's `.dark` class. [Token export](https://doop.design/docs/tokens#export-tokens-to-code)
- Token and font restyles change frames **without** clearing approval or creating a frame version, so approval alone doesn't freeze a design. A baseline has to hash HTML **and** tokens; `.doop/built.json` already does. [Approval rules](https://doop.design/docs/handoff#ready-for-dev), [token propagation](https://doop.design/docs/tokens#how-frames-carry-tokens)
- `data-doop-id` is a stable per-element id for comments and links, but only on elements someone has addressed, not every element. [Source](https://github.com/kgoedecke/doop/blob/main/shared/elementId.ts)
- Doop's own verification is `get_frame_screenshot` followed by the agent's judgement. No app-versus-frame diff, style diff or score exists in the docs, MCP tools or source. [Agent guide source](https://github.com/kgoedecke/doop/blob/main/server/guide.ts)
- The homepage advertises "Doop opens the pull request" and "a visual review on every pull request"; the automation docs say a pull-request step is **planned**. Treat both as not shipped. [Homepage](https://doop.design/#code), [automations](https://doop.design/docs/automations#build-an-integration)

### pen.dev (formerly pencil.dev; `pencil.design` is a parked domain)

- `.pen` design files live in the repo next to the code. The official design-to-code step 4 is "Run the app and compare the result with the design", done by the agent. [Design ↔ Code](https://docs.pen.dev/design-and-code/design-to-code)
- The docs say outright that sync is not continuous: "A request to recreate a component does not establish a continuously synchronized link." No numeric checker. Switching to it moves the problem instead of solving it. [Two-way sync](https://docs.pen.dev/design-and-code/design-to-code#two-way-sync)

### Other design-to-code tools

| Tool | How it avoids drift | Built-in fidelity check |
|---|---|---|
| Figma MCP | Structured design context, Code Connect maps real components | None; Figma's own guidance says to validate with screenshots |
| v0 | "compares the app with each frame as it builds" | AI comparison, no published metric |
| Subframe | Deterministic React generation, one-way sync | None |
| Onlook, Builder Code | Edit the running app itself | None found |
| Paper | Agent translates the design | CI visual diffs are a roadmap item |
| Figma Make | Local-codebase mode is a closed beta | Its verify script checks the dev server, not visuals |

Sources: [Figma MCP rules](https://developers.figma.com/docs/figma-mcp-server/add-custom-rules/), [v0 Figma docs](https://v0.app/docs/figma#what-v0-reads-from-your-file), [Subframe sync](https://docs.subframe.com/develop/concepts/syncing-components.md), [Onlook architecture](https://docs.onlook.com/developers/architecture.md), [Builder Code](https://www.builder.io/platform/code), [Paper MCP](https://paper.design/docs/mcp), [Paper roadmap](https://paper.design/blog/series-a), [Figma Make local codebase](https://help.figma.com/hc/en-us/articles/40775535020695-Make-in-your-local-codebase).

### Verification techniques and tools

- **Reference tests (WPT).** The browser vendors' test suite compares a page against a *separately written* reference page pixel by pixel, with fuzzy limits on colour difference and pixel count. This is the established answer to "but the code is different". [Reftests](https://web-platform-tests.org/writing-tests/reftests.html)
- **agent-browser** (already installed, 0.41.2): `diff screenshot --baseline <png>` returns `differentPixels`, `mismatchPercentage`, a red-on-dimmed diff image, and reports a `dimensionMismatch` instead of comparing different-sized images. `get box` and `get styles` return bounding boxes and computed styles as JSON. **Tested** locally: a 48→44px heading change gave 2530 differing pixels (1.05%) and the new box `{x:48,y:48,w:704,h:51}`. `--threshold` is per-pixel colour tolerance, not an allowed page percentage. [Diffing docs](https://agent-browser.dev/diffing), [commands](https://agent-browser.dev/commands#get-info)
- **Playwright** `toHaveScreenshot` (waits for two identical captures; `maxDiffPixels`, masks, animation off), `toHaveCSS`, `boundingBox()`. Mature, but `toHaveScreenshot` needs the Playwright test runner. Playwright's docs warn that rendering differs by OS, browser version and hardware, so both sides must be captured in the same browser. [Visual comparisons](https://playwright.dev/docs/test-snapshots)
- **pixelmatch / odiff**: the image-diff engines underneath. Newer pixelmatch has `windowSize` (largest diff inside any N×N window), so one small broken icon isn't diluted by a big page. [pixelmatch](https://github.com/mapbox/pixelmatch), [odiff](https://github.com/dmtrKovalenko/odiff)
- **Builder's 2026 agent-loop experiment** gave one of OpenAI's smaller models a mismatch number plus a red overlay, and it took a broken import from 88% of pixels mismatched to 2% over a weekend. The checker itself needed testing first: fonts that never loaded made one export read 17% off when the real difference was 0.19%, and a share-of-whole-screenshot score let a blank page on a dark background score only 3 to 5%. Score the visible content, and test the checker on pages you know are good and bad. [Builder, 2026-10-01](https://www.builder.io/blog/build-an-agent-loop-a-small-model-can-finish)
- **renderdiff** (MIT, created 2026-10-21, 0 stars): diffs two live origins, finds changed regions, attributes them to DOM elements and CSS properties, writes `results.json`. Closest match to our need, but very new; it pairs elements by tag + text snippet, and its default context is light mode only. Worth borrowing ideas from, not depending on. [Repo](https://github.com/tmashara/renderdiff), [pairing source](https://github.com/tmashara/renderdiff/blob/main/src/locate.ts)
- **figma-implementation-verify** (small independent skill): Playwright double capture, pixelmatch, box/style/colour/gap assertions, thresholds frozen before coding, and "the LLM may not override a deterministic failure". Good rules, heavy ceremony. [SKILL.md](https://github.com/nightsu/ora-figma-skills/tree/main/figma-implementation-verify)
- **Design2Code** (NAACL 2025): rejects code similarity as the oracle because different code can render the same page; pairs text blocks across two pages by text similarity with a global assignment and merges split blocks. The reference method if text pairing gets hard. [Paper](https://aclanthology.org/2025.naacl-long.199/), [matching code](https://github.com/NoviScl/Design2Code/blob/main/Design2Code/metrics/README.md)
- **Model vision limits, from the vendors.** Anthropic: "Claude's coordinate and localization outputs are approximate"; OpenAI: the model "struggles with tasks requiring precise spatial localization". Screenshots get resized before the model sees them, so a shrunk side-by-side can't show 2 px errors. [Anthropic](https://platform.claude.com/docs/en/build-with-claude/vision#limitations), [OpenAI](https://developers.openai.com/api/docs/guides/images-vision#limitations)

## What to change in doop-to-code

1. **Diff, don't only look.** In `compare.py`, after the two screenshots, run `agent-browser diff screenshot` per variant and print `differentPixels` and the mismatch % beside the heights; give the agent the diff image. Compare equal-sized viewport tiles (or the region above the first height difference), since a page that's 40 px taller shifts everything below it. Fix from the top down.
2. **Numbers for flagged regions.** For headings, buttons and cards in a red region, read `get box` / `get styles` on both pages and print expected, actual and the difference. Pair by visible text. For the few textless parts that matter (icons, image boxes), keep a small selector map instead of guessing.
3. **Take colours and sizes from `get_tokens`** (Tailwind format) rather than retyping hex values from the HTML.
4. **Same capture conditions on both sides:** same session, viewport, scale and theme; wait for `document.fonts.ready`; no animations or hover. Check the checker once: the Doop frame diffed against itself must score about 0, and a copy with one heading resized must not.
5. **The AI reviews the diff crops last** and can't call a measured mismatch fine; anything it wants to accept goes to the user.

Skipped: switching to pen.dev (no continuous sync either), adopting renderdiff (too new), Playwright Test (agent-browser covers it), and figma-implementation-verify's contract sealing (reconsider if several people build from the same canvas).
