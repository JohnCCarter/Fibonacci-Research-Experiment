"""Phase 2 dummy feature-contract validator — stdlib-only, no Genesis touch.

Mechanically validates a *future* Fib → Genesis V2 feature export against the Phase 1 spec
(``docs/research_wiki/reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md``).
This is a **contract test, not a feature export**: it reads two synthetic dummy CSV
tables and checks that the schema, join keys, and causal invariants *can be verified
mechanically*. It computes **no** Fib features, reads **no** human fibs, imports **no**
Genesis code, and makes **no** trading/edge claim.

Boundary held: **Fib = producer / contract authority; Genesis = future read-only
consumer.** Nothing here authorises a real export.

Two tables (Phase 1 §2):

- **Zone registry** (table A) — one row per causally-valid confluence zone. Carries the
  binding *zone-knowability* stamp ``known_after_ts``.
- **Bar feature table** (table B) — one row per ``(symbol, timeframe, timestamp)`` bar that
  Genesis would left-join against. Feature columns plus a **metadata-only** reference
  column (``meta_referenced_zone_ids``) that names every zone a row's values touch, so the
  per-row causality invariant is *observable* and not merely asserted.

Mechanically checked here (Phase 1 §5):

1. Column schema of both tables (exact header, fail-closed on drift).
2. Join keys ``(symbol, timeframe, timestamp)`` — present, non-null, **unique** (a
   duplicate triple would fan out a left join).
3. Causality: for every zone referenced by a bar row, ``known_after_ts <= timestamp``.
4. ``known_after_ts >= max(member.anchor_b) + confirmation_buffer_hours`` (the floor; "or
   stricter" is allowed). The buffer is **integer hours** — the column is named
   ``confirmation_buffer_hours`` to make the unit unambiguous (Phase 1 §2A left it unit-less
   as ``confirmation_buffer``; this dummy pins the unit).
5. No 1H — off-protocol timeframe rejected, fail-closed.
6. Feature / metadata boundary — no metadata column is ever a feature column.

Usage::

    python -m fibengine.research.feature_contract \\
        --zones docs/research_wiki/reviews/contracts/phase2_dummy/zone_registry.csv \\
        --bars  docs/research_wiki/reviews/contracts/phase2_dummy/bar_features.csv
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# --- Schema (Phase 1 §2) -------------------------------------------------------------

# Table A — zone registry. Exact column order is the contract.
ZONE_REGISTRY_FIELDS: tuple[str, ...] = (
    "zone_id",
    "symbol",
    "method",
    "epsilon_log",
    "zone_price_repr",
    "zone_price_min",
    "zone_price_max",
    "price_span_log",
    "tf_count",
    "level_count",
    "timeframes",
    "ratios",
    "anchor_a_min",
    "anchor_b_max",
    "known_after_ts",
    "confirmation_buffer_hours",
    "source_member_count",
    "feature_version",
)

# Table B — join keys (also the causality anchor) + version tag.
BAR_JOIN_KEYS: tuple[str, ...] = ("symbol", "timeframe", "timestamp")
BAR_VERSION_FIELDS: tuple[str, ...] = ("feature_version",)

# Table B — the actual model feature columns (Phase 1 §2B).
BAR_FEATURE_FIELDS: tuple[str, ...] = (
    "nearest_confluence_price",
    "nearest_confluence_distance_log",
    "nearest_confluence_distance_atr",
    "in_confluence_band",
    "nearest_zone_tf_count",
    "nearest_zone_level_count",
    "nearest_zone_price_span_log",
    "nearest_zone_age_bars",
    "nearest_zone_method",
    "num_zones_within_x_atr",
    "num_fixed_band_zones_active",
    "has_robust_4tf_zone_nearby",
)

# Table B — metadata-only columns. NEVER a model feature (Phase 1 §6, §8). The reference
# column makes invariant §5.1 observable: it names every zone a row's features touch.
BAR_META_FIELDS: tuple[str, ...] = ("meta_referenced_zone_ids",)

# Full table-B header, in order.
BAR_TABLE_FIELDS: tuple[str, ...] = (
    BAR_JOIN_KEYS + BAR_VERSION_FIELDS + BAR_FEATURE_FIELDS + BAR_META_FIELDS
)

# --- Controlled vocab ----------------------------------------------------------------

# Active protocol timeframes. 1H is off-protocol and fail-closed (Phase 1 §5.2).
ALLOWED_TIMEFRAMES: frozenset[str] = frozenset({"1M", "1w", "1d", "4h"})
METHODS: frozenset[str] = frozenset({"fixed_band", "single_linkage"})

# Mechanical feature/metadata boundary invariant (Phase 1 §8): the metadata reference
# column must never leak into the feature set or the join keys. Checked at import so a
# careless schema edit fails loudly rather than silently turning metadata into a feature.
assert not (set(BAR_META_FIELDS) & set(BAR_FEATURE_FIELDS)), "metadata column is a feature"
assert not (set(BAR_META_FIELDS) & set(BAR_JOIN_KEYS)), "metadata column is a join key"


def _parse_ts(value: str, *, field: str) -> datetime:
    """Parse a tz-aware ISO-8601 timestamp (``...Z`` accepted). Fail-closed on naive."""
    v = value.strip()
    if not v:
        raise ValueError(f"{field}: empty timestamp")
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(v)
    except ValueError as exc:
        raise ValueError(f"{field}: not ISO-8601 ({value!r})") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{field}: timestamp must be timezone-aware ({value!r})")
    return dt


def _parse_bool(value: str, *, field: str) -> bool:
    v = value.strip().lower()
    if v in {"true", "1"}:
        return True
    if v in {"false", "0"}:
        return False
    raise ValueError(f"{field}: not a bool ({value!r})")


def _parse_float(value: str, *, field: str) -> float | None:
    v = value.strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError as exc:
        raise ValueError(f"{field}: not a float ({value!r})") from exc


def _parse_int(value: str, *, field: str) -> int | None:
    v = value.strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError as exc:
        raise ValueError(f"{field}: not an int ({value!r})") from exc


@dataclass
class ZoneRow:
    """One causally-valid confluence zone (table A). Built via :meth:`from_row`."""

    zone_id: str
    symbol: str
    method: str
    epsilon_log: float
    zone_price_repr: float
    zone_price_min: float
    zone_price_max: float
    price_span_log: float
    tf_count: int
    level_count: int
    timeframes: tuple[str, ...]
    ratios: str
    anchor_a_min: datetime
    anchor_b_max: datetime
    known_after_ts: datetime
    confirmation_buffer_hours: int
    source_member_count: int
    feature_version: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> ZoneRow:
        zone_id = (row.get("zone_id") or "").strip()
        if not zone_id:
            raise ValueError("zone_id must be non-empty")
        method = (row.get("method") or "").strip()
        if method not in METHODS:
            raise ValueError(f"{zone_id}: invalid method {method!r}; allowed {sorted(METHODS)}")
        timeframes = tuple(t.strip() for t in (row.get("timeframes") or "").split(",") if t.strip())
        bad_tf = [t for t in timeframes if t not in ALLOWED_TIMEFRAMES]
        if bad_tf:
            raise ValueError(f"{zone_id}: off-protocol timeframe(s) {bad_tf} (no 1H)")
        return cls(
            zone_id=zone_id,
            symbol=(row.get("symbol") or "").strip(),
            method=method,
            epsilon_log=_parse_float(row["epsilon_log"], field=f"{zone_id}.epsilon_log") or 0.0,
            zone_price_repr=_parse_float(row["zone_price_repr"], field=f"{zone_id}.repr") or 0.0,
            zone_price_min=_parse_float(row["zone_price_min"], field=f"{zone_id}.min") or 0.0,
            zone_price_max=_parse_float(row["zone_price_max"], field=f"{zone_id}.max") or 0.0,
            price_span_log=_parse_float(row["price_span_log"], field=f"{zone_id}.span") or 0.0,
            tf_count=_parse_int(row["tf_count"], field=f"{zone_id}.tf_count") or 0,
            level_count=_parse_int(row["level_count"], field=f"{zone_id}.level_count") or 0,
            timeframes=timeframes,
            ratios=(row.get("ratios") or "").strip(),
            anchor_a_min=_parse_ts(row["anchor_a_min"], field=f"{zone_id}.anchor_a_min"),
            anchor_b_max=_parse_ts(row["anchor_b_max"], field=f"{zone_id}.anchor_b_max"),
            known_after_ts=_parse_ts(row["known_after_ts"], field=f"{zone_id}.known_after_ts"),
            confirmation_buffer_hours=_parse_int(
                row["confirmation_buffer_hours"], field=f"{zone_id}.confirmation_buffer_hours"
            )
            or 0,
            source_member_count=_parse_int(
                row["source_member_count"], field=f"{zone_id}.source_member_count"
            )
            or 0,
            feature_version=(row.get("feature_version") or "").strip(),
        ).validate()

    def validate(self) -> ZoneRow:
        """Fail-closed on structural / causal violations within the zone row."""
        if not self.symbol:
            raise ValueError(f"{self.zone_id}: symbol must be non-empty")
        if not 2 <= self.tf_count <= 4:
            raise ValueError(f"{self.zone_id}: tf_count {self.tf_count} not in 2..4")
        if len(set(self.timeframes)) != self.tf_count:
            raise ValueError(
                f"{self.zone_id}: tf_count {self.tf_count} != distinct timeframes {self.timeframes}"
            )
        if self.confirmation_buffer_hours < 0:
            raise ValueError(f"{self.zone_id}: negative confirmation_buffer_hours")
        if self.price_span_log < 0:
            raise ValueError(f"{self.zone_id}: negative price_span_log")
        if not self.zone_price_min <= self.zone_price_repr <= self.zone_price_max:
            raise ValueError(
                f"{self.zone_id}: price ordering min<=repr<=max violated "
                f"({self.zone_price_min}/{self.zone_price_repr}/{self.zone_price_max})"
            )
        # Zone-knowability rule (Phase 1 §2A): floor, "or stricter" allowed.
        floor = self.anchor_b_max + timedelta(hours=self.confirmation_buffer_hours)
        if self.known_after_ts < floor:
            raise ValueError(
                f"{self.zone_id}: known_after_ts {self.known_after_ts.isoformat()} earlier than "
                f"anchor_b_max+buffer {floor.isoformat()} (knowability rule violated)"
            )
        return self


@dataclass
class BarRow:
    """One bar feature row (table B). Built via :meth:`from_row`."""

    symbol: str
    timeframe: str
    timestamp: datetime
    timestamp_raw: str
    referenced_zone_ids: tuple[str, ...]
    feature_version: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> BarRow:
        symbol = (row.get("symbol") or "").strip()
        timeframe = (row.get("timeframe") or "").strip()
        ts_raw = (row.get("timestamp") or "").strip()
        if not symbol:
            raise ValueError("bar row: symbol (join key) must be non-empty")
        if timeframe not in ALLOWED_TIMEFRAMES:
            raise ValueError(f"bar row: off-protocol timeframe {timeframe!r} (no 1H)")
        if not ts_raw:
            raise ValueError("bar row: timestamp (join key) must be non-empty")
        timestamp = _parse_ts(ts_raw, field="bar.timestamp")
        refs = tuple(
            z.strip() for z in (row.get("meta_referenced_zone_ids") or "").split(";") if z.strip()
        )
        # Validate the declared feature columns parse to their types (fail-closed), but do
        # NOT recompute or assert their values — that would be feature export, out of scope.
        for fld in ("in_confluence_band", "has_robust_4tf_zone_nearby"):
            if (row.get(fld) or "").strip():
                _parse_bool(row[fld], field=f"bar.{fld}")
        for fld in BAR_FEATURE_FIELDS:
            if fld in {"in_confluence_band", "has_robust_4tf_zone_nearby", "nearest_zone_method"}:
                continue
            _parse_float(row.get(fld, ""), field=f"bar.{fld}")
        method = (row.get("nearest_zone_method") or "").strip()
        if method and method not in METHODS:
            raise ValueError(f"bar row: invalid nearest_zone_method {method!r}")
        return cls(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=timestamp,
            timestamp_raw=ts_raw,
            referenced_zone_ids=refs,
            feature_version=(row.get("feature_version") or "").strip(),
        )

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.symbol, self.timeframe, self.timestamp_raw)


def _read_csv(path: Path | str, header: tuple[str, ...]) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or tuple(reader.fieldnames) != header:
            raise ValueError(f"header {reader.fieldnames} != expected {list(header)}")
        return list(reader)


def read_zone_registry(path: Path | str) -> list[ZoneRow]:
    """Read + validate table A. Raises on header drift or any row violation."""
    return [ZoneRow.from_row(r) for r in _read_csv(path, ZONE_REGISTRY_FIELDS)]


def read_bar_features(path: Path | str) -> list[BarRow]:
    """Read + validate table B. Raises on header drift or any row violation."""
    return [BarRow.from_row(r) for r in _read_csv(path, BAR_TABLE_FIELDS)]


def check_join_keys(bars: list[BarRow]) -> list[str]:
    """Join keys must be unique (a duplicate triple fans out a left join)."""
    errors: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for bar in bars:
        if bar.key in seen:
            errors.append(f"duplicate join key {bar.key}")
        seen.add(bar.key)
    return errors


def check_causality(bars: list[BarRow], zones: list[ZoneRow]) -> list[str]:
    """Phase 1 §5.1: every zone a bar row references must satisfy known_after_ts <= ts."""
    errors: list[str] = []
    by_id = {z.zone_id: z for z in zones}
    for bar in bars:
        for zid in bar.referenced_zone_ids:
            zone = by_id.get(zid)
            if zone is None:
                errors.append(f"{bar.key}: references unknown zone_id {zid!r}")
                continue
            if zone.known_after_ts > bar.timestamp:
                errors.append(
                    f"{bar.key}: LEAKAGE — zone {zid} known_after_ts "
                    f"{zone.known_after_ts.isoformat()} > bar timestamp {bar.timestamp.isoformat()}"
                )
    return errors


def validate_contract(zones_path: Path | str, bars_path: Path | str) -> dict[str, object]:
    """Run the full contract check. Raises ``ValueError`` on any schema/causal violation.

    Returns a small summary dict on success (zone/bar counts, distinct timeframes).
    """
    zones = read_zone_registry(zones_path)
    bars = read_bar_features(bars_path)
    errors = check_join_keys(bars) + check_causality(bars, zones)
    if errors:
        raise ValueError("contract violations:\n" + "\n".join(f"  - {e}" for e in errors))
    return {
        "zones": len(zones),
        "bars": len(bars),
        "timeframes": sorted({b.timeframe for b in bars}),
        "feature_columns": list(BAR_FEATURE_FIELDS),
        "metadata_columns": list(BAR_META_FIELDS),
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate a Phase 2 dummy feature-contract pair.")
    p.add_argument("--zones", required=True, help="Path to the zone registry CSV (table A)")
    p.add_argument("--bars", required=True, help="Path to the bar feature CSV (table B)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    summary = validate_contract(args.zones, args.bars)
    print(
        f"contract OK: {summary['zones']} zone(s), {summary['bars']} bar(s); "
        f"timeframes={summary['timeframes']}"
    )
