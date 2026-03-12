from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_daily_basic",
    description="获取单只股票每日基本指标，包括市盈率(PE)、市净率(PB)、市销率(PS)、总市值、流通市值、换手率(turnover_rate)、股息率(dv_ratio)等。查询单只股票时使用此工具。",
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
    kwargs = {"ts_code": ts_code, "fields": "trade_date,ts_code,pe,pb,ps,total_mv,circ_mv,turnover_rate,dv_ratio"}
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
    name="get_market_rank",
    description="全市场股票排名工具，可按总市值(total_mv)、流通市值(circ_mv)、市盈率(pe)、市净率(pb)、换手率(turnover_rate)、股息率(dv_ratio)、成交额(amount)等指标排名，返回前N名。适用于'市值最大的股票'、'换手率最高的股票'、'股息率最高的股票'、'成交额最大的股票'等问题。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD"},
            "sort_by": {"type": "string", "description": "排序字段：total_mv(总市值)、circ_mv(流通市值)、pe(市盈率)、pb(市净率)、turnover_rate(换手率)、dv_ratio(股息率)、amount(成交额)"},
            "ascending": {"type": "boolean", "description": "是否升序排列，默认 false（降序，即最大的在前）"},
            "top_n": {"type": "integer", "description": "返回前N名，默认 10"},
        },
        "required": ["trade_date", "sort_by"],
    },
)
def get_market_rank(trade_date: str, sort_by: str, ascending: bool = False, top_n: int = 10) -> dict:
    pro = _get_pro()
    valid_fields = {"total_mv", "circ_mv", "pe", "pb", "turnover_rate", "dv_ratio", "ps", "amount"}
    if sort_by not in valid_fields:
        return {"data": [], "message": f"不支持的排序字段: {sort_by}，可选: {', '.join(valid_fields)}"}

    from datetime import datetime, timedelta

    df = pro.daily_basic(trade_date=trade_date, fields="ts_code,trade_date,pe,pb,ps,total_mv,circ_mv,turnover_rate,dv_ratio")
    if df.empty:
        # Fallback: try recent trading days
        dt = datetime.strptime(trade_date, "%Y%m%d")
        for i in range(1, 5):
            prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
            df = pro.daily_basic(trade_date=prev, fields="ts_code,trade_date,pe,pb,ps,total_mv,circ_mv,turnover_rate,dv_ratio")
            if not df.empty:
                trade_date = prev
                break
    if df.empty:
        return {"data": [], "message": "无数据"}

    # If sorting by amount, merge daily data
    if sort_by == "amount":
        daily_df = pro.daily(trade_date=trade_date, fields="ts_code,amount")
        if not daily_df.empty:
            daily_df["amount"] = (daily_df["amount"] / 1e5).round(2)  # 千元 -> 亿元
            df = df.merge(daily_df[["ts_code", "amount"]], on="ts_code", how="inner")

    # Get stock names
    stock_df = pro.stock_basic(list_status='L', fields='ts_code,name')
    if not stock_df.empty:
        name_map = stock_df.set_index('ts_code')['name'].to_dict()
        df['name'] = df['ts_code'].map(name_map)

    # Filter out NaN for sort field, then sort
    df = df.dropna(subset=[sort_by])
    df = df.sort_values(sort_by, ascending=ascending).head(top_n)

    # Convert market value from 万元 to 亿元
    for col in ['total_mv', 'circ_mv']:
        if col in df.columns:
            df[col] = (df[col] / 10000).round(2)

    fields = ['ts_code', 'name', 'trade_date', sort_by]
    if sort_by not in ('total_mv', 'circ_mv'):
        fields.extend(['total_mv', 'circ_mv'])
    fields = [f for f in fields if f in df.columns]
    # deduplicate while preserving order
    seen = set()
    fields = [f for f in fields if not (f in seen or seen.add(f))]

    return {
        "data": df[fields].to_dict("records"),
        "note": "total_mv=总市值(亿元), circ_mv=流通市值(亿元), pe=市盈率, pb=市净率, turnover_rate=换手率(%), dv_ratio=股息率(%), amount=成交额(亿元)",
    }


@tool(
    name="get_financial_indicator",
    description="获取股票财务指标，包括ROE、ROA、毛利率、净利率、每股收益(EPS)等。",
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
    kwargs = {"ts_code": ts_code, "fields": "end_date,roe,roa,grossprofit_margin,netprofit_margin,eps"}
    if period:
        kwargs["period"] = period
    df = pro.fina_indicator(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    return {"data": df.head(8).to_dict("records")}
