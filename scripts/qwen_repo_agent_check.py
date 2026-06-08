#!/usr/bin/env python3
"""Smoke: Qwen3 Coder with repo excerpt — expects inspection-style reply.

Requires NVIDIA_API_KEY (see .env.example). Not a full agent loop; validates API + prompt.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from nvidia_nim_common import chat_completion_stream, load_dotenv  # noqa: E402

MAX_EXCERPT_CHARS = 6000


def _read_excerpt(path: Path, budget: int) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) <= budget:
        return text
    return text[: budget - 40] + "\n\n[... truncated ...]\n"


def build_context() -> str:
    parts: list[str] = []
    budget = MAX_EXCERPT_CHARS
    for rel in (
        "docs/research_wiki/index.md",
        "docs/research_wiki/handoff.md",
        "docs/research_wiki/log.md",
    ):
        chunk = _read_excerpt(REPO_ROOT / rel, budget // 3)
        if chunk:
            parts.append(f"### {rel}\n{chunk}")
            budget -= len(chunk)
    return "\n\n".join(parts)


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not api_key or api_key.startswith("nvapi-your-key"):
        print("Set NVIDIA_API_KEY in .env or environment.", file=sys.stderr)
        return 1

    context = build_context()
    prompt = f"""You are a repo-aware coding agent in an IDE. Below is real project context.

{context}

---
Task: In 8-12 lines, reply using exactly these sections:
Inspected:
Observed:
Assumptions:
Next step:

Question: What is the current research focus per handoff?
What must an LLM NOT invent in this repo?
"""

    print("Calling NVIDIA NIM (streaming)...", file=sys.stderr)
    text = chat_completion_stream(
        api_key=api_key,
        prompt=prompt,
        model="qwen/qwen3-coder-480b-a35b-instruct",
        temperature=0.3,
        top_p=0.8,
        max_tokens=512,
        timeout=300,
    )
    if not text.strip():
        print("Empty response.", file=sys.stderr)
        return 1

    lower = text.lower()
    ok = any(k in lower for k in ("inspected:", "observed:", "assumption"))
    if ok:
        print("\nOK: reply uses inspection-style sections.", file=sys.stderr)
    else:
        print(
            "\nWARN: reply may not follow section format (rules still apply in Cursor).",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
