# First Principle Skill

**Version 1.0.0**

Interrogate finished work from first principles before calling it done: challenge weak assumptions, delete what's unnecessary, simplify what's left.

## Files

| File | Purpose | Loaded at runtime? |
|---|---|---|
| `SKILL.md` | Main agent instructions. Goal check, three challenge questions, delete-first preference order, leave-alone rule, and report contract. | Yes |
| `README.md` | Documentation for humans. You're reading it. | No |

## Use It For

- Pre-done review passes ("is this actually needed?", "sanity-check before merging")
- Pruning speculative, over-complicated, or assumption-driven work
- Simplifying after deletions open up room

## Do Not Use It For

- Building the thing in the first place — run this after the work exists
- Comment-only cleanup — use `no-comments` instead

## How It Works

1. **Challenge** — Measure what was built against the actual goal; name anything unnecessary, overly complicated, or assumption-driven.
2. **Prune** — Delete first, simplify second, optimize third, automate last.
3. **Leave alone if good** — No change is a valid outcome; report what survived and why.
