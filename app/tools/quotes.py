import tushare as ts
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro

QUOTE_FIELDS = ["trade_date", "open", "high", "low", "close", "vol", "pct_chg"]


@tool(
    name="get_daily_quotes",
    description="获取股票日K线数据，包括开盘价、最高价、最低价、收盘价、成交量、涨跌幅。默认返回最近20个交易日。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD（可选）",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD（可选）",
            },
        },
        "required": ["ts_code"],
    },
)
def get_daily_quotes(
    ts_code: str, start_date: str = None, end_date: str = None
) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    df = pro.daily(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    df = df.head(20)
    return {"data": df[QUOTE_FIELDS].to_dict("records")}


@tool(
    name="get_weekly_monthly",
    description="获取股票周K线或月K线数据。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
            "freq": {
                "type": "string",
                "description": "频率：weekly（周K）或 monthly（月K）",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD（可选）",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD（可选）",
            },
        },
        "required": ["ts_code", "freq"],
    },
)
def get_weekly_monthly(
    ts_code: str, freq: str = "weekly", start_date: str = None, end_date: str = None
) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date

    if freq == "monthly":
        df = pro.monthly(**kwargs)
    else:
        df = pro.weekly(**kwargs)

    if df.empty:
        return {"data": [], "message": "无数据"}
    df = df.head(20)
    return {"data": df[QUOTE_FIELDS].to_dict("records")}


@tool(
    name="get_realtime_quote",
    description="获取股票最新实时行情，包括当前价格、开盘价、最高价、最低价、成交量等。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
        },
        "required": ["ts_code"],
    },
)
def get_realtime_quote(ts_code: str) -> dict:
    df = ts.realtime_quote(ts_code=ts_code)
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["ts_code", "name", "open", "pre_close", "price", "high", "low", "vol", "amount"] if c in df.columns]
    return {"data": df[fields].to_dict("records")}
