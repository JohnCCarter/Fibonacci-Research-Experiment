#!/usr/bin/env python3
"""sessionStart: Qwen3-Coder as implementation specialist (GLM-5.1 owns plan/review)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY = REPO_ROOT / "docs/MODEL_COLLABORATION.md"


def _is_qwen_model(model: str) -> bool:
    m = model.lower()
    return "qwen" in m or "qwen3" in m


def main() -> int:
    payload = json.load(sys.stdin)
    model = payload.get("model") or ""

    if not _is_qwen_model(model):
        print("{}")
        return 0

    policy_excerpt = ""
    if POLICY.is_file():
        text = POLICY.read_text(encoding="utf-8")
        policy_excerpt = text[:1800] + ("\n[...]\n" if len(text) > 1800 else "")

    ctx = (
        "[Fibonacci repo - Qwen3-Coder IMPLEMENTER ON]\n\n"
        "You are the implementation specialist ONLY. GLM-5.1 owns plan, architecture, "
        "review, and approval.\n\n"
        "Rules:\n"
        "- Implement ONLY the approved GLM handoff scope.\n"
        "- Minimal focused diffs; return changed files, rationale, tests to run.\n"
        "- Do NOT replan or expand scope; ask if handoff is missing.\n"
        "- After GLM review, fix findings within the same scope.\n\n"
        "User slash command: /qwen-implement (paste GLM handoff under it).\n\n"
        f"Session model: {model}\n\n"
        "--- collaboration policy excerpt ---\n"
        f"{policy_excerpt}\n"
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
