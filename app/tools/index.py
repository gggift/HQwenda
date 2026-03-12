from datetime import datetime, timedelta

from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_index_daily",
    description="获取指数日行情数据（如上证指数、深证成指、创业板指等），包括开高低收、成交量(vol)、成交额(amount，单位亿元)、涨跌幅。",
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
    fields = ["trade_date", "open", "high", "low", "close", "vol", "amount", "pct_chg"]
    fields = [f for f in fields if f in df.columns]
    if "amount" in df.columns:
        df["amount"] = (df["amount"] / 1e5).round(2)
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


@tool(
    name="get_index_history_filter",
    description="查询指数或股票长周期历史日行情并按条件筛选，适用于'过去N年收盘价高于X点有多少天'等需要大范围历史数据的问题。返回符合条件的交易日列表和总数。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "指数或股票代码，如 000001.SH"},
            "start_date": {"type": "string", "description": "开始日期，格式 YYYYMMDD"},
            "end_date": {"type": "string", "description": "结束日期，格式 YYYYMMDD"},
            "field": {"type": "string", "description": "筛选字段，如 close/open/high/low/pct_chg/vol/amount"},
            "operator": {"type": "string", "description": "比较运算符：gt(大于)、gte(大于等于)、lt(小于)、lte(小于等于)、eq(等于)"},
            "value": {"type": "number", "description": "比较阈值"},
            "is_index": {"type": "boolean", "description": "是否为指数代码，默认 true"},
        },
        "required": ["ts_code", "start_date", "end_date", "field", "operator", "value"],
    },
)
def get_index_history_filter(
    ts_code: str, start_date: str, end_date: str,
    field: str, operator: str, value: float,
    is_index: bool = True,
) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
    if is_index:
        df = pro.index_daily(**kwargs)
    else:
        df = pro.daily(**kwargs)
    if df.empty:
        return {"data": {}, "message": "无数据"}

    if field not in df.columns:
        return {"data": {}, "message": f"字段 {field} 不存在"}

    ops = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "eq": "=="}
    op = ops.get(operator)
    if not op:
        return {"data": {}, "message": f"不支持的运算符: {operator}"}

    filtered = df.query(f"`{field}` {op} @value")
    filtered = filtered.sort_values("trade_date", ascending=True)

    result_fields = ["trade_date", field]
    records = filtered[result_fields].to_dict("records")

    return {
        "data": {
            "total_trading_days": len(df),
            "matched_count": len(filtered),
            "condition": f"{field} {op} {value}",
            "records": records,
        }
    }


@tool(
    name="get_index_member_stats",
    description="获取指数成分股的涨跌统计，包括上涨/下跌/平盘家数、涨跌幅中位数、涨停/跌停家数、涨跌幅贡献居前的个股。适用于沪深300、上证综指等境内主要指数。",
    parameters={
        "type": "object",
        "properties": {
            "index_code": {"type": "string", "description": "指数代码，如 000300.SH（沪深300）"},
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD"},
        },
        "required": ["index_code", "trade_date"],
    },
)
def get_index_member_stats(index_code: str, trade_date: str) -> dict:
    pro = _get_pro()

    # Step 1: Get component stocks and weights; data may lag ~2 weeks
    weight_df = pro.index_weight(index_code=index_code, trade_date=trade_date)
    if weight_df.empty:
        # Try without date to get latest available, then filter
        weight_df = pro.index_weight(index_code=index_code)
        if not weight_df.empty:
            latest_date = weight_df["trade_date"].max()
            weight_df = weight_df[weight_df["trade_date"] == latest_date]

    if weight_df.empty:
        return {"data": {}, "message": "无成分股权重数据"}

    # Step 2: Get ts_codes of component stocks
    component_codes = weight_df["con_code"].tolist()

    # Step 3: Get daily market data for all stocks on that date
    daily_df = pro.daily(trade_date=trade_date)
    if daily_df.empty:
        return {"data": {}, "message": "无当日行情数据"}

    # Step 4: Filter to component stocks only
    daily_df = daily_df[daily_df["ts_code"].isin(component_codes)].copy()
    if daily_df.empty:
        return {"data": {}, "message": "成分股当日无行情数据"}

    # Step 5: Calculate statistics
    total = len(daily_df)
    up_count = int((daily_df["pct_chg"] > 0).sum())
    down_count = int((daily_df["pct_chg"] < 0).sum())
    flat_count = total - up_count - down_count
    median_pct_chg = round(float(daily_df["pct_chg"].median()), 2)
    limit_up = int((daily_df["pct_chg"] >= 9.9).sum())
    limit_down = int((daily_df["pct_chg"] <= -9.9).sum())

    # Step 6: Calculate contribution per stock (weight * pct_chg / 100)
    weight_df = weight_df.rename(columns={"con_code": "ts_code"})
    contrib_df = daily_df[["ts_code", "pct_chg"]].merge(
        weight_df[["ts_code", "weight"]], on="ts_code", how="inner"
    )
    contrib_df["contribution"] = (contrib_df["weight"] * contrib_df["pct_chg"] / 100).round(4)
    contrib_df["pct_chg"] = contrib_df["pct_chg"].round(2)
    contrib_df["weight"] = contrib_df["weight"].round(4)
    top_contributors = (
        contrib_df.sort_values("contribution", ascending=False)
        .head(10)[["ts_code", "pct_chg", "weight", "contribution"]]
        .to_dict("records")
    )

    return {
        "data": {
            "total": total,
            "up_count": up_count,
            "down_count": down_count,
            "flat_count": flat_count,
            "median_pct_chg": median_pct_chg,
            "limit_up": limit_up,
            "limit_down": limit_down,
            "top_contributors": top_contributors,
        }
    }


@tool(
    name="get_index_global",
    description="获取境外主要指数行情数据（如恒生指数HSI、标普500 SPX、纳斯达克IXIC、日经225 N225、德国DAX GDAXI等），包括开高低收、涨跌幅。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "指数代码，如 SPX（标普500）、HSI（恒生指数）、IXIC（纳斯达克）、N225（日经225）、GDAXI（德国DAX）（可选）"},
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD（可选）"},
            "start_date": {"type": "string", "description": "开始日期，格式 YYYYMMDD（可选）"},
            "end_date": {"type": "string", "description": "结束日期，格式 YYYYMMDD（可选）"},
        },
        "required": [],
    },
)
def get_index_global(ts_code: str = None, trade_date: str = None, start_date: str = None, end_date: str = None) -> dict:
    pro = _get_pro()
    kwargs = {}
    if trade_date:
        kwargs["trade_date"] = trade_date
    if ts_code:
        kwargs["ts_code"] = ts_code
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    df = pro.index_global(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    if ts_code:
        df = df.head(20)
    fields = ["ts_code", "trade_date", "open", "close", "high", "low", "pre_close", "pct_chg"]
    fields = [f for f in fields if f in df.columns]
    return {"data": df[fields].to_dict("records")}
