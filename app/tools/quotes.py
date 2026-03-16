import tushare as ts
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro

QUOTE_FIELDS = ["trade_date", "open", "high", "low", "close", "vol", "amount", "pct_chg"]


@tool(
    name="get_daily_quotes",
    description="获取股票日K线数据，包括开盘价、最高价、最低价、收盘价、成交量(vol)、成交额(amount，单位亿元)、涨跌幅。默认返回最近20个交易日。",
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
    if "amount" in df.columns:
        df["amount"] = (df["amount"] / 1e5).round(2)
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
    if "amount" in df.columns:
        df["amount"] = (df["amount"] / 1e5).round(2)
    return {"data": df[QUOTE_FIELDS].to_dict("records")}


@tool(
    name="get_market_stats",
    description="获取某日全市场股票涨跌统计，可按交易所筛选（SH沪市/SZ深市），支持按涨跌幅阈值统计数量，返回涨跌分布和符合条件的股票列表。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD",
            },
            "exchange": {
                "type": "string",
                "description": "交易所筛选：SH（沪市）、SZ（深市），不填则全市场",
            },
            "pct_chg_min": {
                "type": "number",
                "description": "涨跌幅下限（如 10 表示涨幅>=10%），可选",
            },
            "pct_chg_max": {
                "type": "number",
                "description": "涨跌幅上限（如 -10 表示跌幅<=-10%），可选",
            },
        },
        "required": ["trade_date"],
    },
)
def get_market_stats(
    trade_date: str, exchange: str = None, pct_chg_min: float = None, pct_chg_max: float = None
) -> dict:
    from datetime import datetime, timedelta
    pro = _get_pro()
    df = pro.daily(trade_date=trade_date)
    # Date fallback
    if df.empty:
        dt = datetime.strptime(trade_date, "%Y%m%d")
        for i in range(1, 5):
            prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
            df = pro.daily(trade_date=prev)
            if not df.empty:
                trade_date = prev
                break
    if df.empty:
        return {"data": {}, "message": "无数据"}
    if exchange:
        df = df[df["ts_code"].str.endswith(f".{exchange}")]
    total = len(df)
    up = int((df["pct_chg"] > 0).sum())
    down = int((df["pct_chg"] < 0).sum())
    flat = total - up - down
    limit_up = int((df["pct_chg"] >= 9.9).sum())
    limit_down = int((df["pct_chg"] <= -9.9).sum())
    result = {
        "trade_date": trade_date,
        "total": total,
        "up": up,
        "down": down,
        "flat": flat,
        "limit_up": limit_up,
        "limit_down": limit_down,
    }
    filtered = df
    if pct_chg_min is not None:
        filtered = filtered[filtered["pct_chg"] >= pct_chg_min]
    if pct_chg_max is not None:
        filtered = filtered[filtered["pct_chg"] <= pct_chg_max]
    result["filtered_count"] = len(filtered)
    if not filtered.empty:
        fields = [c for c in ["ts_code", "close", "pct_chg"] if c in filtered.columns]
        result["filtered_stocks"] = filtered[fields].head(30).to_dict("records")
    return {"data": result}


@tool(
    name="get_multi_period_returns",
    description="计算股票或指数在多个时间周期的累计涨跌幅，用于资产轮动和横向对比。支持5日、20日、60日、120日、250日周期。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票或指数代码，如 000001.SZ 或 000300.SH",
            },
            "is_index": {
                "type": "boolean",
                "description": "是否为指数代码，默认 false；指数请传 true",
            },
        },
        "required": ["ts_code"],
    },
)
def get_multi_period_returns(ts_code: str, is_index: bool = False) -> dict:
    pro = _get_pro()
    if is_index:
        df = pro.index_daily(ts_code=ts_code)
    else:
        df = pro.daily(ts_code=ts_code)
    if df.empty:
        return {"data": {}, "message": "无数据"}
    df = df.head(260).sort_values("trade_date", ascending=True).reset_index(drop=True)
    latest_close = df.iloc[-1]["close"]
    latest_date = df.iloc[-1]["trade_date"]
    result = {
        "ts_code": ts_code,
        "trade_date": latest_date,
        "close": latest_close,
    }
    for period in [5, 20, 60, 120, 250]:
        key = f"return_{period}d"
        idx = len(df) - 1 - period
        if idx >= 0:
            past_close = df.iloc[idx]["close"]
            ret = round((latest_close - past_close) / past_close * 100, 2)
            result[key] = ret
        else:
            result[key] = None
    return {"data": result}


@tool(
    name="get_industry_valuation_rank",
    description="获取申万一级行业（31个）指数的PE和PB估值排名，可用于查找估值极端的行业。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD",
            },
        },
        "required": ["trade_date"],
    },
)
def get_industry_valuation_rank(trade_date: str) -> dict:
    from app.tools.industry import _get_sw_l1_codes
    pro = _get_pro()
    df = pro.sw_daily(trade_date=trade_date)
    if df.empty:
        return {"data": [], "message": "无数据"}
    # Filter to L1 (一级行业) only
    l1_codes = _get_sw_l1_codes()
    if l1_codes:
        df = df[df["ts_code"].isin(l1_codes)]
    fields = [c for c in ["ts_code", "name", "pe", "pb", "pct_change", "close"] if c in df.columns]
    df = df[fields].dropna(subset=["pe"]).sort_values("pe", ascending=True).reset_index(drop=True)
    return {"data": df.to_dict("records")}


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
    try:
        # realtime_quote is a top-level tushare function, needs set_token
        from app.config import Settings
        ts.set_token(Settings().tushare_token)
        df = ts.realtime_quote(ts_code=ts_code)
        if df.empty:
            return {"data": [], "message": "无数据"}
        # Normalize column names to lowercase
        df.columns = [c.lower() for c in df.columns]
        fields = [c for c in ["ts_code", "name", "open", "pre_close", "price", "high", "low", "vol", "amount"] if c in df.columns]
        return {"data": df[fields].to_dict("records")}
    except Exception as e:
        return {"error": str(e), "message": "获取实时行情失败"}


@tool(
    name="get_historical_percentile",
    description="计算股票或指数当前价格/成交额/换手率/PE/PB等指标在历史区间中的分位数，判断是否处于历史高位或低位。返回当前值的分位数排名，以及10%/25%/50%/75%/90%分位对应的具体数值。支持最多10年(2500个交易日)的回溯。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票或指数代码，如 000001.SZ 或 000300.SH",
            },
            "indicator": {
                "type": "string",
                "description": "指标名称，可选 close/amount/vol/pe/pb/turnover_rate",
            },
            "days": {
                "type": "integer",
                "description": "回溯交易日数，默认252（约1年）。可设为2500（约10年）、1250（约5年）、500（约2年）等",
            },
            "is_index": {
                "type": "boolean",
                "description": "是否为指数代码，默认 false；指数请传 true",
            },
        },
        "required": ["ts_code", "indicator"],
    },
)
def get_historical_percentile(
    ts_code: str, indicator: str, days: int = 252, is_index: bool = False
) -> dict:
    pro = _get_pro()
    return_note = None

    price_vol_indicators = {"close", "amount", "vol"}
    valuation_indicators = {"pe", "pb", "turnover_rate"}

    if indicator in price_vol_indicators:
        if is_index:
            df = pro.index_daily(ts_code=ts_code, fields=f"trade_date,{indicator}")
        else:
            df = pro.daily(ts_code=ts_code, fields=f"trade_date,{indicator}")
    elif indicator in valuation_indicators:
        if is_index:
            # Indices don't have daily_basic valuation data; use index_dailybasic if available
            try:
                df = pro.index_dailybasic(ts_code=ts_code, fields=f"trade_date,{indicator}")
            except Exception:
                # Fallback: for turnover_rate, estimate from amount
                if indicator == "turnover_rate":
                    df = pro.index_daily(ts_code=ts_code, fields="trade_date,amount")
                    if not df.empty:
                        indicator = "amount"
                        return_note = "指数无直接换手率数据，使用成交额作为量能替代指标计算分位数"
                    else:
                        return {"data": {}, "message": "指数无换手率数据，且无法获取成交额数据"}
                else:
                    return {"data": {}, "message": f"指数暂不支持 {indicator} 指标的分位数计算"}
        else:
            df = pro.daily_basic(ts_code=ts_code, fields=f"trade_date,{indicator}")
    else:
        return {"data": {}, "message": f"不支持的指标: {indicator}，可选 close/amount/vol/pe/pb/turnover_rate"}

    if df.empty:
        return {"data": {}, "message": "无数据"}

    df = df.head(days).dropna(subset=[indicator])

    if df.empty:
        return {"data": {}, "message": "过滤后无有效数据"}

    if indicator == "amount":
        df[indicator] = (df[indicator] / 1e5).round(4)

    import numpy as np
    values = df[indicator].tolist()
    current = values[0]
    min_val = round(min(values), 4)
    max_val = round(max(values), 4)
    rank = sum(1 for v in values if v <= current)
    percentile = round(rank / len(values) * 100, 2)

    # Calculate key percentile breakpoints
    arr = np.array(values)
    key_percentiles = {
        "p10": round(float(np.percentile(arr, 10)), 4),
        "p25": round(float(np.percentile(arr, 25)), 4),
        "p50_median": round(float(np.percentile(arr, 50)), 4),
        "p75": round(float(np.percentile(arr, 75)), 4),
        "p90": round(float(np.percentile(arr, 90)), 4),
    }

    # Date range info
    date_start = df["trade_date"].iloc[-1] if "trade_date" in df.columns else None
    date_end = df["trade_date"].iloc[0] if "trade_date" in df.columns else None

    result = {
        "data": {
            "ts_code": ts_code,
            "indicator": indicator,
            "current": round(current, 4),
            "min": min_val,
            "max": max_val,
            "percentile": percentile,
            "key_percentiles": key_percentiles,
            "is_at_high": current == max_val,
            "is_at_low": current == min_val,
            "days": len(values),
            "date_range": f"{date_start} ~ {date_end}" if date_start else None,
        }
    }
    if return_note:
        result["note"] = return_note
    return result
