import logging

from app.tools.registry import tool
from app.tools.utils_tool import _get_pro

logger = logging.getLogger(__name__)

# 申万一级行业代码（31个）
_SW_L1_CODES = None
# 个股→申万一级行业名称映射 {stock_ts_code: industry_name}
_STOCK_TO_SW_L1 = None


def _get_sw_l1_codes():
    global _SW_L1_CODES
    if _SW_L1_CODES is None:
        try:
            pro = _get_pro()
            cls = pro.index_classify(level='L1', src='SW2021')
            _SW_L1_CODES = set(cls['index_code'].tolist())
        except Exception:
            _SW_L1_CODES = set()
    return _SW_L1_CODES


def _get_stock_to_sw_l1():
    """Build and cache stock→SW L1 industry name mapping via index_member."""
    global _STOCK_TO_SW_L1
    if _STOCK_TO_SW_L1 is not None:
        return _STOCK_TO_SW_L1
    try:
        pro = _get_pro()
        cls = pro.index_classify(level='L1', src='SW2021')
        mapping = {}
        for _, row in cls.iterrows():
            code = row['index_code']
            name = row['industry_name']
            try:
                members = pro.index_member(index_code=code, is_new='Y')
                if not members.empty:
                    for stock_code in members['con_code'].tolist():
                        mapping[stock_code] = name
            except Exception:
                logger.warning(f"Failed to get members for {code} ({name})")
        _STOCK_TO_SW_L1 = mapping
        logger.info(f"Built SW L1 stock mapping: {len(mapping)} stocks → 31 industries")
    except Exception as e:
        logger.error(f"Failed to build SW L1 mapping: {e}")
        _STOCK_TO_SW_L1 = {}
    return _STOCK_TO_SW_L1


@tool(
    name="get_sw_daily",
    description="获取申万行业指数日行情数据，可查询某日所有行业指数涨跌排名，或查询单个行业指数历史行情。支持按行业级别筛选（L1一级行业31个、L2二级行业、L3三级行业）。默认只返回一级行业。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD（可选）。提供此参数时返回该日行业指数涨跌排名。"},
            "ts_code": {"type": "string", "description": "申万行业指数代码（可选）。提供此参数时返回该行业指数历史行情。"},
            "level": {"type": "string", "description": "行业级别：L1（一级，默认）、L2（二级）、L3（三级）、all（全部）"},
            "start_date": {"type": "string", "description": "开始日期，格式 YYYYMMDD（可选）"},
            "end_date": {"type": "string", "description": "结束日期，格式 YYYYMMDD（可选）"},
        },
        "required": [],
    },
)
def get_sw_daily(
    trade_date: str = None,
    ts_code: str = None,
    level: str = "L1",
    start_date: str = None,
    end_date: str = None,
) -> dict:
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
    df = pro.sw_daily(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}

    # Filter by industry level when querying by trade_date (not single ts_code)
    if trade_date and not ts_code and level != "all":
        if level == "L1":
            l1_codes = _get_sw_l1_codes()
            if l1_codes:
                df = df[df["ts_code"].isin(l1_codes)]
        elif level in ("L2", "L3"):
            try:
                cls = pro.index_classify(level=level, src='SW2021')
                level_codes = set(cls['index_code'].tolist())
                df = df[df["ts_code"].isin(level_codes)]
            except Exception:
                pass

    fields = ["ts_code", "trade_date", "name", "open", "close", "pct_change", "vol", "amount", "pe", "pb"]
    fields = [f for f in fields if f in df.columns]
    if "amount" in df.columns:
        df["amount"] = (df["amount"] / 1e5).round(2)
    if trade_date:
        if "pct_change" in df.columns:
            df = df.sort_values("pct_change", ascending=False)
        return {"data": df[fields].to_dict("records")}
    else:
        return {"data": df[fields].head(20).to_dict("records")}


@tool(
    name="get_industry_index_contribution",
    description="计算申万一级行业对指定指数（如上证指数、沪深300）的贡献点数和贡献涨跌幅。通过个股权重（或流通市值）和涨跌幅，汇总各行业对指数涨跌的贡献。",
    parameters={
        "type": "object",
        "properties": {
            "index_code": {"type": "string", "description": "指数代码，如 000001.SH（上证综指）、000300.SH（沪深300）、399001.SZ（深证成指）"},
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD"},
        },
        "required": ["index_code", "trade_date"],
    },
)
def get_industry_index_contribution(index_code: str, trade_date: str) -> dict:
    pro = _get_pro()

    # 1. Get stock→SW L1 industry mapping (31 industries)
    industry_map = _get_stock_to_sw_l1()
    if not industry_map:
        return {"data": [], "message": "无法获取申万一级行业分类数据"}

    # 2. Try index_weight first (works for CSI300, SSE50, etc.)
    weight_df = pro.index_weight(index_code=index_code, trade_date=trade_date)
    if weight_df.empty:
        weight_df = pro.index_weight(index_code=index_code)
        if not weight_df.empty:
            latest = weight_df['trade_date'].max()
            weight_df = weight_df[weight_df['trade_date'] == latest]

    use_index_weight = not weight_df.empty

    # 3. Get daily quotes
    daily_df = pro.daily(trade_date=trade_date)
    if daily_df.empty:
        return {"data": [], "message": "无当日行情数据"}

    if use_index_weight:
        # Use actual index weights
        weight_df = weight_df.rename(columns={'con_code': 'ts_code'})
        merged = weight_df[['ts_code', 'weight']].merge(
            daily_df[['ts_code', 'pct_chg']], on='ts_code', how='inner'
        )
    else:
        # Estimate weights from circulating market cap (for broad indices like 000001.SH)
        basic_df = pro.daily_basic(trade_date=trade_date, fields='ts_code,circ_mv')
        if basic_df.empty:
            return {"data": [], "message": "无市值数据，无法估算权重"}

        merged = daily_df[['ts_code', 'pct_chg']].merge(
            basic_df[['ts_code', 'circ_mv']], on='ts_code', how='inner'
        )

        # Filter to member stocks by exchange suffix
        if index_code.endswith('.SH'):
            merged = merged[merged['ts_code'].str.endswith('.SH')]
        elif index_code.endswith('.SZ'):
            merged = merged[merged['ts_code'].str.endswith('.SZ')]

        total_mv = merged['circ_mv'].sum()
        if total_mv == 0:
            return {"data": [], "message": "流通市值合计为0"}
        merged['weight'] = merged['circ_mv'] / total_mv * 100
        merged = merged.drop(columns=['circ_mv'])

    # 4. Map to industry
    merged['industry'] = merged['ts_code'].map(industry_map)
    merged = merged.dropna(subset=['industry', 'pct_chg'])

    # 5. Calculate contribution per stock
    merged['contribution_pct'] = merged['weight'] * merged['pct_chg'] / 100

    # 6. Group by industry
    industry_contrib = merged.groupby('industry').agg(
        total_weight=('weight', 'sum'),
        contribution_pct=('contribution_pct', 'sum'),
        stock_count=('ts_code', 'count'),
    ).reset_index()

    # 7. Get index close/pre_close for point calculation
    index_df = pro.index_daily(ts_code=index_code, trade_date=trade_date)
    index_close = None
    index_pct_chg = None
    if not index_df.empty:
        row = index_df.iloc[0]
        pre_close = float(row['pre_close']) if 'pre_close' in row and row['pre_close'] else float(row['close'])
        index_close = float(row['close'])
        index_pct_chg = float(row.get('pct_chg', 0))
        industry_contrib['contribution_points'] = (industry_contrib['contribution_pct'] / 100 * pre_close).round(2)

    industry_contrib['contribution_pct'] = industry_contrib['contribution_pct'].round(4)
    industry_contrib['total_weight'] = industry_contrib['total_weight'].round(2)

    # Sort by contribution_pct descending
    industry_contrib = industry_contrib.sort_values('contribution_pct', ascending=False)

    result = {
        "data": industry_contrib.rename(columns={'industry': 'industry_name'}).to_dict('records'),
        "note": "industry_name=申万一级行业(31个), contribution_pct=贡献涨跌幅(百分点), contribution_points=贡献指数点数, total_weight=行业在指数中的权重占比(%)",
    }
    if index_close is not None:
        result["index_close"] = index_close
        result["index_pct_chg"] = index_pct_chg
        method = "精确权重" if use_index_weight else "流通市值估算权重"
        result["weight_method"] = method

    return result


@tool(
    name="get_ths_daily",
    description="获取同花顺概念板块日行情数据，可查询某日所有概念板块涨跌排名，或查询单个概念板块历史行情。",
    parameters={
        "type": "object",
        "properties": {
            "trade_date": {"type": "string", "description": "交易日期，格式 YYYYMMDD（可选）。提供此参数时返回该日涨跌幅前30的概念板块。"},
            "ts_code": {"type": "string", "description": "同花顺概念板块代码（可选）。提供此参数时返回该板块历史行情。"},
            "start_date": {"type": "string", "description": "开始日期，格式 YYYYMMDD（可选）"},
            "end_date": {"type": "string", "description": "结束日期，格式 YYYYMMDD（可选）"},
        },
        "required": [],
    },
)
def get_ths_daily(
    trade_date: str = None,
    ts_code: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
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
    df = pro.ths_daily(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = ["ts_code", "trade_date", "close", "open", "high", "low", "pct_change", "vol", "turnover_rate"]
    fields = [f for f in fields if f in df.columns]
    if trade_date:
        if "pct_change" in df.columns:
            df = df.sort_values("pct_change", ascending=False)
        return {"data": df[fields].head(30).to_dict("records")}
    else:
        return {"data": df[fields].head(20).to_dict("records")}
