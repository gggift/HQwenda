from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_index_daily",
    description="获取指数日行情数据（如上证指数、深证成指、创业板指等）。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "指数代码，如 000001.SH（上证综指）、399001.SZ（深证成指）、399006.SZ（创业板指）"},
            "start_date": {"type": "string", "description": "开始日期，格式 YYYYMMDD（可选）"},
            "end_date": {"type": "string", "description": "结束日期，格式 YYYYMMDD（可选）"},
        },
        "required": ["ts_code"],
    },
)
def get_index_daily(ts_code: str, start_date: str = None, end_date: str = None) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    df = pro.index_daily(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    df = df.head(20)
    fields = ["trade_date", "open", "high", "low", "close", "vol", "pct_chg"]
    return {"data": df[fields].to_dict("records")}


@tool(
    name="get_index_weight",
    description="获取指数成分股及权重。",
    parameters={
        "type": "object",
        "properties": {
            "index_code": {"type": "string", "description": "指数代码，如 000300.SH（沪深300）"},
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD（可选，默认最新）"},
        },
        "required": ["index_code"],
    },
)
def get_index_weight(index_code: str, trade_date: str = None) -> dict:
    pro = _get_pro()
    kwargs = {"index_code": index_code}
    if trade_date:
        kwargs["trade_date"] = trade_date
    df = pro.index_weight(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["con_code", "con_name", "weight"] if c in df.columns]
    return {"data": df[fields].head(30).to_dict("records")}
