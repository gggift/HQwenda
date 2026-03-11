import tushare as ts
from app.tools.registry import tool

_pro_instance = None


def _get_pro():
    global _pro_instance
    if _pro_instance is None:
        from app.config import Settings

        settings = Settings()
        _pro_instance = ts.pro_api(settings.tushare_token)
    return _pro_instance


@tool(
    name="get_stock_basic",
    description="获取股票基础信息，包括名称、代码、行业、上市日期。可用于股票名称和代码的互相查找。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ（可选）",
            },
            "name": {
                "type": "string",
                "description": "股票名称，如 平安银行（可选）",
            },
        },
    },
)
def get_stock_basic(ts_code: str = None, name: str = None) -> dict:
    pro = _get_pro()
    kwargs = {"exchange": "", "list_status": "L", "fields": "ts_code,name,industry,list_date"}
    if ts_code:
        kwargs["ts_code"] = ts_code
    df = pro.stock_basic(**kwargs)
    if name:
        df = df[df["name"].str.contains(name)]
    if df.empty:
        return {"data": [], "message": "未找到匹配的股票"}
    return {"data": df.head(10).to_dict("records")}


@tool(
    name="get_trade_calendar",
    description="获取交易日历，查询某段时间内的交易日和休市日。",
    parameters={
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "开始日期，格式 YYYYMMDD",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式 YYYYMMDD",
            },
        },
        "required": ["start_date", "end_date"],
    },
)
def get_trade_calendar(start_date: str, end_date: str) -> dict:
    pro = _get_pro()
    df = pro.trade_cal(start_date=start_date, end_date=end_date)
    if df.empty:
        return {"data": [], "message": "无数据"}
    return {"data": df[["cal_date", "is_open"]].to_dict("records")}


@tool(
    name="calculate_metric",
    description="简单计算工具。支持：pct_change（涨跌幅%）、average（均值）、max（最大值）、min（最小值）、sum（求和）。",
    parameters={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "计算类型：pct_change, average, max, min, sum",
            },
            "values": {
                "type": "array",
                "items": {"type": "number"},
                "description": "数值列表",
            },
        },
        "required": ["operation", "values"],
    },
)
def calculate_metric(operation: str, values: list) -> dict:
    if not values:
        return {"error": "数值列表不能为空"}

    if operation == "pct_change":
        if len(values) < 2:
            return {"error": "涨跌幅计算需要至少2个值（起始值和结束值）"}
        result = (values[-1] - values[0]) / values[0] * 100
    elif operation == "average":
        result = sum(values) / len(values)
    elif operation == "max":
        result = max(values)
    elif operation == "min":
        result = min(values)
    elif operation == "sum":
        result = sum(values)
    else:
        return {"error": f"不支持的操作: {operation}"}

    return {"result": result}
