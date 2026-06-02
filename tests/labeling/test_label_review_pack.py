from fibengine.backtest.matrix import MatrixCase
from fibengine.labeling.review_pack import _case_slug


def test_case_slug_is_filesystem_friendly():
    assert _case_slug(MatrixCase("ETH/USD", "1h")) == "ETH-USD_1h"
