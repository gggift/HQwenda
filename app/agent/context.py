import re
from datetime import date
from app.knowledge.loader import KnowledgeLoader
from app.session.manager import SessionManager

# Simple keyword extraction for knowledge search (no LLM needed)
_KNOWLEDGE_KEYWORDS = [
    "PE", "市盈率", "PB", "市净率", "ROE", "净资产收益率",
    "指数", "上证", "深证", "创业板", "沪深300",
    "均线", "估值", "交易规则",
]


def _extract_keywords(message: str) -> list[str]:
    """Extract knowledge-related keywords from message using simple matching."""
    return [kw for kw in _KNOWLEDGE_KEYWORDS if kw in message]


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
    # 1. Simple keyword extraction (no LLM call needed)
    keywords = _extract_keywords(message)
    knowledge_docs = knowledge_loader.search(keywords)

    # 2. Build system prompt
    today = date.today().strftime("%Y-%m-%d")
    today_compact = date.today().strftime("%Y%m%d")
    system_parts = [
        f"你是一个专业的金融数据分析助手。今天的日期是 {today}（工具调用时使用 {today_compact} 格式）。",
        "用户会问你关于股票、指数等金融数据的问题。",
        "你可以调用工具获取实时数据来回答问题。回答要准确、简洁。",
        "当用户提到股票名称时，先用 get_stock_basic 工具查找股票代码，再用代码查询数据。",
    ]

    if knowledge_docs:
        system_parts.append("\n相关知识：")
        for doc in knowledge_docs:
            system_parts.append(f"\n### {doc.title}\n{doc.content}")

    system_prompt = "\n".join(system_parts)

    # 3. Conversation history + new message
    history = session_manager.get_history(session_id)
    messages = list(history) + [{"role": "user", "content": message}]

    return system_prompt, messages
