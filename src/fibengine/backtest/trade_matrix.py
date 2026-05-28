"""Run the simple Layer B trade simulation over the default real-market matrix.

Run:
    uv run python -m fibengine.backtest.trade_matrix
"""

from __future__ import annotations

import json

from fibengine.backtest.trade import run_trade_matrix

if __name__ == "__main__":
    print(json.dumps(run_trade_matrix(), indent=2))
