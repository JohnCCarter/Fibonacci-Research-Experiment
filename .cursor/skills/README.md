# Fibonacci Research Skills

This directory contains AI agent skills for the Fibonacci research project. Each skill is a portable instruction set that teaches AI agents how to work with our Fibonacci research codebase effectively.

## Skill Structure

Each skill follows the NVIDIA Agent Skills specification:
- Portable directories with a `SKILL.md` file at their root
- YAML frontmatter with required `name` and `description` fields
- Progressive disclosure model for lightweight loading

## Available Skills

- `data-analysis` - Data processing and analysis workflows for financial time series
- `optimization` - Parameter optimization for swing detection algorithms
- `backtesting` - Backtesting framework and analysis
- `validation` - Validation and testing workflows
- `research` - Research experimentation and hypothesis testing

## Installation

Skills are automatically loaded by Cursor when working with this repository.

## Adding New Skills

To add a new skill:
1. Create a new directory in `.cursor/skills/`
2. Add a `SKILL.md` file with the proper YAML frontmatter
3. Document the skill's purpose, usage, and best practices

For more information about the skills framework, see the [Agent Skills specification](https://agentskills.io/specification).

Repo-aware agent policy (inspect before edit): [docs/REPO_AWARE_AGENT.md](../../docs/REPO_AWARE_AGENT.md).