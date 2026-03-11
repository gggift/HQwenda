from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_daily_basic",
    description="获取股票每日基本指标，包括市盈率(PE)、市净率(PB)、市销率(PS)、总市值、流通市值等。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "股票代码，如 000001.SZ"},
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD（可选，默认最新）"},
            "start_date": {"type": "string", "description": "开始日期，格式 YYYYMMDD（可选）"},
            "end_date": {"type": "string", "description": "结束日期，格式 YYYYMMDD（可选）"},
        },
        "required": ["ts_code"],
    },
)
def get_daily_basic(ts_code: str, trade_date: str = None, start_date: str = None, end_date: str = None) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code, "fields": "trade_date,ts_code,pe,pb,ps,total_mv,circ_mv"}
    if trade_date:
        kwargs["trade_date"] = trade_date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    df = pro.daily_basic(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    return {"data": df.head(20).to_dict("records")}


@tool(
    name="get_financial_indicator",
    description="获取股票财务指标，包括ROE、ROA、毛利率、净利率等。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "股票代码，如 000001.SZ"},
            "period": {"type": "string", "description": "报告期，格式 YYYYMMDD，如 20231231（可选）"},
        },
        "required": ["ts_code"],
    },
)
def get_financial_indicator(ts_code: str, period: str = None) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code, "fields": "end_date,roe,roa,grossprofit_margin,netprofit_margin"}
    if period:
        kwargs["period"] = period
    df = pro.fina_indicator(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    return {"data": df.head(8).to_dict("records")}
