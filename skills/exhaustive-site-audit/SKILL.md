---
name: exhaustive-site-audit
version: 1.0.0
description: Exhaustive black-box QA and adversarial dogfood audit of a running website using agent-browser. Use when asked to fully test, dogfood, QA, audit, break, visually inspect, or find issues in a web app without changing source code. Requires coverage reconciliation, visual screenshots, responsive testing, accessibility/keyboard checks, chaos testing, reproducible evidence, and report-only output.
---

# Exhaustive Site Audit

Audit a running website as a real user. Find reproducible functional, visual, responsive, accessibility, navigation, state, console, network, and UX problems. Do not fix the application.

## Input

The user should provide a target URL as the skill argument.

If no URL is provided, use `http://localhost:4321`.

Treat the target as a black box even when the agent is running inside the source repository.

## Hard constraints

- MUST NOT inspect application source code to infer behavior or correctness.
- MUST NOT modify application source, configuration, dependencies, tests, or content.
- MUST NOT fix discovered issues.
- MAY create audit evidence and reports under `dogfood-output/`.
- MUST use `agent-browser` for browser interaction.
- MUST NOT substitute another browser abstraction, curl, raw HTTP requests, or source inspection for user-side browser testing.
- MUST visually inspect rendered screenshots. DOM or ARIA inspection alone is insufficient.
- MUST continue after finding bugs. Bug count is never the stopping condition.
- MUST avoid destructive actions against production or external services, including purchases, deletions, publishing, account changes, outbound messages, or irreversible submissions.
- MUST report blocked or unsafe surfaces as untested with the exact reason.

## Bootstrap agent-browser dogfood

Before testing, load the current installed agent-browser dogfood methodology:

```bash
agent-browser skills get dogfood --full
```

Follow that methodology for browser operation, evidence capture, issue reproduction, and reporting, except where this skill overrides it.

### Overrides to dogfood

This skill changes the stopping condition from "find a useful set of issues" to exhaustive coverage.

- Ignore any target issue count such as 5 to 10 issues.
- Completion is based on coverage exhaustion, not number of findings.
- Every discovered reachable surface must end as TESTED or UNTESTED WITH REASON.
- Visual inspection is mandatory.
- A final coverage-gap sweep is mandatory.
- Do not read source code.
- Do not fix issues.

If agent-browser or its dogfood instructions cannot be loaded, stop and report the missing dependency instead of silently switching browser tooling.

# Audit workflow

Structure the work as a staged multi-perspective audit. When the host environment supports parallel or delegated execution, prefer independent isolated agent-browser sessions for specialist passes.

Recommended stages:

1. Surface discovery and inventory
2. Parallel specialist passes
3. Reproduction verification
4. Coverage reconciliation and gap sweep
5. Final report

Do not let parallel agents share mutable browser state.

## Stage 1: Map the complete reachable surface

Explore from the target URL using only browser-visible behavior.

Discover and inventory every reachable:

- route and page
- header and footer interaction
- navigation item
- internal and external link
- button and CTA
- form
- input, textarea, select, checkbox, radio, and custom field
- search, filter, sort, and pagination control
- dropdown, menu, mobile menu, tab, accordion, modal, dialog, popover, and tooltip
- carousel and media control
- interactive card, image, icon, or custom control
- downloadable item
- stateful component
- keyboard-accessible control
- loading, empty, success, validation, and error state that can be reached safely
- any other user-visible interaction surface

Follow newly discovered internal routes recursively.

Do not assume the main navigation is complete.

Create and maintain a coverage ledger with at least:

| Surface ID | Route | Element / Feature | States | Viewports | Keyboard | Status | Evidence / Notes |
|---|---|---|---|---|---|---|---|

Status is exactly one of:

- DISCOVERED
- TESTED
- BUG
- UNTESTED

Every UNTESTED item requires a reason.

## Stage 2: Independent specialist passes

Use separate agent-browser sessions where possible.

### A. Functional user

Test intended workflows end to end.

For each relevant control or flow:
- normal action
- expected success state
- repeat action
- reopen/revisit behavior
- loading and completion state
- sensible failure state where safely reachable

### B. Adversarial / chaos user

Assume normal developers already tested the obvious path.

Try relevant unpredictable behavior:

- rapid clicks
- double clicks
- repeated submission
- clicking during loading
- open/close repeatedly
- Escape unexpectedly
- Enter unexpectedly
- Tab through unusual sequences
- click outside overlays
- scroll while overlays are open
- resize while overlays are open
- navigate away mid-flow
- Back and Forward during stateful interactions
- refresh during or after state changes
- revisit completed flows
- perform actions in unusual order
- open relevant links in another tab
- alternate between tabs where safe
- interact again after errors
- change selections rapidly

Never perform destructive actions merely to increase coverage.

### C. Input and boundary user

Where safe and applicable, try:

- empty value
- whitespace only
- leading and trailing whitespace
- one character
- very long input
- Unicode
- emoji
- quotes and apostrophes
- punctuation and unusual symbols
- line breaks
- paste-like long input
- malformed formats
- zero
- negative values
- minimum and maximum boundaries
- repeated submissions
- rapid edits
- missing optional and required values

Do not turn QA into exploitation. Avoid payloads intended to compromise external systems.

### D. Visual and responsive user

Visual inspection is mandatory.

For EVERY distinct reachable route:
- inspect at least one desktop screenshot
- inspect at least one mobile screenshot

For every important UI state, also capture and visually inspect the state after interaction, including where applicable:
- open menus
- mobile navigation
- dropdowns
- dialogs
- popovers
- tabs
- expanded accordions
- validation
- errors
- loading
- success
- empty states

Use interactive or accessibility snapshots to understand controls, then use screenshots to judge actual rendering.

Use annotated screenshots where useful.

Check for:
- overlap
- clipping
- text overflow
- broken wrapping
- horizontal page scrolling
- alignment problems
- inconsistent spacing
- inconsistent sizing
- unreadable text
- poor contrast
- broken or distorted images
- broken icons
- wrong aspect ratios
- controls outside the viewport
- hidden or obscured controls
- z-index and stacking problems
- modal or dropdown layering problems
- sticky header/footer interference
- content hidden behind sticky/fixed UI
- excessive or suspicious whitespace
- layout shifts
- broken focus, hover, selected, disabled, loading, success, or error visuals
- inconsistent typography or component styling
- visual state that disagrees with functional state

Representative viewport classes:

- 320x568, small mobile
- 390x844, modern mobile
- 768x1024, tablet
- 1280x720, laptop
- 1440x900, desktop
- 1920x1080, large desktop

At minimum, every distinct route gets mobile and desktop visual coverage. Exercise additional viewport classes for unique layout/component families and suspected responsive issues.

### E. Accessibility and keyboard user

Where applicable, test keyboard-only behavior using:
- Tab
- Shift+Tab
- Enter
- Space
- Escape
- arrow keys

Inspect:
- logical focus order
- visible focus indicator
- unreachable controls
- keyboard traps
- dialog focus trapping
- focus restoration after closing overlays
- accessible names
- form labels
- semantic control behavior
- keyboard behavior of custom widgets

Run agent-browser accessibility auditing where supported. Prefer WCAG A/AA checks.

Automated accessibility output supplements manual keyboard testing. It does not replace it.

### F. Navigation and state user

Test safely applicable cases:

- internal navigation
- external links
- direct deep links
- refresh on nested routes
- Back
- Forward
- new-tab behavior
- 404 / nonexistent route
- query parameters discovered through normal use
- fragment/hash navigation
- trailing slash behavior when relevant
- revisit after state changes
- interrupted workflows

Look for:
- broken links
- wrong destinations
- incorrect tab behavior
- redirect loops
- blank screens
- lost or stale state
- broken history behavior
- content that fails after refresh

## Console and network observation

Throughout testing, inspect browser-visible console/runtime and network failures when agent-browser supports them.

Investigate:
- uncaught exceptions
- hydration/runtime errors
- failed resources
- unexpected 4xx/5xx requests
- broken image or asset requests
- repeated failing requests
- warnings that correlate with a real user-facing problem

Do not inflate the report with harmless noise.

# Bug confirmation standard

A suspicious observation is not automatically a confirmed bug.

For each candidate issue:

1. Reproduce it.
2. Reproduce it again when safe and practical.
3. Classify it as deterministic or intermittent.
4. Record the exact URL.
5. Record viewport and relevant state.
6. Record exact reproduction steps.
7. Capture screenshot evidence.
8. Capture video when motion, timing, or interaction sequence matters.
9. Capture console/network evidence when relevant.
10. State expected behavior.
11. State actual behavior.
12. Assign severity.

Severity:

- CRITICAL: site/core workflow unusable, destructive behavior, severe user-impacting failure
- HIGH: major functionality broken or significant users blocked
- MEDIUM: real functional, responsive, accessibility, or UX problem with limited impact or workaround
- LOW: genuine minor visual, polish, or usability problem worth fixing

Keep confirmed bugs separate from:
- unconfirmed observations
- subjective design preferences
- enhancement ideas

# Coverage completion gate

Finding many bugs does not mean the audit is complete.

Let:

- D = all discovered reachable surfaces
- T = surfaces actually tested
- U = surfaces explicitly untested with a valid reason

Completion requires:

`D = T + U`

No discovered surface may remain unexplained.

Before finishing:

1. Reconcile the coverage ledger.
2. Find all remaining DISCOVERED items.
3. Test them or mark them UNTESTED with reason.
4. Perform one final exploratory sweep specifically for missed routes, controls, states, and responsive problems.
5. Re-check the highest-risk flows after the broader audit.
6. Confirm every reported bug has reproduction evidence.

# Output

Create:

```text
dogfood-output/
├── report.md
├── coverage.md
├── screenshots/
└── videos/
```

`videos/` may be empty if no issue benefits from video evidence.

## report.md

Use these sections:

1. Executive Summary
2. Overall Confidence
3. Critical Findings
4. High Findings
5. Medium Findings
6. Low Findings
7. Visual / Responsive Issues
8. Accessibility Issues
9. Navigation / State Issues
10. Console / Network Issues
11. UX Observations
12. Untested Areas
13. Coverage Gaps
14. Final Assessment

For every confirmed bug include:
- title
- severity
- URL
- viewport
- prerequisites/state
- exact reproduction steps
- expected behavior
- actual behavior
- reproducibility
- screenshot/video evidence path
- console/network evidence if relevant

## coverage.md

Include:
- routes discovered
- routes tested
- interactive surfaces discovered
- interactive surfaces tested
- viewport classes tested
- keyboard/accessibility surfaces tested
- confirmed bug count by severity
- all untested surfaces and reasons
- full coverage ledger
- final D / T / U reconciliation

# Final behavior

Do not fix anything.

Do not stop because a useful number of bugs has been found.

Act like many different real users, including impatient and unpredictable ones. Test the rendered site, not the implementation. Visually inspect what the user sees. Produce reproducible evidence.

The audit is complete only when the reachable discovered surface has been reconciled against the tested surface with no unexplained gaps.
