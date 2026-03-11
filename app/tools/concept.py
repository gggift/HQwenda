from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_concept_list",
    description="获取概念板块列表。",
    parameters={"type": "object", "properties": {}},
)
def get_concept_list() -> dict:
    pro = _get_pro()
    df = pro.concept()
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["code", "name"] if c in df.columns]
    return {"data": df[fields].to_dict("records")}


@tool(
    name="get_concept_stocks",
    description="获取概念板块的成分股列表。",
    parameters={
        "type": "object",
        "properties": {
            "concept_id": {"type": "string", "description": "概念板块ID，如 TS001。可先用 get_concept_list 查询。"},
        },
        "required": ["concept_id"],
    },
)
def get_concept_stocks(concept_id: str) -> dict:
    pro = _get_pro()
    df = pro.concept_detail(id=concept_id)
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["ts_code", "name"] if c in df.columns]
    return {"data": df[fields].head(30).to_dict("records")}


@tool(
    name="get_stock_concepts",
    description="获取个股所属的概念板块列表。注意：此接口遍历概念板块查找，可能较慢。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {"type": "string", "description": "股票代码，如 000001.SZ"},
        },
        "required": ["ts_code"],
    },
)
def get_stock_concepts(ts_code: str) -> dict:
    pro = _get_pro()
    try:
        df = pro.concept_detail(ts_code=ts_code)
    except Exception:
        return {"data": [], "message": "该接口暂不支持按股票代码查询"}
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["id", "concept_name"] if c in df.columns]
    return {"data": df[fields].to_dict("records")}
