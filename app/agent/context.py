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
        "",
        "【核心规则】",
        "1. 你必须通过调用工具获取真实数据来回答问题。严禁编造、猜测或虚构任何数据。",
        "2. 如果工具返回无数据，尝试改用前一个交易日（如今天无数据则用昨天的日期重新调用）。",
        "3. 回答必须基于工具返回的实际数据，不得凭空生成数据表格或数字。",
        "4. 当用户提到股票名称时，先用 get_stock_basic 工具查找股票代码，再用代码查询数据。",
        "",
        "【回答要求】",
        "1. 回答要准确、完整。行业排名类问题应尽量列出全部数据（如31个一级行业），不要只列前几名。",
        "2. 涉及技术分析时，必须调用 get_moving_averages 工具获取均线数据，结合实际数据分析。",
        "3. 涉及量能/成交额时，必须调用 get_index_daily 或 get_daily_quotes 获取真实成交额数据。",
        "4. 涉及历史分位数时，必须调用 get_historical_percentile 工具计算，不得说\"待计算\"。",
        "5. 涉及资金流向时，调用 get_northbound_flow 或 get_moneyflow 获取真实数据。",
        "6. 涉及期货行情时，先调用 get_fut_mapping 获取当前主力合约代码，再用该代码调用 get_fut_daily。不要猜测合约代码。",
        "7. 如果某项数据确实无法获取，明确说明原因，不要用模拟数据替代。",
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
