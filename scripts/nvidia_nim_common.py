"""Shared stdlib helpers for NVIDIA NIM chat/completions smoke scripts."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines into os.environ without overwriting existing keys."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _post_chat(*, api_key: str, payload: dict, timeout: int) -> urllib.request.addinfourl:
    req = urllib.request.Request(
        f"{NVIDIA_BASE}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=timeout)


def chat_completion(
    *,
    api_key: str,
    prompt: str,
    model: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    timeout: int,
) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": False,
    }
    with _post_chat(api_key=api_key, payload=payload, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def chat_completion_stream(
    *,
    api_key: str,
    prompt: str,
    model: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    timeout: int,
) -> str:
    """Stream SSE chunks; return full assistant text."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": True,
    }
    parts: list[str] = []
    with _post_chat(api_key=api_key, payload=payload, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line.removeprefix("data:").strip()
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            delta = chunk["choices"][0].get("delta") or {}
            text = delta.get("content") or ""
            if text:
                parts.append(text)
                print(text, end="", flush=True)
    if parts:
        print()
    return "".join(parts)
