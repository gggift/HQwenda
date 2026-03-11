from unittest.mock import patch
import pandas as pd


def test_get_index_daily():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301"],
            "open": [3000.0],
            "high": [3050.0],
            "low": [2980.0],
            "close": [3020.0],
            "vol": [30000000],
            "pct_chg": [0.5],
        }
    )

    with patch("app.tools.index._get_pro") as mock_pro:
        mock_pro.return_value.index_daily.return_value = mock_df
        from app.tools.index import get_index_daily

        result = get_index_daily(ts_code="000001.SH")
        assert len(result["data"]) == 1
        assert result["data"][0]["close"] == 3020.0


def test_get_index_weight():
    mock_df = pd.DataFrame(
        {
            "con_code": ["600519.SH", "000858.SZ"],
            "con_name": ["贵州茅台", "五粮液"],
            "weight": [5.2, 2.1],
        }
    )

    with patch("app.tools.index._get_pro") as mock_pro:
        mock_pro.return_value.index_weight.return_value = mock_df
        from app.tools.index import get_index_weight

        result = get_index_weight(index_code="000300.SH")
        assert len(result["data"]) == 2
