from unittest.mock import patch, MagicMock
import json


def test_recognize_intent_stock_query():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "category": "行情查询",
            "entities": {
                "stock_names": ["贵州茅台"],
                "time_range": "最近一周",
                "indicators": [],
            },
            "keywords": ["茅台", "行情"],
        }
    )

    with patch("app.agent.intent._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response
        from app.agent.intent import recognize_intent

        result = recognize_intent("贵州茅台最近一周的行情怎么样？")
        assert result["category"] == "行情查询"
        assert "贵州茅台" in result["entities"]["stock_names"]


def test_recognize_intent_invalid_json():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "这不是JSON"

    with patch("app.agent.intent._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response
        from app.agent.intent import recognize_intent

        result = recognize_intent("随便说点什么")
        assert result["category"] == "其他"
        assert result["entities"]["stock_names"] == []
