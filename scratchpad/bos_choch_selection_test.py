"""BOS/CHoCH structure-context as a SELECTION signal (descriptive, EXPLORATORY, nothing locked).

Question: do Chamoun's M/W/D origins sit on STRUCTURE-DEFINING swings — reversal (CHoCH) or
continuation (BOS) — more than random swings of the same kind?

Design (per advisor, 2026-07-01):
  A. Null universe = SMC swings (NOT repo detect_pivots) so the coincidence rate is not a
     detector-mismatch artifact (the DC lesson). Observed = fraction of his swing-origins that carry
     a CHoCH / BOS label; null = fraction of RANDOM same-kind SMC swings that carry it.
  B. Scope to the swing-origin subset. ~half his origins are continuation-mode (not swings) → the
     test is SILENT on them. Report usable N + the excluded count explicitly.
  C. Split CHoCH (reversal) vs BOS (continuation) — that is the only cut prominence/DC don't already
     answer. Never pool them.
  D. Underpowered: n~10-12 pooled, split halves it → DESCRIPTIVE pattern-noting, not a powered
     verdict. swing_length LOCKED before measuring (=3, the repo pivots.lookback; =5 pre-declared
     robustness echo). Expect DC-style p fragility.

Direction (advisor): a down-origin "1" is the swing HIGH that LAUNCHES the fall (leg-start extreme),
not the bar that breaks. Each swing extreme is labeled by the character of the leg it launches.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20260701
B = 20000
SNAP_TOL = 1  # bars: absorb transcription + price-snap noise when testing swing-membership
SWING_LENGTHS = [3, 5]  # 3 = locked primary (= repo pivots.lookback); 5 = robustness echo
CACHE = {
    "1M": "data/raw/bitfinex/BTC-USD/1M/limit_500.csv",
    "1w": "data/raw/bitfinex/BTC-USD/1w/limit_1000.csv",
    "1d": "data/raw/bitfinex/BTC-USD/1d/limit_3500.csv",
}
WIN_DAYS = {"1M": 130, "1w": 45, "1d": 30}

# (tf, tag, direction, origin_price, approx_origin_date) — same 20 as newfacit_topdown.py
FIBS = [
    ("1M", "M1", "up", 9882.0, "2020-09-01"),
    ("1M", "M2", "down", 47600.0, "2022-04-01"),
    ("1M", "M3", "up", 52756.0, "2024-09-01"),
    ("1M", "M4", "up", 888.2, "2017-03-01"),
    ("1w", "W1", "down", 97850.0, "2026-01-05"),
    ("1w", "W2", "down", 116500.0, "2025-10-06"),
    ("1w", "W3", "up", 58943.0, "2024-09-30"),
    ("1w", "W4", "up", 16584.0, "2022-11-14"),
    ("1w", "W5", "up", 29313.0, "2021-07-19"),
    ("1w", "W6", "up", 1923.2, "2017-07-17"),
    ("1w", "W7", "down", 19891.0, "2017-12-11"),
    ("1d", "D1", "down", 90600.0, "2026-01-25"),
    ("1d", "D2", "down", 107500.0, "2025-10-28"),
    ("1d", "D3", "down", 126110.0, "2025-10-06"),
    ("1d", "D4", "up", 107630.0, "2025-06-22"),
    ("1d", "D5", "down", 39850.0, "2022-04-28"),
    ("1d", "D6", "down", 31775.0, "2022-06-06"),
    ("1d", "D7", "up", 2610.0, "2017-07-16"),
    ("1d", "D8", "down", 6485.8, "2018-11-14"),
    ("1d", "D9", "up", 21884.0, "2020-12-21"),
]


def swing_highs_lows(high, low, n):
    """Fractal swings: bar i is a swing high if high[i] is the strict max over [i-n, i+n]
    (symmetric for lows), then enforce alternation keeping the more extreme of any same-kind run.
    Returns an ordered list of (idx, price, kind)."""
    npts = len(high)
    raw = []
    for i in range(n, npts - n):
        if (
            high[i] == high[i - n : i + n + 1].max()
            and (high[i] > high[i - n : i]).all()
            and (high[i] > high[i + 1 : i + n + 1]).all()
        ):
            raw.append((i, high[i], "high"))
        elif (
            low[i] == low[i - n : i + n + 1].min()
            and (low[i] < low[i - n : i]).all()
            and (low[i] < low[i + 1 : i + n + 1]).all()
        ):
            raw.append((i, low[i], "low"))
    # enforce alternation: within a same-kind run keep the extreme
    alt = []
    for s in raw:
        if not alt or alt[-1][2] != s[2]:
            alt.append(s)
        else:
            keep_new = s[1] > alt[-1][1] if s[2] == "high" else s[1] < alt[-1][1]
            if keep_new:
                alt[-1] = s
    return alt


def label_swings(swings):
    """Label each swing EXTREME by the character of the leg it launches, mapped to Chamoun's origin.
    Needs the 4-swing window S[p-2..p+1]. Returns dict idx -> label in {choch, bos, none}.
    - swing HIGH launches a down-leg (his down-origin): break = next low < prior low.
        reversal (was higher-high) -> CHoCH bearish ; continuation (lower-high) -> BOS bearish.
    - swing LOW launches an up-leg (his up-origin): break = next high > prior high.
        reversal (was lower-low) -> CHoCH bullish ; continuation (higher-low) -> BOS bullish.
    """
    lab = {}
    for p in range(2, len(swings) - 1):
        idx, price, kind = swings[p]
        prev_opp = swings[p - 1][1]  # opposite-kind swing before
        next_opp = swings[p + 1][1]  # opposite-kind swing after (the launched leg's terminus)
        prev_same = swings[p - 2][1]  # same-kind swing two back
        if kind == "high":
            broke = next_opp < prev_opp  # down-leg breaks prior low
            reversal = price > prev_same  # this high was a higher-high (prior uptrend)
        else:
            broke = next_opp > prev_opp  # up-leg breaks prior high
            reversal = price < prev_same  # this low was a lower-low (prior downtrend)
        if not broke:
            lab[idx] = "none"
        else:
            lab[idx] = "choch" if reversal else "bos"
    return lab


CTX = {}
for tf, path in CACHE.items():
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    CTX[tf] = {"df": df, "high": high, "low": low}


def build(tf, n):
    c = CTX[tf]
    swings = swing_highs_lows(c["high"], c["low"], n)
    lab = label_swings(swings)
    by_kind = {"high": {}, "low": {}}  # idx -> label, only labeled swings
    for idx, _price, kind in swings:
        if idx in lab:
            by_kind[kind][idx] = lab[idx]
    return by_kind


def snap_origins(tf):
    """Snap Chamoun's origins for this tf to a bar index by price; return list of (kind, j)."""
    df = CTX[tf]["df"]
    out = []
    for ftf, tag, direc, oprice, adate in FIBS:
        if ftf != tf:
            continue
        t0 = pd.Timestamp(adate, tz="UTC")
        w = (df.index >= t0 - pd.Timedelta(days=WIN_DAYS[tf])) & (
            df.index <= t0 + pd.Timedelta(days=WIN_DAYS[tf])
        )
        widx = np.where(w)[0]
        kind = "high" if direc == "down" else "low"
        col = "high" if direc == "down" else "low"
        arr = df[col].to_numpy()[widx]
        j = int(widx[np.argmin(np.abs(arr - oprice))])
        out.append((tag, kind, j))
    return out


def nearest_labeled(by_kind_map, kind, j):
    """If a labeled swing of `kind` is within +/-SNAP_TOL of bar j, return its label; else None."""
    best = None
    bestd = SNAP_TOL + 1
    for idx, label in by_kind_map[kind].items():
        d = abs(idx - j)
        if d <= SNAP_TOL and d < bestd:
            best, bestd = label, d
    return best


rng = np.random.default_rng(SEED)


def _perm(draw_cells, pools, obs_rate, pred):
    """Permutation p for a rate: draw one matched-(tf,kind) label per cell from pools, apply pred,
    measure the rate; p = P(null rate >= observed)."""
    if not draw_cells or any(len(pools[c]) == 0 for c in draw_cells):
        return None, None
    null = np.zeros(B)
    for b in range(B):
        hit = 0
        for cell in draw_cells:
            lab = pools[cell][rng.integers(len(pools[cell]))]
            hit += pred(lab)
        null[b] = hit / len(draw_cells)
    p = (np.sum(null >= obs_rate) + 1) / (B + 1)
    return p, null.mean()


def run(tfs, n, label):
    """Descriptive permutations at swing_length n. Two tests:
    (1) UNCONDITIONAL break-rate vs random SMC swings. ~definitional (a fib origin launches a
        structure-breaking move by construction) → NOT the selection question.
    (2) CONDITIONAL on breaking: bos-vs-choch split vs random BREAKING swings. Removes the
        definitional component → the actual continuation-vs-reversal selection question.
    """
    swing_origins = []  # (tf, kind, label) for each origin that IS a labeled swing
    n_origins = {"high": 0, "low": 0}
    pool_all = {}  # (tf,kind) -> all labeled-swing labels ; pool_brk -> breaking-only labels
    pool_brk = {}
    for tf in tfs:
        bk = build(tf, n)
        for kind in ("high", "low"):
            labs = list(bk[kind].values())
            pool_all[(tf, kind)] = labs
            pool_brk[(tf, kind)] = [x for x in labs if x in ("bos", "choch")]
        for _tag, kind, j in snap_origins(tf):
            n_origins[kind] += 1
            lab = nearest_labeled(bk, kind, j)
            if lab is not None:
                swing_origins.append((tf, kind, lab))
    tot_orig = n_origins["high"] + n_origins["low"]
    tot_swing = len(swing_origins)
    obs_bos = sum(1 for _, _, x in swing_origins if x == "bos")
    obs_choch = sum(1 for _, _, x in swing_origins if x == "choch")
    print(f"  [{label}  swing_length={n}]")
    print(
        f"    usable: {tot_swing}/{tot_orig} origins ARE labeled swings "
        f"(excluded non-swing/continuation-mode: {tot_orig - tot_swing})"
    )
    if tot_swing == 0:
        print("    no swing-origins — nothing to test\n")
        return

    # (1) UNCONDITIONAL — break-rate driven, ~definitional (report but do NOT read as selection).
    cells_all = [(tf, kind) for tf, kind, _ in swing_origins]
    obs_break = obs_bos + obs_choch
    brk_rate = obs_break / tot_swing
    p_brk, nm_brk = _perm(cells_all, pool_all, brk_rate, lambda x: x in ("bos", "choch"))
    print(
        f"    [~definitional] BREAKS structure: obs {obs_break}/{tot_swing}={brk_rate:.0%}"
        f"  null {nm_brk:.0%}  p={p_brk:.4f}   (a fib origin launches a move by construction)"
    )

    # (2) CONDITIONAL on breaking — the real continuation-vs-reversal selection question.
    brk_origins = [(tf, kind) for tf, kind, x in swing_origins if x in ("bos", "choch")]
    if obs_break == 0:
        print("    no breaking swing-origins — conditional test empty\n")
        return
    obs_bos_cond = obs_bos / obs_break
    p_cond, nm_cond = _perm(brk_origins, pool_brk, obs_bos_cond, lambda x: x == "bos")
    cc = "***" if (p_cond is not None and p_cond < 0.05) else ""
    pc_str = f"{p_cond:.4f}" if p_cond is not None else "n/a (empty breaking pool)"
    print(
        f"    [SELECTION] BOS|broke: obs {obs_bos}/{obs_break}={obs_bos_cond:.0%}"
        f"  null {nm_cond if nm_cond is not None else float('nan'):.0%}  p={pc_str}  {cc}"
    )
    print()


print(f"BOS/CHoCH selection test  B={B}  seed={SEED}  snap_tol=+/-{SNAP_TOL} bars")
print("DESCRIPTIVE / underpowered — split CHoCH vs BOS; null drawn from SMC swings (Design A)\n")
for n in SWING_LENGTHS:
    run(["1M"], n, "Monthly  ")
    run(["1w"], n, "Weekly   ")
    run(["1d"], n, "Daily    ")
    run(["1w", "1d"], n, "Pooled WD")
    print("  " + "-" * 60)
