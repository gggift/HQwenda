import pandas as pd
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_moving_averages",
    description="计算股票或指数的移动均线（MA5/MA10/MA20/MA60/MA120/MA250），判断金叉死叉信号，计算收盘价偏离均线的百分比。",
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
def get_moving_averages(ts_code: str, is_index: bool = False) -> dict:
    pro = _get_pro()

    if is_index:
        df = pro.index_daily(ts_code=ts_code)
    else:
        df = pro.daily(ts_code=ts_code)

    if df.empty:
        return {"data": {}, "message": "无数据"}

    df = df.head(260).copy()
    # Data is in reverse chronological order; reverse for rolling calculation
    df = df.iloc[::-1].reset_index(drop=True)

    df["ma5"] = df["close"].rolling(5).mean()
    df["ma10"] = df["close"].rolling(10).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    df["ma120"] = df["close"].rolling(120).mean()
    df["ma250"] = df["close"].rolling(250).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else None

    close = round(float(latest["close"]), 4)
    trade_date = str(latest["trade_date"])

    ma_values = {}
    for ma in ["ma5", "ma10", "ma20", "ma60", "ma120", "ma250"]:
        val = latest[ma]
        ma_values[ma] = round(float(val), 4) if pd.notna(val) else None

    def deviation(close_val, ma_val):
        if ma_val is None:
            return None
        return round((close_val - ma_val) / ma_val * 100, 2)

    deviation_ma20_pct = deviation(close, ma_values["ma20"])
    deviation_ma60_pct = deviation(close, ma_values["ma60"])

    above_mas = []
    below_mas = []
    for ma in ["ma5", "ma10", "ma20", "ma60", "ma120", "ma250"]:
        val = ma_values[ma]
        if val is None:
            continue
        label = ma.upper()
        if close > val:
            above_mas.append(label)
        elif close < val:
            below_mas.append(label)

    signals = []
    if prev is not None:
        # MA5/MA10 golden cross / death cross
        ma5_today = latest["ma5"]
        ma10_today = latest["ma10"]
        ma5_prev = prev["ma5"]
        ma10_prev = prev["ma10"]

        if pd.notna(ma5_today) and pd.notna(ma10_today) and pd.notna(ma5_prev) and pd.notna(ma10_prev):
            if float(ma5_today) > float(ma10_today) and float(ma5_prev) <= float(ma10_prev):
                signals.append("MA5/MA10金叉")
            elif float(ma5_today) < float(ma10_today) and float(ma5_prev) >= float(ma10_prev):
                signals.append("MA5/MA10死叉")

        # MA10/MA20 golden cross / death cross
        ma20_today = latest["ma20"]
        ma20_prev = prev["ma20"]

        if pd.notna(ma10_today) and pd.notna(ma20_today) and pd.notna(ma10_prev) and pd.notna(ma20_prev):
            if float(ma10_today) > float(ma20_today) and float(ma10_prev) <= float(ma20_prev):
                signals.append("MA10/MA20金叉")
            elif float(ma10_today) < float(ma20_today) and float(ma10_prev) >= float(ma20_prev):
                signals.append("MA10/MA20死叉")

    return {
        "data": {
            "ts_code": ts_code,
            "trade_date": trade_date,
            "close": close,
            "ma5": ma_values["ma5"],
            "ma10": ma_values["ma10"],
            "ma20": ma_values["ma20"],
            "ma60": ma_values["ma60"],
            "ma120": ma_values["ma120"],
            "ma250": ma_values["ma250"],
            "deviation_ma20_pct": deviation_ma20_pct,
            "deviation_ma60_pct": deviation_ma60_pct,
            "above_mas": above_mas,
            "below_mas": below_mas,
            "signals": signals,
        }
    }
