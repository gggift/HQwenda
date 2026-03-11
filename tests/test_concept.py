from unittest.mock import patch
import pandas as pd


def test_get_concept_list():
    mock_df = pd.DataFrame({"code": ["TS001", "TS002"], "name": ["人工智能", "新能源"]})

    with patch("app.tools.concept._get_pro") as mock_pro:
        mock_pro.return_value.concept.return_value = mock_df
        from app.tools.concept import get_concept_list

        result = get_concept_list()
        assert len(result["data"]) == 2


def test_get_concept_stocks():
    mock_df = pd.DataFrame({"ts_code": ["000001.SZ", "600000.SH"], "name": ["平安银行", "浦发银行"]})

    with patch("app.tools.concept._get_pro") as mock_pro:
        mock_pro.return_value.concept_detail.return_value = mock_df
        from app.tools.concept import get_concept_stocks

        result = get_concept_stocks(concept_id="TS001")
        assert len(result["data"]) == 2


def test_get_stock_concepts():
    mock_df = pd.DataFrame({
        "id": ["TS001", "TS002"],
        "concept_name": ["人工智能", "大数据"],
        "ts_code": ["000001.SZ", "000001.SZ"],
    })

    with patch("app.tools.concept._get_pro") as mock_pro:
        mock_pro.return_value.concept_detail.return_value = mock_df
        from app.tools.concept import get_stock_concepts

        result = get_stock_concepts(ts_code="000001.SZ")
        assert len(result["data"]) == 2
        assert result["data"][0]["concept_name"] == "人工智能"
