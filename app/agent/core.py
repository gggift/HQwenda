from app.tools.registry import get_tool_schemas, execute_tool

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        from app.config import Settings

        settings = Settings()
        _client = OpenAI(
            api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url
        )
    return _client


def run_agent(
    system_prompt: str, messages: list[dict], max_iterations: int = 10
) -> str:
    from app.config import Settings

    settings = Settings()
    client = _get_client()
    tool_schemas = get_tool_schemas()

    all_messages = [{"role": "system", "content": system_prompt}] + messages

    for _ in range(max_iterations):
        kwargs = {
            "model": settings.deepseek_model,
            "messages": all_messages,
            "temperature": 0.3,
        }
        if tool_schemas:
            kwargs["tools"] = tool_schemas

        response = client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or ""

        # Append assistant message with tool calls
        all_messages.append(message.model_dump())

        # Execute each tool call and append results
        for tool_call in message.tool_calls:
            result = execute_tool(
                tool_call.function.name, tool_call.function.arguments
            )
            all_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    return "抱歉，处理超时，请稍后重试。"
