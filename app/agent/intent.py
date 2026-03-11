import json

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        from app.config import Settings

        settings = Settings()
        _client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    return _client


INTENT_PROMPT = """你是一个金融问题分类器。分析用户问题，输出JSON：
{
  "category": "行情查询" | "概念解释" | "闲聊" | "其他",
  "entities": {
    "stock_names": ["提到的股票名称"],
    "time_range": "提到的时间范围或null",
    "indicators": ["提到的指标如PE、PB等"]
  },
  "keywords": ["用于知识库检索的关键词"]
}
只输出JSON，不要其他内容。"""

_FALLBACK = {
    "category": "其他",
    "entities": {"stock_names": [], "time_range": None, "indicators": []},
    "keywords": [],
}


def recognize_intent(message: str) -> dict:
    client = _get_client()
    from app.config import Settings
    settings = Settings()
    response = client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
        max_tokens=300,
    )
    content = response.choices[0].message.content or ""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return dict(_FALLBACK)
