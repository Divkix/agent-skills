# Custom Agent Skills

Personal collection of AI agent skills for OpenCode and compatible coding agents.

## Installation

Install skills using the [skills.sh](https://skills.sh) CLI:

```bash
npx skills add divkix/agent-skills --skill code-cleanup
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [code-cleanup](./skills/code-cleanup/) | Deep codebase cleanup using 8 focused subagents |
| [security-audit](./skills/security-audit/) | Full-codebase defensive security audit with 5-phase pipeline |
| [brand-naming](./skills/brand-naming/) | Generate viral, memorable brand names using Lexicon Branding's sound-symbolism methodology |
| [exhaustive-site-audit](./skills/exhaustive-site-audit/) | Exhaustive black-box QA and adversarial dogfood audit of a running website using agent-browser |

## Repository Structure

```
skills/
├── code-cleanup/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
├── security-audit/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   ├── README.md     # Human documentation
│   └── references/   # Supporting docs for the skill
│       ├── inventory.md
│       ├── attack-surface.md
│       ├── scanners.md
│       ├── vuln-patterns.md
│       └── platform-checks.md
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
└── ...
```

## Compatibility

These skills work with any AI coding agent that supports the universal skill format, including OpenCode, Claude Code, GitHub Copilot CLI, and others.

`exhaustive-site-audit` additionally requires the `agent-browser` CLI to be installed on the system.

## See Also

- [skills.sh](https://skills.sh) - Universal skills registry
