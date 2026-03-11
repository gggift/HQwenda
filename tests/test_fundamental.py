from unittest.mock import patch
import pandas as pd


def test_get_daily_basic():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301"],
            "ts_code": ["000001.SZ"],
            "pe": [8.5],
            "pb": [0.9],
            "ps": [1.2],
            "total_mv": [300000],
            "circ_mv": [280000],
        }
    )

    with patch("app.tools.fundamental._get_pro") as mock_pro:
        mock_pro.return_value.daily_basic.return_value = mock_df
        from app.tools.fundamental import get_daily_basic

        result = get_daily_basic(ts_code="000001.SZ")
        assert result["data"][0]["pe"] == 8.5


def test_get_financial_indicator():
    mock_df = pd.DataFrame(
        {
            "end_date": ["20231231"],
            "roe": [12.5],
            "roa": [1.2],
            "grossprofit_margin": [35.0],
            "netprofit_margin": [28.0],
        }
    )

    with patch("app.tools.fundamental._get_pro") as mock_pro:
        mock_pro.return_value.fina_indicator.return_value = mock_df
        from app.tools.fundamental import get_financial_indicator

        result = get_financial_indicator(ts_code="000001.SZ")
        assert result["data"][0]["roe"] == 12.5
