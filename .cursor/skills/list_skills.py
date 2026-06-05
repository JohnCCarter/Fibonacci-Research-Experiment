#!/usr/bin/env python3
"""
Script to demonstrate how to use the skills framework.
"""


def list_skills():
    """List all available skills in the repository."""
    from pathlib import Path

    skills_dir = Path(".cursor/skills")
    if skills_dir.exists():
        print("Available skills:")
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_name = skill_dir.name
                print(f"- {skill_name}")
    else:
        print("No skills directory found.")


if __name__ == "__main__":
    list_skills()
