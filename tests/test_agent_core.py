from unittest.mock import patch, MagicMock


def _make_text_response(text: str):
    msg = MagicMock()
    msg.tool_calls = None
    msg.content = text
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_tool_call_response(tool_name: str, arguments: str, call_id: str = "call_1"):
    tool_call = MagicMock()
    tool_call.id = call_id
    tool_call.function.name = tool_name
    tool_call.function.arguments = arguments

    msg = MagicMock()
    msg.tool_calls = [tool_call]
    msg.content = None
    msg.model_dump.return_value = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {"name": tool_name, "arguments": arguments},
            }
        ],
    }

    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def test_agent_simple_response():
    with patch("app.agent.core._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = _make_text_response(
            "你好！有什么可以帮你的吗？"
        )
        from app.agent.core import run_agent

        result = run_agent("你是助手", [{"role": "user", "content": "你好"}])
        assert result == "你好！有什么可以帮你的吗？"


def test_agent_with_tool_call():
    tool_response = _make_tool_call_response(
        "calculate_metric", '{"operation": "average", "values": [10, 20, 30]}'
    )
    final_response = _make_text_response("平均值是20。")

    with patch("app.agent.core._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.side_effect = [
            tool_response,
            final_response,
        ]
        with patch("app.agent.core.execute_tool", return_value='{"result": 20.0}'):
            from app.agent.core import run_agent

            result = run_agent("你是助手", [{"role": "user", "content": "计算10,20,30的平均值"}])
            assert result == "平均值是20。"


def test_agent_max_iterations():
    tool_response = _make_tool_call_response(
        "calculate_metric", '{"operation": "sum", "values": [1]}'
    )

    with patch("app.agent.core._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = tool_response
        with patch("app.agent.core.execute_tool", return_value='{"result": 1}'):
            from app.agent.core import run_agent

            result = run_agent(
                "你是助手",
                [{"role": "user", "content": "test"}],
                max_iterations=2,
            )
            assert "超时" in result or "重试" in result
