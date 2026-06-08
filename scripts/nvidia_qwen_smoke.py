#!/usr/bin/env python3
"""Smoke-test NVIDIA NIM chat API for qwen/qwen3-coder-480b-a35b-instruct.

Requires NVIDIA_API_KEY in the environment (never commit the key).
Docs: https://docs.api.nvidia.com/nim/reference/qwen-qwen3-coder-480b-a35b-instruct-infer
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from nvidia_nim_common import (  # noqa: E402
    chat_completion,
    chat_completion_stream,
    load_dotenv,
)

DEFAULT_MODEL = "qwen/qwen3-coder-480b-a35b-instruct"


def main() -> int:
    p = argparse.ArgumentParser(description="NVIDIA NIM Qwen3 Coder smoke test.")
    p.add_argument(
        "prompt",
        nargs="?",
        default="Reply with exactly: NVIDIA NIM smoke OK",
        help="User message content (default is a tiny connectivity check).",
    )
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--top-p", type=float, default=0.8)
    p.add_argument("--max-tokens", type=int, default=32)
    p.add_argument("--timeout", type=int, default=300, help="HTTP timeout seconds.")
    p.add_argument(
        "--no-stream",
        action="store_true",
        help="Wait for full JSON response (slower for large models).",
    )
    args = p.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not api_key:
        print(
            "Missing NVIDIA_API_KEY. Copy .env.example to .env or set the variable.",
            file=sys.stderr,
        )
        return 1
    if api_key.startswith("nvapi-your-key"):
        print("Replace placeholder key in .env with a real nvapi- key.", file=sys.stderr)
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
            message = data["choices"][0]["message"]
            print(json.dumps(message, indent=2, ensure_ascii=False))
        else:
            print("Streaming (first token = API OK):", file=sys.stderr)
            text = chat_completion_stream(**common)
            if not text.strip():
                print("No content in stream.", file=sys.stderr)
                return 1
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {body}", file=sys.stderr)
        if exc.code == 403:
            print("Check NVIDIA_API_KEY at build.nvidia.com (rotate if exposed).", file=sys.stderr)
        return 1
    except TimeoutError:
        msg = f"Timed out after {args.timeout}s. Retry or use --timeout 600."
        print(msg, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
