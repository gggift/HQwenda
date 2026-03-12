from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_fx_daily",
    description="获取外汇日行情，如美元兑人民币(USDCNY)、美元指数(DXY)等。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "外汇代码，如 USDCNY.FXCM（美元兑人民币）、DXYUSD.FXCM（美元指数），可选",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD，可选",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD，可选",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD，可选",
            },
        },
    },
)
def get_fx_daily(
    ts_code: str = None,
    trade_date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {}
    if ts_code:
        kwargs["ts_code"] = ts_code
    if trade_date:
        kwargs["trade_date"] = trade_date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    try:
        df = pro.fx_daily(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty:
        return {"data": [], "message": "无数据，可能权限不足或该日期无行情"}
    return {"data": df.head(30).to_dict("records")}


@tool(
    name="get_shibor",
    description="获取Shibor利率数据，包括隔夜、1周、1月、3月等期限。",
    parameters={
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "查询日期，格式 YYYYMMDD，可选",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD，可选",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD，可选",
            },
        },
    },
)
def get_shibor(
    date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {}
    if date:
        kwargs["date"] = date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    try:
        df = pro.shibor(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty:
        return {"data": [], "message": "无数据"}
    # Columns: date, on, 1w, 2w, 1m, 3m, 6m, 9m, 1y
    return {"data": df.head(30).to_dict("records")}


@tool(
    name="get_cn_bond_yield",
    description="获取中国国债收益率曲线数据。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "收益率曲线代码，默认 1001.CB（中债国债收益率曲线），可选",
            },
            "curve_type": {
                "type": "string",
                "description": "曲线类型：0（到期收益率）、1（即期收益率），默认 0，可选",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD，可选",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD，可选",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD，可选",
            },
        },
    },
)
def get_cn_bond_yield(
    ts_code: str = "1001.CB",
    curve_type: str = "0",
    trade_date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code, "curve_type": curve_type}
    if trade_date:
        kwargs["trade_date"] = trade_date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    try:
        df = pro.yc_cb(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty:
        # Date fallback
        if trade_date:
            from datetime import datetime, timedelta
            dt = datetime.strptime(trade_date, "%Y%m%d")
            for i in range(1, 5):
                prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
                kwargs["trade_date"] = prev
                df = pro.yc_cb(**kwargs)
                if not df.empty:
                    break
    if df.empty:
        return {"data": [], "message": "无数据"}
    # Filter to key terms for readability
    key_terms = {0.25: "3月", 0.5: "6月", 1.0: "1年", 2.0: "2年", 3.0: "3年",
                 5.0: "5年", 7.0: "7年", 10.0: "10年", 20.0: "20年", 30.0: "30年"}
    if "curve_term" in df.columns:
        df_key = df[df["curve_term"].isin(key_terms.keys())].copy()
        if not df_key.empty:
            df_key["term_name"] = df_key["curve_term"].map(key_terms)
            fields = [c for c in ["trade_date", "term_name", "curve_term", "yield"] if c in df_key.columns]
            return {"data": df_key[fields].to_dict("records")}
    fields = [c for c in ["trade_date", "curve_term", "yield"] if c in df.columns]
    return {"data": df[fields].head(20).to_dict("records")}


@tool(
    name="get_us_treasury_yield",
    description="获取美国国债收益率数据，包括1个月到30年各期限收益率。",
    parameters={
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "查询日期，格式 YYYYMMDD，可选",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD，可选（与date等价）",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD，可选",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD，可选",
            },
        },
    },
)
def get_us_treasury_yield(
    date: str = None,
    trade_date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {}
    # Accept both date and trade_date (LLM sometimes sends trade_date)
    actual_date = date or trade_date
    if actual_date:
        kwargs["date"] = actual_date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    try:
        df = pro.us_tycr(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty and actual_date:
        from datetime import datetime, timedelta
        dt = datetime.strptime(actual_date, "%Y%m%d")
        for i in range(1, 5):
            prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
            kwargs["date"] = prev
            try:
                df = pro.us_tycr(**kwargs)
            except Exception:
                continue
            if not df.empty:
                break
    if df.empty:
        return {"data": [], "message": "无数据"}
    # Columns: date, m1, m2, m3, m6, y1, y2, y3, y5, y7, y10, y20, y30
    return {"data": df.head(30).to_dict("records")}


@tool(
    name="get_fut_mapping",
    description="获取期货主力合约映射，查询某品种当前的主力合约代码。用于不确定具体合约代码时先查询主力合约。",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "期货品种代码（大写），如 AU（黄金）、SC（原油）、CU（铜）、AG（白银）、AL（铝）、RB（螺纹钢）、I（铁矿石）",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD（可选）",
            },
        },
        "required": ["symbol"],
    },
)
def get_fut_mapping(symbol: str, trade_date: str = None) -> dict:
    pro = _get_pro()
    kwargs = {}
    if trade_date:
        kwargs["trade_date"] = trade_date
    try:
        df = pro.fut_mapping(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty:
        # Date fallback
        if trade_date:
            from datetime import datetime, timedelta
            dt = datetime.strptime(trade_date, "%Y%m%d")
            for i in range(1, 5):
                prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
                try:
                    df = pro.fut_mapping(trade_date=prev)
                except Exception:
                    continue
                if not df.empty:
                    break
        else:
            # Try without date
            try:
                df = pro.fut_mapping()
            except Exception:
                pass
    if df.empty:
        return {"data": [], "message": "无数据"}
    # Filter by symbol
    df_filtered = df[df["ts_code"].str.startswith(symbol.upper())]
    if df_filtered.empty:
        # Try lowercase
        df_filtered = df[df["ts_code"].str.upper().str.startswith(symbol.upper())]
    if df_filtered.empty:
        return {"data": [], "message": f"未找到品种 {symbol} 的主力合约", "all_symbols": df["ts_code"].head(20).tolist()}
    fields = [c for c in ["ts_code", "trade_date", "mapping_ts_code"] if c in df_filtered.columns]
    return {"data": df_filtered[fields].head(5).to_dict("records"), "note": "mapping_ts_code为当前主力合约代码"}


@tool(
    name="get_fut_daily",
    description="获取期货品种日行情（黄金AU、原油SC、铜CU等）。如不确定合约代码，先调用get_fut_mapping获取主力合约代码。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "期货合约代码（如AU2506.SHF），不确定时先调用get_fut_mapping获取主力合约，可选",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD，可选",
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD，可选",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD，可选",
            },
        },
    },
)
def get_fut_daily(
    ts_code: str = None,
    trade_date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {}
    if ts_code:
        kwargs["ts_code"] = ts_code
    if trade_date:
        kwargs["trade_date"] = trade_date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    try:
        df = pro.fut_daily(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty and trade_date:
        # Date fallback
        from datetime import datetime, timedelta
        dt = datetime.strptime(trade_date, "%Y%m%d")
        for i in range(1, 5):
            prev = (dt - timedelta(days=i)).strftime("%Y%m%d")
            kwargs["trade_date"] = prev
            try:
                df = pro.fut_daily(**kwargs)
            except Exception:
                continue
            if not df.empty:
                break
    if df.empty:
        return {"data": [], "message": "无数据，请先调用get_fut_mapping获取当前主力合约代码"}
    fields = [c for c in ["ts_code", "trade_date", "open", "high", "low", "close", "settle", "vol", "amount", "oi"] if c in df.columns]
    return {"data": df[fields].head(30).to_dict("records")}
