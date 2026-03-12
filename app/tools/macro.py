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
        return {"data": [], "message": "无数据"}
    # Columns: trade_date, ts_code, curve_name, curve_type, curve_term, yield
    return {"data": df.head(50).to_dict("records")}


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
        df = pro.us_tycr(**kwargs)
    except Exception as e:
        return {"data": [], "message": f"接口调用失败: {e}"}
    if df.empty:
        return {"data": [], "message": "无数据"}
    # Columns: date, m1, m2, m3, m6, y1, y2, y3, y5, y7, y10, y20, y30
    return {"data": df.head(30).to_dict("records")}


@tool(
    name="get_fut_daily",
    description="获取期货品种日行情（黄金AU、原油SC、铜CU等）。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "期货合约代码，如 AU2502.SHF（黄金）、SC2503.INE（原油）、CU2503.SHF（铜），可选",
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
    if df.empty:
        return {"data": [], "message": "无数据，请检查合约代码和日期是否正确"}
    fields = [c for c in ["ts_code", "trade_date", "open", "high", "low", "close", "settle", "vol", "amount", "oi"] if c in df.columns]
    return {"data": df[fields].head(30).to_dict("records")}
