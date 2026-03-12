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
    description="全市场股票排名工具，可按涨跌幅(pct_chg)、总市值(total_mv)、流通市值(circ_mv)、市盈率(pe)、市净率(pb)、换手率(turnover_rate)、股息率(dv_ratio)、成交额(amount)等指标排名，返回前N名。适用于'涨幅最大的股票'、'跌幅最大的股票'、'市值最大的股票'、'换手率最高的股票'、'成交额最大的股票'等问题。支持多日累计涨跌幅排名。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD"},
            "sort_by": {"type": "string", "description": "排序字段：pct_chg(涨跌幅)、total_mv(总市值)、circ_mv(流通市值)、pe(市盈率)、pb(市净率)、turnover_rate(换手率)、dv_ratio(股息率)、amount(成交额)"},
            "ascending": {"type": "boolean", "description": "是否升序排列，默认 false（降序，即最大的在前）。查涨幅前N用false，查跌幅前N用true"},
            "top_n": {"type": "integer", "description": "返回前N名，默认 10"},
            "days": {"type": "integer", "description": "累计天数，默认1（当日）。如查'近两日涨跌幅'则传2，'近5日'传5。仅对pct_chg和amount有效"},
        },
        "required": ["trade_date", "sort_by"],
    },
)
def get_market_rank(trade_date: str, sort_by: str, ascending: bool = False, top_n: int = 10, days: int = 1) -> dict:
    pro = _get_pro()
    valid_fields = {"total_mv", "circ_mv", "pe", "pb", "turnover_rate", "dv_ratio", "ps", "amount", "pct_chg"}
    if sort_by not in valid_fields:
        return {"data": [], "message": f"不支持的排序字段: {sort_by}，可选: {', '.join(valid_fields)}"}

    from datetime import datetime, timedelta
    import pandas as pd

    daily_fields = {"pct_chg", "amount"}

    if sort_by in daily_fields:
        # Use daily API for pct_chg / amount
        if days > 1 and sort_by == "pct_chg":
            # Multi-day cumulative return: fetch N days of daily data
            # First find the latest trading date
            df_latest = pro.daily(trade_date=trade_date, fields="ts_code,trade_date,close,pct_chg")
            if df_latest.empty:
                dt = datetime.strptime(trade_date, "%Y%m%d")
                for i in range(1, 5):
                    prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
                    df_latest = pro.daily(trade_date=prev, fields="ts_code,trade_date,close,pct_chg")
                    if not df_latest.empty:
                        trade_date = prev
                        break
            if df_latest.empty:
                return {"data": [], "message": "无数据"}
            # Get trade calendar to find the date N trading days ago
            actual_date = df_latest["trade_date"].iloc[0]
            cal = pro.trade_cal(exchange='SSE', is_open='1', end_date=actual_date, fields='cal_date')
            cal = cal.sort_values('cal_date', ascending=False).head(days + 1)
            if len(cal) < days + 1:
                return {"data": [], "message": f"交易日历数据不足，无法计算{days}日累计涨跌幅"}
            start_date_n = cal.iloc[-1]['cal_date']
            # Get the close price on start_date_n for each stock
            df_start = pro.daily(trade_date=start_date_n, fields="ts_code,close")
            if df_start.empty:
                return {"data": [], "message": f"{start_date_n}无行情数据"}
            df_start = df_start.rename(columns={"close": "close_start"})
            df_latest = df_latest.rename(columns={"close": "close_end"})
            merged = df_latest[["ts_code", "trade_date", "close_end"]].merge(
                df_start[["ts_code", "close_start"]], on="ts_code", how="inner"
            )
            merged["pct_chg"] = ((merged["close_end"] - merged["close_start"]) / merged["close_start"] * 100).round(2)
            df = merged
            df["close"] = df["close_end"]
        else:
            # Single day pct_chg or amount
            df = pro.daily(trade_date=trade_date, fields="ts_code,trade_date,close,pct_chg,amount")
            if df.empty:
                dt = datetime.strptime(trade_date, "%Y%m%d")
                for i in range(1, 5):
                    prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
                    df = pro.daily(trade_date=prev, fields="ts_code,trade_date,close,pct_chg,amount")
                    if not df.empty:
                        trade_date = prev
                        break
            if df.empty:
                return {"data": [], "message": "无数据"}
            if sort_by == "amount":
                df["amount"] = (df["amount"] / 1e5).round(2)
    else:
        # Valuation fields from daily_basic
        df = pro.daily_basic(trade_date=trade_date, fields="ts_code,trade_date,pe,pb,ps,total_mv,circ_mv,turnover_rate,dv_ratio")
        if df.empty:
            dt = datetime.strptime(trade_date, "%Y%m%d")
            for i in range(1, 5):
                prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
                df = pro.daily_basic(trade_date=prev, fields="ts_code,trade_date,pe,pb,ps,total_mv,circ_mv,turnover_rate,dv_ratio")
                if not df.empty:
                    trade_date = prev
                    break
        if df.empty:
            return {"data": [], "message": "无数据"}

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
    if sort_by == "pct_chg" and "close" in df.columns:
        fields.append("close")
    if sort_by not in ('total_mv', 'circ_mv', 'pct_chg', 'amount'):
        fields.extend(['total_mv', 'circ_mv'])
    fields = [f for f in fields if f in df.columns]
    # deduplicate while preserving order
    seen = set()
    fields = [f for f in fields if not (f in seen or seen.add(f))]

    note = "pct_chg=涨跌幅(%), close=收盘价, total_mv=总市值(亿元), circ_mv=流通市值(亿元), amount=成交额(亿元)"
    if days > 1 and sort_by == "pct_chg":
        note = f"pct_chg={days}日累计涨跌幅(%), close=最新收盘价"

    return {
        "data": df[fields].to_dict("records"),
        "note": note,
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
