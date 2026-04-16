# Custom Agent Skills

Personal collection of AI agent skills for OpenCode and compatible coding agents.

## Installation

Install skills using the [skills.sh](https://skills.sh) CLI:

```bash
bunx skills add code-cleanup
```

Or install directly from this repo:

```bash
bunx skills add Divkix/agent-skills/code-cleanup
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [code-cleanup](./skills/code-cleanup/) | Deep codebase cleanup using 8 focused subagents |

## Repository Structure

```
skills/
├── code-cleanup/
│   ├── SKILL.md      # Skill definition (for AI agents)
│   └── README.md     # Human documentation
└── ...
```

## Compatibility

These skills work with any AI coding agent that supports the universal skill format, including OpenCode, Claude Code, GitHub Copilot CLI, and others.

## See Also

- [skills.sh](https://skills.sh) - Universal skills registry
