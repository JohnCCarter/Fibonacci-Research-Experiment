#!/usr/bin/env python3
"""sessionStart: inject GLM-5.1 lead-agent context."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF = REPO_ROOT / "docs/research_wiki/handoff.md"
TEMPLATE = REPO_ROOT / "docs/research_wiki/templates/model-handoff.md"


def _is_glm_model(model: str) -> bool:
    m = model.lower()
    return "glm" in m and ("5.1" in m or "glm-5" in m or "glm5" in m)


def _read_excerpt(path: Path, max_chars: int) -> str:
    if not path.is_file():
        return f"({path.name} not found)"
    text = path.read_text(encoding="utf-8").replace("\u2192", "->")
    return text if len(text) <= max_chars else text[: max_chars - 40] + "\n\n[... truncated ...]\n"


def main() -> int:
    payload = json.load(sys.stdin)
    model = payload.get("model") or ""

    if not _is_glm_model(model):
        print("{}")
        return 0

    ctx = (
        "[Fibonacci repo - GLM-5.1 LEAD agent ON]\n\n"
        "Constitution: AGENTS.md (CONSTITUTION FOR AGENTS AND SUBAGENTS).\n"
        "You are the lead agent (plan, handoff, review, approve).\n"
        "Qwen3-Coder is your implementation subagent — not a parallel architect.\n"
        "Do NOT let both models freely change scope.\n\n"
        "Your job: inspect wiki/repo, produce a clear implementation handoff, delegate to "
        "qwen-implementer, review output, final verification. Avoid large code edits unless "
        "user explicitly asks.\n\n"
        "Workflow: GLM plan -> delegate qwen-implementer subagent -> GLM review -> "
        "delegate fixes -> GLM verify.\n"
        "Subagent: .cursor/agents/qwen-implementer.md\n"
        "Delegate: Use the qwen-implementer subagent to implement this GLM handoff: ...\n"
        "Handoff template: docs/research_wiki/templates/model-handoff.md\n"
        "Slash: /glm-plan\n\n"
        f"Session model: {model}\n\n"
        "--- handoff.md ---\n"
        f"{_read_excerpt(HANDOFF, 2000)}\n\n"
        "--- handoff template ---\n"
        f"{_read_excerpt(TEMPLATE, 1200)}\n"
    )

    out = json.dumps(
        {"env": {"FIB_GLM_LEAD_AGENT": "1"}, "additional_context": ctx},
        ensure_ascii=True,
    )
    sys.stdout.buffer.write(out.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except json.JSONDecodeError:
        print("{}")
        raise SystemExit(1) from None
