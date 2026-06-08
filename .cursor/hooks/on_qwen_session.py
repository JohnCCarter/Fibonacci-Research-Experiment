#!/usr/bin/env python3
"""sessionStart: Qwen3-Coder as implementation specialist (GLM-5.1 owns plan/review)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF = REPO_ROOT / "docs/research_wiki/handoff.md"


def _read_excerpt(path: Path, max_chars: int) -> str:
    if not path.is_file():
        return f"({path.name} not found)"
    text = path.read_text(encoding="utf-8").replace("\u2192", "->")
    return text if len(text) <= max_chars else text[: max_chars - 40] + "\n\n[... truncated ...]\n"


def _is_qwen_model(model: str) -> bool:
    m = model.lower()
    return "qwen" in m or "qwen3" in m


def main() -> int:
    payload = json.load(sys.stdin)
    model = payload.get("model") or ""

    if not _is_qwen_model(model):
        print("{}")
        return 0

    ctx = (
        "[Fibonacci repo - Qwen3-Coder IMPLEMENTER ON]\n\n"
        "Constitution: AGENTS.md §5 (implementer subagent of GLM-5.1).\n"
        "You implement ONLY an approved GLM handoff — do not replan or expand scope.\n\n"
        "Rules:\n"
        "- Minimal focused diffs; return changed files, rationale, tests to run.\n"
        "- Missing or unclear handoff → ask; do not guess scope.\n"
        "- After GLM review, fix findings within the same scope.\n\n"
        "Slash: /qwen-implement (paste GLM handoff under it).\n"
        "Ops detail: docs/agent/MODEL_COLLABORATION.md\n\n"
        f"Session model: {model}\n\n"
        "--- handoff.md ---\n"
        f"{_read_excerpt(HANDOFF, 2000)}\n"
    )

    out = json.dumps(
        {"env": {"FIB_QWEN_IMPLEMENTER": "1"}, "additional_context": ctx},
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
