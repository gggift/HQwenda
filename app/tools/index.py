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


@tool(
    name="get_consecutive_streak",
    description="计算股票或指数的最长连续上涨/下跌/阳线/阴线天数，返回历史上前N段最长记录（起止日期、天数、累计涨跌幅）。适用于'连续上涨最长'、'最长连跌'、'连续阳线最多'、'连续阴线最多'等问题。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "股票或指数代码，如 000001.SH（上证指数）"},
            "direction": {"type": "string", "description": "方向：up（连涨，收盘>前收盘）、down（连跌，收盘<前收盘）、yang（连续阳线，收盘>开盘）、yin（连续阴线，收盘<开盘），默认 up"},
            "is_index": {"type": "boolean", "description": "是否为指数代码，默认 false；指数请传 true"},
            "top_n": {"type": "integer", "description": "返回前N段最长记录，默认 10"},
            "start_date": {"type": "string", "description": "起始日期，格式 YYYYMMDD，默认不限（查全部历史）"},
            "end_date": {"type": "string", "description": "截止日期，格式 YYYYMMDD，默认不限"},
        },
        "required": ["ts_code"],
    },
)
def get_consecutive_streak(
    ts_code: str,
    direction: str = "up",
    is_index: bool = False,
    top_n: int = 10,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code, "fields": "trade_date,open,close,pct_chg"}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date

    if is_index:
        df = pro.index_daily(**kwargs)
    else:
        df = pro.daily(**kwargs)

    if df.empty:
        return {"data": [], "message": "无数据"}

    # Sort ascending by date
    df = df.sort_values("trade_date", ascending=True).reset_index(drop=True)
    df = df.dropna(subset=["pct_chg"])

    if df.empty:
        return {"data": [], "message": "过滤后无数据"}

    # Find all consecutive streaks
    if direction == "down":
        df["match"] = df["pct_chg"] < 0
    elif direction == "yang":
        df["match"] = df["close"] > df["open"]
    elif direction == "yin":
        df["match"] = df["close"] < df["open"]
    else:
        df["match"] = df["pct_chg"] > 0

    streaks = []
    streak_start = None
    streak_len = 0

    for i, row in df.iterrows():
        if row["match"]:
            if streak_start is None:
                streak_start = i
            streak_len += 1
        else:
            if streak_len > 0:
                streaks.append((streak_start, i - 1, streak_len))
            streak_start = None
            streak_len = 0
    # Handle streak at end
    if streak_len > 0:
        streaks.append((streak_start, len(df) - 1, streak_len))

    direction_labels = {"up": "连涨", "down": "连跌", "yang": "连续阳线", "yin": "连续阴线"}
    label = direction_labels.get(direction, "连涨")

    if not streaks:
        return {"data": [], "message": f"未找到{label}记录"}

    # Sort by streak length descending
    streaks.sort(key=lambda x: x[2], reverse=True)
    streaks = streaks[:top_n]

    results = []
    for s_start, s_end, s_len in streaks:
        start_row = df.iloc[s_start]
        end_row = df.iloc[s_end]
        # Calculate cumulative return
        start_close = df.iloc[s_start - 1]["close"] if s_start > 0 else start_row["close"]
        end_close = end_row["close"]
        cum_return = round((end_close - start_close) / start_close * 100, 2) if start_close else 0

        results.append({
            "start_date": start_row["trade_date"],
            "end_date": end_row["trade_date"],
            "days": s_len,
            "start_close": round(float(start_close), 2),
            "end_close": round(float(end_close), 2),
            "cumulative_return_pct": cum_return,
        })

    return {
        "data": results,
        "note": f"历史最长{label}前{len(results)}段记录，days=连续天数，cumulative_return_pct=累计涨跌幅(%)",
        "total_trading_days": len(df),
    }
