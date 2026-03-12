from app.tools.registry import tool
from app.tools.utils_tool import _get_pro

HSGT_FIELDS = ["trade_date", "hgt", "sgt", "north_money", "ggt_ss", "ggt_sz", "south_money"]

MONEYFLOW_FIELDS = [
    "ts_code",
    "trade_date",
    "buy_elg_amount",
    "sell_elg_amount",
    "buy_lg_amount",
    "sell_lg_amount",
    "buy_md_amount",
    "sell_md_amount",
    "buy_sm_amount",
    "sell_sm_amount",
    "net_mf_amount",
    "net_mf_vol",
]


@tool(
    name="get_northbound_flow",
    description="获取沪深港通北向资金（陆股通）每日流入流出数据，包括沪股通和深股通的买入、卖出和净买入金额。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD（可选）",
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
        "required": [],
    },
)
def get_northbound_flow(
    trade_date: str = None, start_date: str = None, end_date: str = None
) -> dict:
    try:
        pro = _get_pro()
        kwargs = {}
        if trade_date:
            kwargs["trade_date"] = trade_date
        if start_date:
            kwargs["start_date"] = start_date
        if end_date:
            kwargs["end_date"] = end_date
        df = pro.moneyflow_hsgt(**kwargs)
        if df.empty:
            return {"data": [], "message": "无数据"}
        df = df.head(20)
        # Amount fields are in 百万元, convert to 亿元
        amount_cols = ["hgt", "sgt", "north_money", "ggt_ss", "ggt_sz", "south_money"]
        for col in amount_cols:
            if col in df.columns:
                df[col] = (df[col] / 100).round(2)
        fields = [f for f in HSGT_FIELDS if f in df.columns]
        records = df[fields].to_dict("records")
        return {
            "data": records,
            "note": "金额单位：亿元；hgt=沪股通，sgt=深股通，north_money=北向资金合计，ggt_ss=港股通（沪），ggt_sz=港股通（深），south_money=南向资金合计",
        }
    except Exception as e:
        return {"error": str(e), "message": "获取北向资金数据失败，请检查权限或参数"}


@tool(
    name="get_moneyflow",
    description="获取个股资金流向数据，包括主力、超大单、大单、中单、小单的买入卖出金额。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD（可选）",
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
def get_moneyflow(
    ts_code: str,
    trade_date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    try:
        pro = _get_pro()
        kwargs = {"ts_code": ts_code}
        if trade_date:
            kwargs["trade_date"] = trade_date
        if start_date:
            kwargs["start_date"] = start_date
        if end_date:
            kwargs["end_date"] = end_date
        df = pro.moneyflow(**kwargs)
        if df.empty:
            return {"data": [], "message": "无数据"}
        df = df.head(20)
        fields = [f for f in MONEYFLOW_FIELDS if f in df.columns]
        records = df[fields].to_dict("records")
        return {
            "data": records,
            "note": "金额单位：万元；elg=超大单，lg=大单，md=中单，sm=小单，net_mf_amount=主力净流入金额，net_mf_vol=主力净流入量（手）",
        }
    except Exception as e:
        return {"error": str(e), "message": f"获取个股资金流向数据失败，ts_code={ts_code}，请检查权限或参数"}
