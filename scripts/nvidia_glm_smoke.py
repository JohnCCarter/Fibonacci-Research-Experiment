#!/usr/bin/env python3
"""Smoke-test NVIDIA NIM chat API for z-ai/glm-5.1 (lead agent).

Requires NVIDIA_API_KEY. Docs: https://docs.api.nvidia.com/nim/reference/z-ai-glm5.1

Status: manuell smoke-test, körs ej i CI. Bekräfta att den fortfarande används
innan borttagning/arkivering (flaggad i repo-audit för token-effektivitet).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from nvidia_nim_common import (  # noqa: E402
    chat_completion,
    chat_completion_stream,
    load_dotenv,
)

DEFAULT_MODEL = os.environ.get("NVIDIA_GLM_MODEL", "z-ai/glm-5.1")


def main() -> int:
    p = argparse.ArgumentParser(description="NVIDIA NIM GLM-5.1 smoke test.")
    p.add_argument(
        "prompt",
        nargs="?",
        default="Reply with exactly: NVIDIA GLM-5.1 smoke OK",
    )
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-tokens", type=int, default=64)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--no-stream", action="store_true")
    args = p.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not api_key:
        print("Missing NVIDIA_API_KEY.", file=sys.stderr)
        return 1

    common = {
        "api_key": api_key,
        "prompt": args.prompt,
        "model": args.model,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
    }
    try:
        if args.no_stream:
            data = chat_completion(**common)
            print(data["choices"][0]["message"])
        else:
            print("Streaming:", file=sys.stderr)
            text = chat_completion_stream(**common)
            if not text.strip():
                return 1
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
