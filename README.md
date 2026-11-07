# Custom Agent Skills

Personal collection of AI agent skills for OpenCode and compatible coding agents.

## Installation

Install skills using the [skills.sh](https://skills.sh) CLI:

```bash
npx skills add divkix/agent-skills --skill no-comments
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [brand-naming](./skills/brand-naming/) | Generate viral, memorable brand names using Lexicon Branding's sound-symbolism methodology |
| [doop-design](./skills/doop-design/) | Design screens on a Doop canvas as one desktop light master each, or as options to pick from |
| [doop-sync](./skills/doop-sync/) | Make the dark and phone copies of every Doop master, and click-test the prototype locally in all four versions |
| [doop-to-code](./skills/doop-to-code/) | Build Doop canvas screens into an app's real code, then measure the app against each design (differing pixels, text size, font, colour and position) in all four versions until they match |
| [exhaustive-site-audit](./skills/exhaustive-site-audit/) | Exhaustive black-box QA and adversarial dogfood audit of a running website using agent-browser |
| [first-principle](./skills/first-principle/) | Interrogate finished work from first principles — challenge assumptions, delete, simplify |
| [first-run-personas](./skills/first-run-personas/) | Launch QA through five first-time-user personas in parallel browsers; friction ranked by how many personas hit it |
| [no-comments](./skills/no-comments/) | Delete comments by fixing the code that needed them — hostile review, root-cause fixes, constraint encoding |
| [seo-plays](./skills/seo-plays/) | Free, repeatable SEO plays (query mining, internal linking, AI crawler check) for any site with an OpenSEO project, run from the site's repo |

## Repository Structure

```
skills/
├── brand-naming/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   ├── README.md     # Human documentation
│   └── references/   # Supporting docs for the skill
│       ├── sound-symbolism.md
│       ├── naming-rules.md
│       └── creative-territories.md
├── doop-design/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   ├── README.md     # Human documentation
│   └── scripts/      # Doop access, variant sync, local click test, frame preview (shared by the Doop skills)
├── doop-sync/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
├── doop-to-code/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   ├── README.md     # Human documentation
│   └── scripts/      # Frame finder, app-vs-design measurement
├── exhaustive-site-audit/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
├── first-run-personas/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   ├── README.md     # Human documentation
│   └── scripts/      # slow-3g.mjs network throttle
├── no-comments/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
├── seo-plays/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   ├── README.md     # Human documentation
│   └── plays/        # One file per play
└── ...
```

## Compatibility

These skills work with any AI coding agent that supports the universal skill format, including OpenCode, Claude Code, GitHub Copilot CLI, and others.

`exhaustive-site-audit` additionally requires the `agent-browser` CLI to be installed on the system.

`first-run-personas` requires the `agent-browser` CLI and Node 22+.

`doop-design`, `doop-sync` and `doop-to-code` run inside [omp](https://github.com/can1357/oh-my-pi) with Doop behind an MCP portal that has code mode (`portal_codemode_execute`), and need the `agent-browser` CLI. `doop-sync` and `doop-to-code` also need `doop-design` installed beside them.

`seo-plays` requires the OpenSEO MCP server with Google Search Console connected; the Cloudflare MCP server is optional.

## See Also

- [skills.sh](https://skills.sh) - Universal skills registry
