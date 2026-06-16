"""Causal BTC/Fib behaviour event study (research-only, Lean Fib Research).

Tests whether price reacts measurably differently at causally-valid human-fib retracement
levels than at matched placebo levels and a naive causal-swing baseline. **Behaviour only —
no trading/edge claim, no Genesis touch, no 1H, no auto-fib, no label mutation.**

Pre-registration (frozen rules): docs/research_wiki/reviews/
btc-fib-behaviour-event-study-prereg-20260616.md

Run:
    uv run python -m fibengine.research.fib_behaviour_event_study \\
        --timeframes 1M,1w,1d,4h --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import glob
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import REPO_ROOT, load_settings
from fibengine.data.loader import atr, load_candles

# --- frozen constants (see prereg) ------------------------------------------------------------

ALLOWED_TIMEFRAMES = ("1M", "1w", "1d", "4h")  # 1H is rejected fail-closed
INTERIOR_RATIOS = (0.382, 0.5, 0.618, 0.786)  # fib set excludes 0.0/1.0 anchors
SEED = 20260616
HUMAN_FIB_ROOT = REPO_ROOT / "data" / "labels" / "human_fib" / "bitfinex" / "BTC-USD"
RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "fib_behaviour_event_study"

# per-TF frozen parameters: (horizons, primary_horizon, bar_seconds, level_active_bars)
_TF_PARAMS: dict[str, tuple[tuple[int, ...], int, int, int]] = {
    "4h": ((6, 18, 36), 18, 4 * 3600, 720),
    "1d": ((4, 12, 24), 12, 24 * 3600, 365),
    "1w": ((2, 4, 8), 4, 7 * 24 * 3600, 104),
    "1M": ((2, 3, 6), 3, 31 * 24 * 3600, 36),
}


@dataclass(frozen=True)
class EventStudyConfig:
    """Frozen knobs. None are tuned on the test window (prereg §3-§9)."""

    k_confirm: int = 1  # confirmation buffer in bars of the fib's own TF
    pivot_k: int = 3  # fractal swing half-width for the SWING baseline
    eps_atr: float = 0.25  # touch tolerance in ATR units
    react_eps: float = 0.5  # reject / close-through threshold in ATR units
    atr_period: int = 14
    train_frac: float = 0.70
    min_events: int = 30  # power floor per source per window
    n_perm: int = 5000
    seed: int = SEED


# --- causal helpers ---------------------------------------------------------------------------


def _parse_utc(iso: str) -> datetime:
    """ISO-8601 -> tz-aware UTC datetime; fail-closed on naive/missing tz."""
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        raise ValueError(f"naive anchor timestamp (no tz): {iso!r} — fail-closed")
    return dt.astimezone(UTC)


def _index_ns(df: pd.DataFrame) -> np.ndarray:
    """Bar timestamps as int64 UTC nanoseconds, robust to the index resolution (us/ns)."""
    return df.index.values.astype("datetime64[ns]").astype("int64")


@dataclass
class Level:
    known_after_ts: pd.Timestamp  # first time the level may be used
    price: float


def load_fib_levels(timeframe: str, cfg: EventStudyConfig) -> list[Level]:
    """Causal fib interior-retracement levels for a TF (prereg §3). Fail-closed if empty."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise ValueError(f"timeframe {timeframe!r} not allowed (1H is rejected fail-closed)")
    bar_secs = _TF_PARAMS[timeframe][2]
    buffer = timedelta(seconds=cfg.k_confirm * bar_secs)
    # Base human-fib JSON only. Exclude regenerable auto-candidate sidecars
    # (`*_events.json`) — they carry hindsight `auto_candidate` labels and must never be used.
    paths = [
        p
        for p in sorted(glob.glob(str(HUMAN_FIB_ROOT / timeframe / "fib_*.json")))
        if not p.endswith("_events.json")
    ]
    if not paths:
        raise ValueError(f"no source fibs found for {timeframe} under {HUMAN_FIB_ROOT}")
    levels: list[Level] = []
    for p in paths:
        if "_candidate" in Path(p).name:  # candidates are not facit — fail-closed
            raise ValueError(f"refusing non-human candidate fib: {p}")
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        if data.get("created_by") != "human":  # only human facit
            raise ValueError(f"refusing non-human fib (created_by != human): {p}")
        a_t = _parse_utc(data["anchor_a"]["time"])
        b_t = _parse_utc(data["anchor_b"]["time"])
        known = pd.Timestamp(max(a_t, b_t) + buffer)
        by_ratio = {round(float(lv["ratio"]), 3): float(lv["price"]) for lv in data["levels"]}
        for r in INTERIOR_RATIOS:
            price = by_ratio.get(r)
            if price is None or price <= 0:
                raise ValueError(f"fib {p} missing/invalid interior ratio {r}")
            levels.append(Level(known, price))
    return levels


def detect_swing_levels(df: pd.DataFrame, cfg: EventStudyConfig) -> list[Level]:
    """Causal fractal swing highs/lows: a static level knowable pivot_k bars after the pivot."""
    k = cfg.pivot_k
    highs, lows, idx = df["high"].to_numpy(), df["low"].to_numpy(), df.index
    n = len(df)
    levels: list[Level] = []
    for i in range(k, n - k):
        window_hi = highs[i - k : i + k + 1]
        window_lo = lows[i - k : i + k + 1]
        if highs[i] == window_hi.max() and (window_hi.argmax() == k):
            levels.append(Level(pd.Timestamp(idx[i + k]), float(highs[i])))
        if lows[i] == window_lo.min() and (window_lo.argmin() == k):
            levels.append(Level(pd.Timestamp(idx[i + k]), float(lows[i])))
    return levels


def make_placebo_levels(
    fib_levels: list[Level], df: pd.DataFrame, rng: np.random.Generator
) -> list[Level]:
    """Matched control: same count + same known_after_ts as fib, random price in the causal
    trailing log-range strictly before known_after_ts (prereg §4). Deterministic via rng."""
    highs, lows = df["high"].to_numpy(), df["low"].to_numpy()
    idx_ns = _index_ns(df)
    out: list[Level] = []
    for lv in fib_levels:
        prior = idx_ns < lv.known_after_ts.value
        if not prior.any():
            out.append(Level(lv.known_after_ts, float(df["close"].iloc[0])))
            continue
        lo = float(lows[prior].min())
        hi = float(highs[prior].max())
        lo, hi = max(lo, 1e-9), max(hi, 1e-9)
        log_price = rng.uniform(np.log(lo), np.log(hi))
        out.append(Level(lv.known_after_ts, float(np.exp(log_price))))
    return out


# --- event detection & outcomes ---------------------------------------------------------------


def _min_distance_series(
    df: pd.DataFrame, levels: list[Level], level_active_bars: int
) -> tuple[np.ndarray, np.ndarray]:
    """Per-bar nearest causally-active level: (min_distance, nearest_price). Distance is 0 when
    the level lies inside the bar's [low, high] range. Honours the recency window."""
    ts_ns = _index_ns(df)
    low, high = df["low"].to_numpy(), df["high"].to_numpy()
    n = len(df)
    mindist = np.full(n, np.inf)
    nearest = np.full(n, np.nan)
    if not levels:
        return mindist, nearest
    lv_sorted = sorted(levels, key=lambda x: x.known_after_ts)
    lv_known = np.array([x.known_after_ts.value for x in lv_sorted])  # UTC ns
    lv_price = np.array([x.price for x in lv_sorted])
    # expiry per level = known_after + level_active_bars * median bar spacing (in ns)
    bar_ns = int(np.median(np.diff(ts_ns))) if n > 1 else 0
    lv_expire = lv_known + level_active_bars * bar_ns
    for i in range(n):
        active = (lv_known <= ts_ns[i]) & (ts_ns[i] < lv_expire)
        if not active.any():
            continue
        prices = lv_price[active]
        dist = np.maximum.reduce([low[i] - prices, prices - high[i], np.zeros_like(prices)])
        j = int(dist.argmin())
        mindist[i] = float(dist[j])
        nearest[i] = float(prices[j])
    return mindist, nearest


@dataclass
class Event:
    pos: int  # bar integer position
    level: float
    approach_side: str  # "above" (support) or "below" (resistance)


def find_events(
    df: pd.DataFrame, atr_s: np.ndarray, levels: list[Level], cfg: EventStudyConfig, tf: str
) -> list[Event]:
    """Fresh touches of the nearest causally-active level (prereg §5). One event per bar max."""
    level_active_bars = _TF_PARAMS[tf][3]
    mindist, nearest = _min_distance_series(df, levels, level_active_bars)
    close = df["close"].to_numpy()
    n = len(df)
    tol = cfg.eps_atr * atr_s
    events: list[Event] = []
    for i in range(1, n):
        if not np.isfinite(mindist[i]) or np.isnan(atr_s[i]) or atr_s[i] <= 0:
            continue
        touch = mindist[i] <= tol[i]
        prev_fresh = (not np.isfinite(mindist[i - 1])) or (mindist[i - 1] > tol[i - 1])
        if not (touch and prev_fresh):
            continue
        lv = nearest[i]
        side = "above" if close[i - 1] >= lv else "below"
        events.append(Event(pos=i, level=float(lv), approach_side=side))
    return events


def event_reject(
    df: pd.DataFrame, atr_s: np.ndarray, ev: Event, horizon: int, react_eps: float
) -> dict[str, Any] | None:
    """Outcome metrics for one event at one horizon, or None if the horizon is unavailable."""
    n = len(df)
    i, end = ev.pos, ev.pos + horizon
    if end >= n:
        return None
    close, high, low = df["close"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy()
    a = atr_s[i]
    thr = react_eps * a
    fut_close = close[i + 1 : end + 1]
    fut_high = high[i + 1 : end + 1]
    fut_low = low[i + 1 : end + 1]
    if ev.approach_side == "above":  # support: reject = bounce up, close back above level
        reject = bool((fut_close >= ev.level + thr).any())
        through = bool((fut_close <= ev.level - thr).any())
        mfe = float((fut_high.max() - close[i]) / a)
        mae = float((close[i] - fut_low.min()) / a)
    else:  # resistance: reject = bounce down, close back below level
        reject = bool((fut_close <= ev.level - thr).any())
        through = bool((fut_close >= ev.level + thr).any())
        mfe = float((close[i] - fut_low.min()) / a)
        mae = float((fut_high.max() - close[i]) / a)
    abs_move = float(abs(close[end] - close[i]) / a)
    return {
        "reject": reject,
        "close_through": through,
        "abs_fwd_move_atr": abs_move,
        "mfe_atr": mfe,
        "mae_atr": mae,
    }


# --- windows & statistics ---------------------------------------------------------------------


def split_positions(n: int, train_frac: float, max_horizon: int) -> tuple[int, int]:
    """Return (split_idx, n). Train events need pos+max_h < split_idx; test pos >= split_idx."""
    return int(n * train_frac), n


def _window_of(pos: int, split_idx: int, n: int, max_h: int) -> str | None:
    if pos + max_h < split_idx:
        return "train"
    if pos >= split_idx and pos + max_h < n:
        return "test"
    return None  # embargo / insufficient horizon


def permutation_p(
    flags_a: list[bool], flags_b: list[bool], rng: np.random.Generator, n_perm: int
) -> float | None:
    """Two-sided permutation p-value for the difference in mean(flags) between A and B."""
    if not flags_a or not flags_b:
        return None
    a = np.asarray(flags_a, dtype=float)
    b = np.asarray(flags_b, dtype=float)
    obs = abs(a.mean() - b.mean())
    pooled = np.concatenate([a, b])
    na = len(a)
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(pooled)
        if abs(perm[:na].mean() - perm[na:].mean()) >= obs - 1e-12:
            count += 1
    return (count + 1) / (n_perm + 1)


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0, "reject_rate": None, "close_through_rate": None, "mean_abs_move_atr": None}
    rej = [r["reject"] for r in rows]
    thr = [r["close_through"] for r in rows]
    mov = [r["abs_fwd_move_atr"] for r in rows]
    return {
        "n": len(rows),
        "reject_rate": float(np.mean(rej)),
        "close_through_rate": float(np.mean(thr)),
        "mean_abs_move_atr": float(np.mean(mov)),
    }


# --- per-timeframe driver ---------------------------------------------------------------------


def _collect_rows(
    df: pd.DataFrame,
    atr_s: np.ndarray,
    events: list[Event],
    primary_h: int,
    max_h: int,
    split_idx: int,
    react_eps: float,
) -> dict[str, dict[str, Any]]:
    """Bucket events into train/test and compute primary-horizon outcomes."""
    n = len(df)
    out: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    for ev in events:
        win = _window_of(ev.pos, split_idx, n, max_h)
        if win is None:
            continue
        res = event_reject(df, atr_s, ev, primary_h, react_eps)
        if res is None:
            continue
        out[win].append(res)
    return {
        "train": _aggregate(out["train"]),
        "test": _aggregate(out["test"]),
        "_train_rows": out["train"],
        "_test_rows": out["test"],
    }


def run_timeframe(timeframe: str, cfg: EventStudyConfig, settings: Any) -> dict[str, Any]:
    """Run the event study for one timeframe; return aggregates, stats and the gate verdict."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise ValueError(f"timeframe {timeframe!r} not allowed (1H is rejected fail-closed)")
    horizons, primary_h, _, _ = _TF_PARAMS[timeframe]
    max_h = max(horizons)
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    atr_s = atr(df, period=cfg.atr_period).to_numpy()
    rng = np.random.default_rng(cfg.seed)

    fib_levels = load_fib_levels(timeframe, cfg)
    swing_levels = detect_swing_levels(df, cfg)
    placebo_levels = make_placebo_levels(fib_levels, df, rng)
    sources = {"fib": fib_levels, "swing": swing_levels, "placebo": placebo_levels}

    split_idx, n = split_positions(len(df), cfg.train_frac, max_h)
    per_source: dict[str, dict[str, Any]] = {}
    for name, levels in sources.items():
        events = find_events(df, atr_s, levels, cfg, timeframe)
        per_source[name] = _collect_rows(
            df, atr_s, events, primary_h, max_h, split_idx, cfg.react_eps
        )

    # permutation tests on test-window reject flags (fib vs each baseline)
    fib_test = [r["reject"] for r in per_source["fib"]["_test_rows"]]
    perm = {}
    for base in ("placebo", "swing"):
        base_test = [r["reject"] for r in per_source[base]["_test_rows"]]
        perm[base] = permutation_p(fib_test, base_test, rng, cfg.n_perm)

    gate = _gate(per_source, perm, cfg.min_events)
    summary = {
        "timeframe": timeframe,
        "n_bars": int(n),
        "primary_horizon": primary_h,
        "horizons": list(horizons),
        "n_fib_levels": len(fib_levels),
        "n_swing_levels": len(swing_levels),
        "n_placebo_levels": len(placebo_levels),
        "sources": {k: {"train": v["train"], "test": v["test"]} for k, v in per_source.items()},
        "permutation_p_test": perm,
        "gate": gate,
    }
    return summary


def _gate(
    per_source: dict[str, dict[str, Any]], perm: dict[str, float | None], min_events: int
) -> dict[str, Any]:
    """Pre-registered robustness gate (prereg §9). Returns booleans + overall pass."""
    checks: dict[str, Any] = {}
    n_ok = all(per_source[s]["test"]["n"] >= min_events for s in ("fib", "placebo", "swing"))
    checks["n_events_ge_min"] = n_ok

    def _beat(win: str, base: str) -> bool | None:
        f = per_source["fib"][win]["reject_rate"]
        b = per_source[base][win]["reject_rate"]
        if f is None or b is None:
            return None
        return f > b

    checks["fib_beats_placebo_test"] = _beat("test", "placebo")
    checks["fib_beats_swing_test"] = _beat("test", "swing")
    checks["fib_beats_placebo_train"] = _beat("train", "placebo")
    checks["fib_beats_swing_train"] = _beat("train", "swing")
    checks["perm_p_placebo"] = perm.get("placebo")
    checks["perm_p_swing"] = perm.get("swing")
    p_pl = perm.get("placebo")
    p_sw = perm.get("swing")
    sig = (p_pl is not None and p_pl < 0.05) and (p_sw is not None and p_sw < 0.05)
    checks["perm_significant"] = sig
    passed = bool(
        n_ok
        and checks["fib_beats_placebo_test"]
        and checks["fib_beats_swing_test"]
        and checks["fib_beats_placebo_train"]
        and checks["fib_beats_swing_train"]
        and sig
    )
    checks["robust_signal"] = passed
    return checks


def run_study(timeframes: list[str], config_path: str | None, cfg: EventStudyConfig) -> dict:
    settings = load_settings(config_path) if config_path else load_settings()
    results = [run_timeframe(tf, cfg, settings) for tf in timeframes]
    any_robust = any(r["gate"]["robust_signal"] for r in results)
    return {
        "generated_by": "fib_behaviour_event_study",
        "seed": cfg.seed,
        "timeframes": timeframes,
        "any_robust_signal": any_robust,
        "results": results,
    }


# --- CLI --------------------------------------------------------------------------------------


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Causal BTC/Fib behaviour event study")
    ap.add_argument("--timeframes", default="1M,1w,1d,4h")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR))
    args = ap.parse_args(argv)
    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    bad = [t for t in tfs if t not in ALLOWED_TIMEFRAMES]
    if bad:
        raise SystemExit(f"disallowed timeframe(s) {bad} (1H is rejected fail-closed)")
    report = run_study(tfs, args.config, EventStudyConfig())
    path = _write_summary(report, Path(args.out))
    for r in report["results"]:
        g = r["gate"]
        print(
            f"[{r['timeframe']}] fib_reject(test)="
            f"{r['sources']['fib']['test']['reject_rate']} "
            f"placebo={r['sources']['placebo']['test']['reject_rate']} "
            f"swing={r['sources']['swing']['test']['reject_rate']} "
            f"robust={g['robust_signal']}"
        )
    print(f"any_robust_signal={report['any_robust_signal']}  summary={path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
