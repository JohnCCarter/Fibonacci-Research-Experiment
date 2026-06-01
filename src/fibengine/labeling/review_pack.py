"""Generate non-interactive chart packs for manual label review.

This prepares images and candidate metadata; it does not create manual labels.

Run:
    uv run python -m fibengine.labeling.review_pack
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from fibengine.backtest.matrix import MatrixCase, _case_settings
from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.scoring import select_swing
from fibengine.data.loader import load_candles
from fibengine.viz.plot import plot_prediction

REVIEW_PACKS_DIR = REPO_ROOT / "experiments" / "label_review" / "packs"
DEFAULT_REVIEW_CASES = (
    MatrixCase("ETH/USD", "1h"),
    MatrixCase("BTC/USD", "1h"),
    MatrixCase("SOL/USD", "15m"),
)


@dataclass(frozen=True)
class ReviewCandidate:
    exchange: str
    symbol: str
    timeframe: str
    chart_path: str
    candidate_swing: dict | None
    note: str


def _case_slug(case: MatrixCase) -> str:
    return f"{case.symbol.replace('/', '-')}_{case.timeframe}"


def build_review_pack(
    settings: Settings | None = None,
    cases: tuple[MatrixCase, ...] = DEFAULT_REVIEW_CASES,
) -> Path:
    """Create chart images and candidate metadata for human label review."""
    settings = settings or load_settings()
    run_id = datetime.now(UTC).strftime("label_review_%Y%m%dT%H%M%SZ")
    out_dir = REVIEW_PACKS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates: list[ReviewCandidate] = []
    for case in cases:
        case_settings = _case_settings(settings, case)
        df = load_candles(case_settings.data)
        swing = select_swing(df, case_settings.pivots, case_settings.scoring)
        slug = _case_slug(case)
        chart_path = out_dir / f"{slug}.png"
        if swing is not None:
            plot_prediction(
                df,
                swing,
                case_settings.fib.levels,
                chart_path,
                title=f"{case.symbol} {case.timeframe} candidate",
            )
            swing_payload = swing.to_dict()
            note = "Review visually. If accepted, recreate as a manual label."
        else:
            swing_payload = None
            note = "No candidate swing selected for this case."

        candidates.append(
            ReviewCandidate(
                exchange=case_settings.data.exchange,
                symbol=case.symbol,
                timeframe=case.timeframe,
                chart_path=str(chart_path),
                candidate_swing=swing_payload,
                note=note,
            )
        )

    payload = {
        "run_id": run_id,
        "created_at": datetime.now(UTC).isoformat(),
        "config_hash": settings.config_hash(),
        "labels_written": False,
        "instructions": [
            "Inspect each chart image.",
            "Use the candidate swing only as a suggestion, not as ground truth.",
            "Create manual labels with `uv run python -m fibengine.labeling.tool`.",
            "Then run `uv run python -m fibengine.evaluation.pivot_recall`.",
        ],
        "candidates": [asdict(candidate) for candidate in candidates],
    }
    (out_dir / "review_candidates.json").write_text(json.dumps(payload, indent=2))
    return out_dir


if __name__ == "__main__":
    print(build_review_pack())
