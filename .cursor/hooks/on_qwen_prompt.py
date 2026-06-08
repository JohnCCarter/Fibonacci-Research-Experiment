#!/usr/bin/env python3
"""beforeSubmitPrompt: Qwen must have GLM handoff or /qwen-implement bootstrap."""

from __future__ import annotations

import json
import sys


def _is_qwen_model(model: str) -> bool:
    m = model.lower()
    return "qwen" in m or "qwen3" in m


def _has_bootstrap(prompt: str, attachments: list) -> bool:
    markers = (
        "glm handoff",
        "implementation handoff",
        "/qwen-implement",
        "in scope:",
        "out of scope:",
        "repo-aware",
        "/repo-agent",
        "research_wiki",
    )
    pl = prompt.lower()
    if any(m in pl for m in markers):
        return True
    for att in attachments:
        if not isinstance(att, dict):
            continue
        path = (att.get("file_path") or "").replace("\\", "/").lower()
        if "model-handoff" in path or "research_wiki" in path:
            return True
    return False


def main() -> int:
    payload = json.load(sys.stdin)
    model = payload.get("model") or ""
    prompt = payload.get("prompt") or ""
    attachments = payload.get("attachments") or []

    if not _is_qwen_model(model):
        print(json.dumps({"continue": True}))
        return 0

    if len(prompt.strip()) < 12:
        print(json.dumps({"continue": True}))
        return 0

    if _has_bootstrap(prompt, attachments):
        print(json.dumps({"continue": True}))
        return 0

    print(
        json.dumps(
            {
                "continue": False,
                "user_message": (
                    "Qwen implementer: get a GLM-5.1 handoff first (/glm-plan in GLM chat), "
                    "then /qwen-implement here and paste the handoff. "
                    "See docs/MODEL_COLLABORATION.md."
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except json.JSONDecodeError:
        print(json.dumps({"continue": True}))
        raise SystemExit(0) from None
