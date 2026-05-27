from fibengine.config import PivotConfig
from fibengine.pivots.detect import detect_pivots


def test_detects_alternating_pivots(synthetic_df):
    cfg = PivotConfig(lookback=5, atr_period=14, min_prominence_atr=0.3)
    pivots = detect_pivots(synthetic_df, cfg)

    assert len(pivots) >= 2
    # Pivots ska vara sorterade i tid och alternera high/low.
    kinds = [p.kind for p in pivots]
    for a, b in zip(kinds, kinds[1:], strict=False):
        assert a != b
    assert [p.index for p in pivots] == sorted(p.index for p in pivots)


def test_finds_major_high_and_low(synthetic_df):
    cfg = PivotConfig(lookback=5, atr_period=14, min_prominence_atr=0.3)
    pivots = detect_pivots(synthetic_df, cfg)

    highs = [p for p in pivots if p.kind == "high"]
    lows = [p for p in pivots if p.kind == "low"]
    assert highs and lows
    # Toppen runt bar 60 (pris ~130) ska finnas med.
    assert max(p.price for p in highs) > 128
