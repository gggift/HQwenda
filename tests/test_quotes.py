from unittest.mock import patch
import pandas as pd


def test_get_daily_quotes():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301", "20240304"],
            "open": [10.0, 10.5],
            "high": [10.8, 11.0],
            "low": [9.8, 10.2],
            "close": [10.5, 10.8],
            "vol": [100000, 120000],
            "amount": [5000000, 6000000],
            "pct_chg": [1.5, 2.86],
        }
    )

    with patch("app.tools.quotes._get_pro") as mock_pro:
        mock_pro.return_value.daily.return_value = mock_df
        from app.tools.quotes import get_daily_quotes

        result = get_daily_quotes(ts_code="000001.SZ", start_date="20240301", end_date="20240304")
        assert len(result["data"]) == 2
        assert result["data"][0]["close"] == 10.5


def test_get_daily_quotes_empty():
    with patch("app.tools.quotes._get_pro") as mock_pro:
        mock_pro.return_value.daily.return_value = pd.DataFrame()
        from app.tools.quotes import get_daily_quotes

        result = get_daily_quotes(ts_code="000001.SZ")
        assert result["data"] == []


def test_get_weekly_monthly():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301"],
            "open": [10.0],
            "high": [11.0],
            "low": [9.5],
            "close": [10.8],
            "vol": [500000],
            "amount": [2500000],
            "pct_chg": [3.0],
        }
    )

    with patch("app.tools.quotes._get_pro") as mock_pro:
        mock_pro.return_value.weekly.return_value = mock_df
        from app.tools.quotes import get_weekly_monthly

        result = get_weekly_monthly(ts_code="000001.SZ", freq="weekly")
        assert len(result["data"]) == 1


def test_get_realtime_quote():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ"],
            "name": ["平安银行"],
            "open": [10.0],
            "pre_close": [9.8],
            "price": [10.5],
            "high": [10.8],
            "low": [9.9],
            "vol": [50000],
            "amount": [52000],
        }
    )

    with patch("app.tools.quotes.ts") as mock_ts:
        mock_ts.realtime_quote.return_value = mock_df
        from app.tools.quotes import get_realtime_quote

        result = get_realtime_quote(ts_code="000001.SZ")
        assert result["data"][0]["price"] == 10.5
