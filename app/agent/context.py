from app.agent.intent import recognize_intent
from app.knowledge.loader import KnowledgeLoader
from app.session.manager import SessionManager


def resolve_stock_name(name: str) -> str | None:
    """Try to resolve a stock name to its code using Tushare."""
    try:
        from app.tools.utils_tool import get_stock_basic

        result = get_stock_basic(name=name)
        if result.get("data"):
            return result["data"][0]["ts_code"]
    except Exception:
        pass
    return None


def assemble_context(
    message: str,
    session_id: str,
    session_manager: SessionManager,
    knowledge_loader: KnowledgeLoader,
) -> tuple[str, list[dict]]:
    # 1. Intent recognition
    intent = recognize_intent(message)

    # 2. Resolve stock names to codes
    stock_codes = {}
    for name in intent.get("entities", {}).get("stock_names", []):
        code = resolve_stock_name(name)
        if code:
            stock_codes[name] = code

    # 3. Knowledge retrieval
    keywords = intent.get("keywords", [])
    knowledge_docs = knowledge_loader.search(keywords)

    # 4. Build system prompt
    system_parts = [
        "你是一个专业的金融数据分析助手。用户会问你关于股票、指数等金融数据的问题。",
        "你可以调用工具获取实时数据来回答问题。回答要准确、简洁。",
        "当用户提到股票名称时，先用 get_stock_basic 工具查找股票代码，再用代码查询数据。",
    ]

    if stock_codes:
        codes_info = "、".join(f"{n}({c})" for n, c in stock_codes.items())
        system_parts.append(f"\n已识别的股票：{codes_info}")

    if knowledge_docs:
        system_parts.append("\n相关知识：")
        for doc in knowledge_docs:
            system_parts.append(f"\n### {doc.title}\n{doc.content}")

    system_prompt = "\n".join(system_parts)

    # 5. Conversation history + new message
    history = session_manager.get_history(session_id)
    messages = list(history) + [{"role": "user", "content": message}]

    return system_prompt, messages
