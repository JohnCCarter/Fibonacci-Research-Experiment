"""Human-fib corpus manifest — freeze WHICH facit a run sees (2026-07-20 audit, P0:1).

The 2026-06 grow-facit events changed the corpus (462 → 484 base ``fib_*.json``) while every
selection harness loads facit live from disk and only the W-gap preflight carries a frozen
count. Result: signed-off results are snapshot-bound, and a re-run silently measures a
different corpus. This module makes the corpus explicit and verifiable:

- ``build_manifest()`` — count + a deterministic sha256 fingerprint per timeframe over the
  base ``fib_*.json`` set (filename + file bytes; ``*_events.json`` sidecars excluded, same
  glob discipline as ``selection_learning.load_human_legs``).
- ``verify_manifest()`` — fail-closed comparison of the on-disk corpus against a committed
  manifest; any count or fingerprint drift is reported per timeframe.

This is **bookkeeping, not facit**: the manifest never alters, promotes, or interprets any
fib. Frozen prereg instruments are NOT modified to call this (their behaviour stays as
locked); new preregs should reference a manifest snapshot instead of an implicit "current
tree" (audit finding FIB-AUDIT-003).

Usage::

    uv run python -m fibengine.research.corpus_manifest --write   # (re)generate
    uv run python -m fibengine.research.corpus_manifest --verify  # fail-closed check
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HUMAN_FIB_ROOT = REPO_ROOT / "data" / "labels" / "human_fib" / "bitfinex" / "BTC-USD"
MANIFEST_PATH = REPO_ROOT / "data" / "labels" / "human_fib" / "MANIFEST.json"
TIMEFRAMES = ("1M", "1w", "1d", "4h")


def _base_fib_paths(root: Path, timeframe: str) -> list[Path]:
    """Base facit files for a TF — ``fib_*.json`` minus ``*_events.json`` sidecars, sorted."""
    return sorted(
        Path(p)
        for p in glob.glob(str(root / timeframe / "fib_*.json"))
        if not p.endswith("_events.json")
    )


def _fingerprint(paths: list[Path]) -> str:
    """Deterministic sha256 over (basename, bytes) of every file, in sorted order."""
    h = hashlib.sha256()
    for p in paths:
        h.update(p.name.encode("utf-8"))
        h.update(b"\x00")
        h.update(p.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()


def build_manifest(root: Path | None = None) -> dict:
    root = root or HUMAN_FIB_ROOT
    per_tf: dict[str, dict] = {}
    for tf in TIMEFRAMES:
        paths = _base_fib_paths(root, tf)
        per_tf[tf] = {"count": len(paths), "sha256": _fingerprint(paths)}
    return {
        "corpus": "human_fib/bitfinex/BTC-USD",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "generator": "fibengine.research.corpus_manifest --write",
        "timeframes": per_tf,
        "total": sum(v["count"] for v in per_tf.values()),
    }


def verify_manifest(root: Path | None = None, manifest_path: Path | None = None) -> list[str]:
    """Compare the on-disk corpus to the committed manifest. Returns mismatch strings
    (empty ⇒ OK). Missing manifest is itself a failure — fail-closed."""
    root = root or HUMAN_FIB_ROOT
    manifest_path = manifest_path or MANIFEST_PATH
    if not manifest_path.exists():
        return [f"no manifest at {manifest_path} - run --write first"]
    ref = json.loads(manifest_path.read_text(encoding="utf-8"))
    out: list[str] = []
    for tf in TIMEFRAMES:
        want = ref.get("timeframes", {}).get(tf)
        if want is None:
            out.append(f"{tf}: missing from manifest")
            continue
        paths = _base_fib_paths(root, tf)
        if len(paths) != want["count"]:
            out.append(f"{tf}: count {len(paths)} != manifest {want['count']}")
        got = _fingerprint(paths)
        if got != want["sha256"]:
            out.append(f"{tf}: sha256 drift (files added/removed/edited vs manifest)")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Human-fib corpus manifest (write / verify).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true", help="(re)generate the manifest")
    g.add_argument("--verify", action="store_true", help="fail-closed drift check")
    args = ap.parse_args(argv)
    if args.write:
        manifest = build_manifest()
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        counts = ", ".join(f"{tf}={v['count']}" for tf, v in manifest["timeframes"].items())
        print(f"manifest written: {counts} (total {manifest['total']}) -> {MANIFEST_PATH}")
        return 0
    mismatches = verify_manifest()
    if mismatches:
        for m in mismatches:
            print(f"DRIFT: {m}")
        return 1
    print("corpus manifest OK: on-disk facit matches the committed manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
