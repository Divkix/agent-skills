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
| [exhaustive-site-audit](./skills/exhaustive-site-audit/) | Exhaustive black-box QA and adversarial dogfood audit of a running website using agent-browser |
| [first-principle](./skills/first-principle/) | Interrogate finished work from first principles — challenge assumptions, delete, simplify |
| [no-comments](./skills/no-comments/) | Delete comments by fixing the code that needed them — hostile review, root-cause fixes, constraint encoding |

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
├── exhaustive-site-audit/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
├── no-comments/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
└── ...
```

## Compatibility

These skills work with any AI coding agent that supports the universal skill format, including OpenCode, Claude Code, GitHub Copilot CLI, and others.

`exhaustive-site-audit` additionally requires the `agent-browser` CLI to be installed on the system.

## See Also

- [skills.sh](https://skills.sh) - Universal skills registry
