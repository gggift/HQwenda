from unittest.mock import patch, MagicMock
import pandas as pd


def test_get_stock_basic_by_name():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ"],
            "name": ["平安银行"],
            "industry": ["银行"],
            "list_date": ["19910403"],
        }
    )

    with patch("app.tools.utils_tool._get_pro") as mock_pro:
        mock_pro.return_value.stock_basic.return_value = mock_df
        from app.tools.utils_tool import get_stock_basic

        result = get_stock_basic(name="平安银行")
        assert result["data"][0]["ts_code"] == "000001.SZ"
        assert result["data"][0]["name"] == "平安银行"


def test_get_stock_basic_by_code():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["600519.SH"],
            "name": ["贵州茅台"],
            "industry": ["白酒"],
            "list_date": ["20010827"],
        }
    )

    with patch("app.tools.utils_tool._get_pro") as mock_pro:
        mock_pro.return_value.stock_basic.return_value = mock_df
        from app.tools.utils_tool import get_stock_basic

        result = get_stock_basic(ts_code="600519.SH")
        assert result["data"][0]["name"] == "贵州茅台"


def test_get_trade_calendar():
    mock_df = pd.DataFrame(
        {
            "cal_date": ["20240101", "20240102", "20240103"],
            "is_open": [0, 1, 1],
        }
    )

    with patch("app.tools.utils_tool._get_pro") as mock_pro:
        mock_pro.return_value.trade_cal.return_value = mock_df
        from app.tools.utils_tool import get_trade_calendar

        result = get_trade_calendar(start_date="20240101", end_date="20240103")
        assert len(result["data"]) == 3


def test_calculate_metric_pct_change():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(
        operation="pct_change", values=[100, 110]
    )
    assert result["result"] == 10.0


def test_calculate_metric_average():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="average", values=[10, 20, 30])
    assert result["result"] == 20.0


def test_calculate_metric_max():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="max", values=[5, 15, 10])
    assert result["result"] == 15


def test_calculate_metric_min():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="min", values=[5, 15, 10])
    assert result["result"] == 5


def test_calculate_metric_unknown():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="unknown_op", values=[1, 2])
    assert "error" in result
