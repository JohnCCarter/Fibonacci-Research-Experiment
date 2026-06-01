from fibengine.labeling.hover import _ohlc_line, format_price


def test_format_price_scales():
    assert format_price(116_400.5) == "116,400.50"
    assert format_price(1.2345) == "1.2345"
    assert format_price(0.00012) == "0.00012"


def test_ohlc_line_includes_bar_fields(synthetic_df):
    line = _ohlc_line(synthetic_df, 3)
    assert line.startswith("bar 3")
    assert "O " in line and "H " in line and "L " in line and "C " in line
