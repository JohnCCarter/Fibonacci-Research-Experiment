"""Quick NVIDIA API connectivity diag (no secrets printed)."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from nvidia_nim_common import load_dotenv  # noqa: E402

PLACEHOLDER_PREFIX = "nvapi-your-key"


def _key_configured() -> bool:
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get("NVIDIA_API_KEY", "").strip()
    return bool(key) and not key.startswith(PLACEHOLDER_PREFIX)


def _api_key() -> str:
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get("NVIDIA_API_KEY", "").strip()


def probe(key: str, label: str, timeout: int) -> None:
    payload = json.dumps(
        {
            "model": "qwen/qwen3-coder-480b-a35b-instruct",
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 1,
            "stream": False,
        }
    ).encode()
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        print(f"{label}: OK in {time.time() - t0:.1f}s")
    except urllib.error.HTTPError as exc:
        body = exc.read(500).decode("utf-8", errors="replace")
        print(f"{label}: HTTP {exc.code} in {time.time() - t0:.1f}s — {body[:200]}")
    except TimeoutError:
        print(f"{label}: TIMEOUT after {timeout}s")
    except OSError as exc:
        print(f"{label}: {type(exc).__name__} in {time.time() - t0:.1f}s — {exc}")


def main() -> None:
    print("real_key: present" if _key_configured() else "real_key: missing")
    probe("INVALID", "invalid_key", 30)
    if _key_configured():
        probe(_api_key(), "real_key", 60)


if __name__ == "__main__":
    main()
