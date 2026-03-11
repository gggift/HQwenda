# HQwenda 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于 DeepSeek Function Calling 的金融行情数据智能问答系统，支持自然语言查询股票数据并返回分析结果。

**Architecture:** 用户通过 FastAPI Web 界面发送自然语言问题，经过意图识别和上下文组装后，交给 DeepSeek Agent 自主调用 Tushare 数据接口获取数据，最终生成自然语言回答。会话历史保存在内存中，知识库通过关键词匹配检索。

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, openai SDK (DeepSeek兼容), tushare, pandas, pytest

**Spec:** `docs/superpowers/specs/2026-03-11-hqwenda-design.md`

---

## File Structure

```
HQwenda/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 入口，挂载路由和静态文件
│   ├── config.py                # 配置加载（.env）
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py              # 对话 API 接口
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py              # Agent 核心循环（DeepSeek function calling）
│   │   ├── intent.py            # 意图识别 + 实体抽取
│   │   └── context.py           # 上下文组装
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py          # Tool 注册机制
│   │   ├── quotes.py            # 行情类 Tool
│   │   ├── index.py             # 指数类 Tool
│   │   ├── fundamental.py       # 基本面类 Tool
│   │   ├── concept.py           # 概念板块类 Tool
│   │   └── utils_tool.py        # 辅助类 Tool（股票信息、日历、计算）
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── loader.py            # 知识库加载与检索
│   │   └── docs/                # 知识文档（Markdown + tags）
│   │       ├── indicators/
│   │       │   ├── pe.md
│   │       │   └── roe.md
│   │       └── market_basics/
│   │           └── index_intro.md
│   └── session/
│       ├── __init__.py
│       └── manager.py           # 会话管理
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_registry.py
│   ├── test_quotes.py
│   ├── test_index_tools.py
│   ├── test_fundamental.py
│   ├── test_concept.py
│   ├── test_utils_tool.py
│   ├── test_session.py
│   ├── test_knowledge.py
│   ├── test_intent.py
│   ├── test_context.py
│   ├── test_agent_core.py
│   └── test_api.py
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## Chunk 1: Project Foundation

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `pytest.ini`
- Create: `app/__init__.py`, `app/api/__init__.py`, `app/agent/__init__.py`, `app/tools/__init__.py`, `app/knowledge/__init__.py`, `app/session/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn==0.30.0
openai==1.50.0
tushare==1.4.2
pandas==2.2.0
pydantic-settings==2.5.0
python-dotenv==1.0.1
pytest==8.3.0
httpx==0.27.0
```

- [ ] **Step 2: Create .env.example**

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
TUSHARE_TOKEN=your_tushare_token_here
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

- [ ] **Step 4: Create empty __init__.py files**

Create empty files:
- `app/__init__.py`
- `app/api/__init__.py`
- `app/agent/__init__.py`
- `app/tools/__init__.py`
- `app/knowledge/__init__.py`
- `app/session/__init__.py`
- `tests/__init__.py`

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 6: Commit**

```bash
git init
printf ".env\n__pycache__\n*.pyc\n.pytest_cache\n" > .gitignore
git add -A
git commit -m "chore: project setup with dependencies"
```

---

### Task 2: Config Module

**Files:**
- Create: `app/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_config.py`:

```python
import os
import pytest


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.test.com")
    monkeypatch.setenv("DEEPSEEK_MODEL", "test-model")
    monkeypatch.setenv("TUSHARE_TOKEN", "test-token")

    # Re-import to pick up env vars
    from app.config import Settings

    s = Settings()
    assert s.deepseek_api_key == "test-key"
    assert s.deepseek_base_url == "https://api.test.com"
    assert s.deepseek_model == "test-model"
    assert s.tushare_token == "test-token"
    assert s.max_history_rounds == 20


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    monkeypatch.setenv("TUSHARE_TOKEN", "t")

    from app.config import Settings

    s = Settings()
    assert s.deepseek_base_url == "https://api.deepseek.com"
    assert s.deepseek_model == "deepseek-chat"
    assert s.max_history_rounds == 20
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.config'`

- [ ] **Step 3: Write minimal implementation**

Create `app/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    tushare_token: str
    max_history_rounds: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/config.py tests/test_config.py
git commit -m "feat: add config module with pydantic-settings"
```

---

### Task 3: Tool Registry

**Files:**
- Create: `app/tools/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_registry.py`:

```python
from app.tools.registry import tool, get_tool_schemas, execute_tool, _TOOL_REGISTRY, _TOOL_SCHEMAS


def setup_function():
    """Clear registry before each test."""
    _TOOL_REGISTRY.clear()
    _TOOL_SCHEMAS.clear()


def test_register_tool():
    @tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "A number"},
            },
            "required": ["x"],
        },
    )
    def test_tool(x: int) -> dict:
        return {"result": x * 2}

    schemas = get_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "test_tool"
    assert schemas[0]["function"]["description"] == "A test tool"


def test_execute_tool():
    @tool(
        name="add_tool",
        description="Adds numbers",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    )
    def add_tool(a: int, b: int) -> dict:
        return {"sum": a + b}

    result = execute_tool("add_tool", '{"a": 3, "b": 5}')
    assert '"sum": 8' in result


def test_execute_unknown_tool():
    result = execute_tool("nonexistent", '{}')
    assert "error" in result
    assert "Unknown tool" in result


def test_execute_tool_with_exception():
    @tool(
        name="bad_tool",
        description="Raises error",
        parameters={"type": "object", "properties": {}},
    )
    def bad_tool() -> dict:
        raise ValueError("something broke")

    result = execute_tool("bad_tool", '{}')
    assert "error" in result
    assert "something broke" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_registry.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

Create `app/tools/registry.py`:

```python
import json
from typing import Callable

_TOOL_REGISTRY: dict[str, Callable] = {}
_TOOL_SCHEMAS: list[dict] = []


def tool(name: str, description: str, parameters: dict):
    """Decorator to register a function as an agent tool."""

    def decorator(func: Callable):
        _TOOL_REGISTRY[name] = func
        _TOOL_SCHEMAS.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            }
        )
        return func

    return decorator


def get_tool_schemas() -> list[dict]:
    """Return all registered tool schemas for LLM function calling."""
    return _TOOL_SCHEMAS


def execute_tool(name: str, arguments: str) -> str:
    """Execute a registered tool by name with JSON arguments string."""
    func = _TOOL_REGISTRY.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
    try:
        args = json.loads(arguments)
        result = func(**args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_registry.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add app/tools/registry.py tests/test_registry.py
git commit -m "feat: add tool registry with decorator-based registration"
```

---

### Task 4: FastAPI Skeleton

**Files:**
- Create: `app/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_main.py`:

```python
from fastapi.testclient import TestClient


def test_health_endpoint():
    from app.main import app

    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_main.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create FastAPI app entry point**

Create `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="HQwenda", description="金融行情数据智能问答系统")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_main.py -v
```

Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add app/main.py tests/test_main.py
git commit -m "feat: add FastAPI app skeleton"
```

---

## Chunk 2: Tool Layer

### Task 5: Utils Tool (Stock Basic Info + Calculate)

**Files:**
- Create: `app/tools/utils_tool.py`
- Create: `tests/test_utils_tool.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_utils_tool.py`:

```python
from unittest.mock import patch, MagicMock
import pandas as pd


def test_get_stock_basic_by_name():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ"],
            "name": ["平安银行"],
            "industry": ["银行"],
            "list_date": ["19910403"],
        }
    )

    with patch("app.tools.utils_tool._get_pro") as mock_pro:
        mock_pro.return_value.stock_basic.return_value = mock_df
        from app.tools.utils_tool import get_stock_basic

        result = get_stock_basic(name="平安银行")
        assert result["data"][0]["ts_code"] == "000001.SZ"
        assert result["data"][0]["name"] == "平安银行"


def test_get_stock_basic_by_code():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["600519.SH"],
            "name": ["贵州茅台"],
            "industry": ["白酒"],
            "list_date": ["20010827"],
        }
    )

    with patch("app.tools.utils_tool._get_pro") as mock_pro:
        mock_pro.return_value.stock_basic.return_value = mock_df
        from app.tools.utils_tool import get_stock_basic

        result = get_stock_basic(ts_code="600519.SH")
        assert result["data"][0]["name"] == "贵州茅台"


def test_get_trade_calendar():
    mock_df = pd.DataFrame(
        {
            "cal_date": ["20240101", "20240102", "20240103"],
            "is_open": [0, 1, 1],
        }
    )

    with patch("app.tools.utils_tool._get_pro") as mock_pro:
        mock_pro.return_value.trade_cal.return_value = mock_df
        from app.tools.utils_tool import get_trade_calendar

        result = get_trade_calendar(start_date="20240101", end_date="20240103")
        assert len(result["data"]) == 3


def test_calculate_metric_pct_change():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(
        operation="pct_change", values=[100, 110]
    )
    assert result["result"] == 10.0


def test_calculate_metric_average():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="average", values=[10, 20, 30])
    assert result["result"] == 20.0


def test_calculate_metric_max():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="max", values=[5, 15, 10])
    assert result["result"] == 15


def test_calculate_metric_min():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="min", values=[5, 15, 10])
    assert result["result"] == 5


def test_calculate_metric_unknown():
    from app.tools.utils_tool import calculate_metric

    result = calculate_metric(operation="unknown_op", values=[1, 2])
    assert "error" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_utils_tool.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

Create `app/tools/utils_tool.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_utils_tool.py -v
```

Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add app/tools/utils_tool.py tests/test_utils_tool.py
git commit -m "feat: add utils tools (stock basic, trade calendar, calculate)"
```

---

### Task 6: Quotes Tools

**Files:**
- Create: `app/tools/quotes.py`
- Create: `tests/test_quotes.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_quotes.py`:

```python
from unittest.mock import patch
import pandas as pd


def test_get_daily_quotes():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301", "20240304"],
            "open": [10.0, 10.5],
            "high": [10.8, 11.0],
            "low": [9.8, 10.2],
            "close": [10.5, 10.8],
            "vol": [100000, 120000],
            "pct_chg": [1.5, 2.86],
        }
    )

    with patch("app.tools.quotes._get_pro") as mock_pro:
        mock_pro.return_value.daily.return_value = mock_df
        from app.tools.quotes import get_daily_quotes

        result = get_daily_quotes(ts_code="000001.SZ", start_date="20240301", end_date="20240304")
        assert len(result["data"]) == 2
        assert result["data"][0]["close"] == 10.5


def test_get_daily_quotes_empty():
    with patch("app.tools.quotes._get_pro") as mock_pro:
        mock_pro.return_value.daily.return_value = pd.DataFrame()
        from app.tools.quotes import get_daily_quotes

        result = get_daily_quotes(ts_code="000001.SZ")
        assert result["data"] == []


def test_get_weekly_monthly():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301"],
            "open": [10.0],
            "high": [11.0],
            "low": [9.5],
            "close": [10.8],
            "vol": [500000],
            "pct_chg": [3.0],
        }
    )

    with patch("app.tools.quotes._get_pro") as mock_pro:
        mock_pro.return_value.weekly.return_value = mock_df
        from app.tools.quotes import get_weekly_monthly

        result = get_weekly_monthly(ts_code="000001.SZ", freq="weekly")
        assert len(result["data"]) == 1


def test_get_realtime_quote():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ"],
            "name": ["平安银行"],
            "open": [10.0],
            "pre_close": [9.8],
            "price": [10.5],
            "high": [10.8],
            "low": [9.9],
            "vol": [50000],
            "amount": [52000],
        }
    )

    with patch("app.tools.quotes.ts") as mock_ts:
        mock_ts.realtime_quote.return_value = mock_df
        from app.tools.quotes import get_realtime_quote

        result = get_realtime_quote(ts_code="000001.SZ")
        assert result["data"][0]["price"] == 10.5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_quotes.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/tools/quotes.py`:

```python
import tushare as ts
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro

QUOTE_FIELDS = ["trade_date", "open", "high", "low", "close", "vol", "pct_chg"]


@tool(
    name="get_daily_quotes",
    description="获取股票日K线数据，包括开盘价、最高价、最低价、收盘价、成交量、涨跌幅。默认返回最近20个交易日。",
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
    return {"data": df[QUOTE_FIELDS].to_dict("records")}


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
    df = ts.realtime_quote(ts_code=ts_code)
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["ts_code", "name", "open", "pre_close", "price", "high", "low", "vol", "amount"] if c in df.columns]
    return {"data": df[fields].to_dict("records")}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_quotes.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add app/tools/quotes.py tests/test_quotes.py
git commit -m "feat: add quotes tools (daily, weekly/monthly, realtime)"
```

---

### Task 7: Index Tools

**Files:**
- Create: `app/tools/index.py`
- Create: `tests/test_index_tools.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_index_tools.py`:

```python
from unittest.mock import patch
import pandas as pd


def test_get_index_daily():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301"],
            "open": [3000.0],
            "high": [3050.0],
            "low": [2980.0],
            "close": [3020.0],
            "vol": [30000000],
            "pct_chg": [0.5],
        }
    )

    with patch("app.tools.index._get_pro") as mock_pro:
        mock_pro.return_value.index_daily.return_value = mock_df
        from app.tools.index import get_index_daily

        result = get_index_daily(ts_code="000001.SH")
        assert len(result["data"]) == 1
        assert result["data"][0]["close"] == 3020.0


def test_get_index_weight():
    mock_df = pd.DataFrame(
        {
            "con_code": ["600519.SH", "000858.SZ"],
            "con_name": ["贵州茅台", "五粮液"],
            "weight": [5.2, 2.1],
        }
    )

    with patch("app.tools.index._get_pro") as mock_pro:
        mock_pro.return_value.index_weight.return_value = mock_df
        from app.tools.index import get_index_weight

        result = get_index_weight(index_code="000300.SH")
        assert len(result["data"]) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_index_tools.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/tools/index.py`:

```python
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_index_daily",
    description="获取指数日行情数据（如上证指数、深证成指、创业板指等）。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "指数代码，如 000001.SH（上证综指）、399001.SZ（深证成指）、399006.SZ（创业板指）",
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
def get_index_daily(
    ts_code: str, start_date: str = None, end_date: str = None
) -> dict:
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
    fields = ["trade_date", "open", "high", "low", "close", "vol", "pct_chg"]
    return {"data": df[fields].to_dict("records")}


@tool(
    name="get_index_weight",
    description="获取指数成分股及权重。",
    parameters={
        "type": "object",
        "properties": {
            "index_code": {
                "type": "string",
                "description": "指数代码，如 000300.SH（沪深300）",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD（可选，默认最新）",
            },
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_index_tools.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/tools/index.py tests/test_index_tools.py
git commit -m "feat: add index tools (daily, weight)"
```

---

### Task 8: Fundamental Tools

**Files:**
- Create: `app/tools/fundamental.py`
- Create: `tests/test_fundamental.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_fundamental.py`:

```python
from unittest.mock import patch
import pandas as pd


def test_get_daily_basic():
    mock_df = pd.DataFrame(
        {
            "trade_date": ["20240301"],
            "ts_code": ["000001.SZ"],
            "pe": [8.5],
            "pb": [0.9],
            "ps": [1.2],
            "total_mv": [300000],
            "circ_mv": [280000],
        }
    )

    with patch("app.tools.fundamental._get_pro") as mock_pro:
        mock_pro.return_value.daily_basic.return_value = mock_df
        from app.tools.fundamental import get_daily_basic

        result = get_daily_basic(ts_code="000001.SZ")
        assert result["data"][0]["pe"] == 8.5


def test_get_financial_indicator():
    mock_df = pd.DataFrame(
        {
            "end_date": ["20231231"],
            "roe": [12.5],
            "roa": [1.2],
            "grossprofit_margin": [35.0],
            "netprofit_margin": [28.0],
        }
    )

    with patch("app.tools.fundamental._get_pro") as mock_pro:
        mock_pro.return_value.fina_indicator.return_value = mock_df
        from app.tools.fundamental import get_financial_indicator

        result = get_financial_indicator(ts_code="000001.SZ")
        assert result["data"][0]["roe"] == 12.5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_fundamental.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/tools/fundamental.py`:

```python
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_daily_basic",
    description="获取股票每日基本指标，包括市盈率(PE)、市净率(PB)、市销率(PS)、总市值、流通市值等。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式 YYYYMMDD（可选，默认最新）",
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
def get_daily_basic(
    ts_code: str,
    trade_date: str = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    pro = _get_pro()
    kwargs = {"ts_code": ts_code, "fields": "trade_date,ts_code,pe,pb,ps,total_mv,circ_mv"}
    if trade_date:
        kwargs["trade_date"] = trade_date
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    df = pro.daily_basic(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    return {"data": df.head(20).to_dict("records")}


@tool(
    name="get_financial_indicator",
    description="获取股票财务指标，包括ROE、ROA、毛利率、净利率等。",
    parameters={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
            "period": {
                "type": "string",
                "description": "报告期，格式 YYYYMMDD，如 20231231（可选）",
            },
        },
        "required": ["ts_code"],
    },
)
def get_financial_indicator(ts_code: str, period: str = None) -> dict:
    pro = _get_pro()
    kwargs = {
        "ts_code": ts_code,
        "fields": "end_date,roe,roa,grossprofit_margin,netprofit_margin",
    }
    if period:
        kwargs["period"] = period
    df = pro.fina_indicator(**kwargs)
    if df.empty:
        return {"data": [], "message": "无数据"}
    return {"data": df.head(8).to_dict("records")}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_fundamental.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/tools/fundamental.py tests/test_fundamental.py
git commit -m "feat: add fundamental tools (daily basic, financial indicator)"
```

---

### Task 9: Concept Tools

**Files:**
- Create: `app/tools/concept.py`
- Create: `tests/test_concept.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_concept.py`:

```python
from unittest.mock import patch
import pandas as pd


def test_get_concept_list():
    mock_df = pd.DataFrame(
        {
            "code": ["TS001", "TS002"],
            "name": ["人工智能", "新能源"],
        }
    )

    with patch("app.tools.concept._get_pro") as mock_pro:
        mock_pro.return_value.concept.return_value = mock_df
        from app.tools.concept import get_concept_list

        result = get_concept_list()
        assert len(result["data"]) == 2


def test_get_concept_stocks():
    mock_df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "600000.SH"],
            "name": ["平安银行", "浦发银行"],
        }
    )

    with patch("app.tools.concept._get_pro") as mock_pro:
        mock_pro.return_value.concept_detail.return_value = mock_df
        from app.tools.concept import get_concept_stocks

        result = get_concept_stocks(concept_id="TS001")
        assert len(result["data"]) == 2


def test_get_stock_concepts():
    mock_df = pd.DataFrame(
        {
            "id": ["TS001", "TS002"],
            "concept_name": ["人工智能", "大数据"],
            "ts_code": ["000001.SZ", "000001.SZ"],
        }
    )

    with patch("app.tools.concept._get_pro") as mock_pro:
        mock_pro.return_value.concept_detail.return_value = mock_df
        from app.tools.concept import get_stock_concepts

        result = get_stock_concepts(ts_code="000001.SZ")
        assert len(result["data"]) == 2
        assert result["data"][0]["concept_name"] == "人工智能"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_concept.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/tools/concept.py`:

```python
from app.tools.registry import tool
from app.tools.utils_tool import _get_pro


@tool(
    name="get_concept_list",
    description="获取概念板块列表。",
    parameters={
        "type": "object",
        "properties": {},
    },
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
            "concept_id": {
                "type": "string",
                "description": "概念板块ID，如 TS001。可先用 get_concept_list 查询。",
            },
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
            "ts_code": {
                "type": "string",
                "description": "股票代码，如 000001.SZ",
            },
        },
        "required": ["ts_code"],
    },
)
def get_stock_concepts(ts_code: str) -> dict:
    pro = _get_pro()
    # concept_detail supports filtering by ts_code in some Tushare versions
    # Fall back to fetching all concepts if needed
    try:
        df = pro.concept_detail(ts_code=ts_code)
    except Exception:
        return {"data": [], "message": "该接口暂不支持按股票代码查询"}
    if df.empty:
        return {"data": [], "message": "无数据"}
    fields = [c for c in ["id", "concept_name"] if c in df.columns]
    return {"data": df[fields].to_dict("records")}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_concept.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add app/tools/concept.py tests/test_concept.py
git commit -m "feat: add concept tools (list, stocks, stock concepts)"
```

---

### Task 10: Tool Auto-Import

**Files:**
- Modify: `app/tools/__init__.py`

- [ ] **Step 1: Set up auto-import so all tools register on startup**

Edit `app/tools/__init__.py`:

```python
# Import all tool modules to trigger @tool decorator registration
from app.tools import utils_tool  # noqa: F401
from app.tools import quotes  # noqa: F401
from app.tools import index  # noqa: F401
from app.tools import fundamental  # noqa: F401
from app.tools import concept  # noqa: F401
```

- [ ] **Step 2: Verify all tools are registered**

```bash
python -c "
import app.tools
from app.tools.registry import get_tool_schemas
schemas = get_tool_schemas()
print(f'Registered {len(schemas)} tools:')
for s in schemas:
    print(f'  - {s[\"function\"][\"name\"]}')
"
```

Expected: 13 tools registered (get_stock_basic, get_trade_calendar, calculate_metric, get_daily_quotes, get_weekly_monthly, get_realtime_quote, get_index_daily, get_index_weight, get_daily_basic, get_financial_indicator, get_concept_list, get_concept_stocks, get_stock_concepts)

- [ ] **Step 3: Commit**

```bash
git add app/tools/__init__.py
git commit -m "feat: auto-import all tool modules for registration"
```

---

## Chunk 3: Session & Knowledge

### Task 11: Session Manager

**Files:**
- Create: `app/session/manager.py`
- Create: `tests/test_session.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_session.py`:

```python
from app.session.manager import SessionManager


def test_create_session():
    sm = SessionManager()
    sid = sm.create_session()
    assert isinstance(sid, str)
    assert len(sid) > 0


def test_add_and_get_history():
    sm = SessionManager()
    sid = sm.create_session()
    sm.add_message(sid, "user", "hello")
    sm.add_message(sid, "assistant", "hi")
    history = sm.get_history(sid)
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "hello"}
    assert history[1] == {"role": "assistant", "content": "hi"}


def test_history_truncation():
    sm = SessionManager(max_rounds=2)
    sid = sm.create_session()
    # Add 3 rounds (6 messages), should keep only last 2 rounds (4 messages)
    for i in range(3):
        sm.add_message(sid, "user", f"q{i}")
        sm.add_message(sid, "assistant", f"a{i}")
    history = sm.get_history(sid)
    assert len(history) == 4
    assert history[0]["content"] == "q1"


def test_delete_session():
    sm = SessionManager()
    sid = sm.create_session()
    sm.add_message(sid, "user", "test")
    sm.delete_session(sid)
    history = sm.get_history(sid)
    assert history == []


def test_get_history_nonexistent():
    sm = SessionManager()
    history = sm.get_history("nonexistent")
    assert history == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_session.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/session/manager.py`:

```python
import uuid


class SessionManager:
    def __init__(self, max_rounds: int = 20):
        self._sessions: dict[str, list[dict]] = {}
        self._max_rounds = max_rounds

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        return session_id

    def get_history(self, session_id: str) -> list[dict]:
        return list(self._sessions.get(session_id, []))

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})
        max_messages = self._max_rounds * 2
        if len(self._sessions[session_id]) > max_messages:
            self._sessions[session_id] = self._sessions[session_id][-max_messages:]

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_session.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add app/session/manager.py tests/test_session.py
git commit -m "feat: add session manager with history truncation"
```

---

### Task 12: Knowledge Base

**Files:**
- Create: `app/knowledge/loader.py`
- Create: `app/knowledge/docs/indicators/pe.md`
- Create: `app/knowledge/docs/indicators/roe.md`
- Create: `app/knowledge/docs/market_basics/index_intro.md`
- Create: `tests/test_knowledge.py`

- [ ] **Step 1: Create sample knowledge docs**

Create `app/knowledge/docs/indicators/pe.md`:

```markdown
# 市盈率 (PE)

tags: PE, 市盈率, 估值, 盈利

---

市盈率（Price-to-Earnings Ratio，PE）= 股价 / 每股收益（EPS）

**含义：** 投资者愿意为每1元利润支付的价格。PE越高表示市场对公司未来增长预期越高。

**常见分类：**
- 静态PE：基于上一年度已公布的EPS
- 动态PE（TTM）：基于最近四个季度的EPS

**参考标准（A股）：**
- PE < 15：低估值
- PE 15-25：合理估值
- PE > 25：高估值（需结合行业判断）

**注意：** 不同行业PE差异大，银行通常5-10，科技股可达50+。亏损公司PE无意义。
```

Create `app/knowledge/docs/indicators/roe.md`:

```markdown
# 净资产收益率 (ROE)

tags: ROE, 净资产收益率, 盈利能力, 财务指标

---

净资产收益率（Return on Equity，ROE）= 净利润 / 股东权益 × 100%

**含义：** 衡量公司利用股东投入资本创造利润的效率。ROE越高，说明公司盈利能力越强。

**参考标准：**
- ROE > 20%：优秀
- ROE 15-20%：良好
- ROE 10-15%：一般
- ROE < 10%：较差

**杜邦分析法拆解：**
ROE = 净利率 × 总资产周转率 × 权益乘数

巴菲特常用ROE > 15%作为选股标准之一。
```

Create `app/knowledge/docs/market_basics/index_intro.md`:

```markdown
# 主要股票指数

tags: 指数, 上证, 深证, 创业板, 沪深300

---

**上证综指（000001.SH）：** 上海证券交易所全部上市股票的加权指数，反映沪市整体表现。

**深证成指（399001.SZ）：** 深圳证券交易所500只代表性股票的加权指数。

**创业板指（399006.SZ）：** 创业板100只代表性股票的指数，偏成长型公司。

**沪深300（000300.SH）：** 沪深两市市值最大、流动性最好的300只股票，A股核心指数。

**中证500（000905.SH）：** 扣除沪深300后，市值排名前500的股票，代表中盘股表现。
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_knowledge.py`:

```python
import os
import tempfile
from pathlib import Path

from app.knowledge.loader import KnowledgeLoader


def _create_test_docs(tmp_dir: str):
    """Create test knowledge docs."""
    ind_dir = Path(tmp_dir) / "indicators"
    ind_dir.mkdir(parents=True)

    (ind_dir / "pe.md").write_text(
        "# 市盈率\n\ntags: PE, 市盈率, 估值\n\n---\n\nPE = 股价 / EPS"
    )
    (ind_dir / "roe.md").write_text(
        "# ROE\n\ntags: ROE, 净资产收益率\n\n---\n\nROE = 净利润 / 股东权益"
    )


def test_load_docs():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)
        assert len(loader._docs) == 2


def test_search_by_keyword():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)

        results = loader.search(["PE"])
        assert len(results) == 1
        assert "市盈率" in results[0].title


def test_search_multiple_keywords():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)

        results = loader.search(["PE", "估值"])
        # PE doc matches both keywords, so it should rank first
        assert len(results) >= 1
        assert "市盈率" in results[0].title


def test_search_no_match():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)

        results = loader.search(["不存在的关键词"])
        assert len(results) == 0


def test_search_max_results():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)

        results = loader.search(["ROE", "PE"], max_results=1)
        assert len(results) == 1
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_knowledge.py -v
```

Expected: FAIL

- [ ] **Step 4: Write implementation**

Create `app/knowledge/loader.py`:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KnowledgeDoc:
    title: str
    tags: list[str]
    content: str


class KnowledgeLoader:
    def __init__(self, docs_dir: str):
        self._docs: list[KnowledgeDoc] = []
        self._load_docs(docs_dir)

    def _load_docs(self, docs_dir: str):
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            return
        for md_file in docs_path.rglob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            title, tags, body = self._parse_doc(text)
            if title or body:
                self._docs.append(KnowledgeDoc(title=title, tags=tags, content=body))

    def _parse_doc(self, content: str) -> tuple[str, list[str], str]:
        lines = content.strip().split("\n")
        title = ""
        tags = []
        body_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("# ") and not title:
                title = stripped[2:].strip()
            elif stripped.startswith("tags:"):
                tags = [t.strip() for t in stripped[5:].split(",") if t.strip()]
            elif stripped == "---":
                body_start = i + 1
                break

        body = "\n".join(lines[body_start:]).strip()
        return title, tags, body

    def search(self, keywords: list[str], max_results: int = 2) -> list[KnowledgeDoc]:
        scored = []
        for doc in self._docs:
            doc_tags_lower = [t.lower() for t in doc.tags]
            score = sum(1 for kw in keywords if kw.lower() in doc_tags_lower)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:max_results]]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_knowledge.py -v
```

Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add app/knowledge/ tests/test_knowledge.py
git commit -m "feat: add knowledge base loader with keyword search"
```

---

## Chunk 4: Agent Core

### Task 13: Intent Recognition

**Files:**
- Create: `app/agent/intent.py`
- Create: `tests/test_intent.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_intent.py`:

```python
from unittest.mock import patch, MagicMock
import json


def test_recognize_intent_stock_query():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "category": "行情查询",
            "entities": {
                "stock_names": ["贵州茅台"],
                "time_range": "最近一周",
                "indicators": [],
            },
            "keywords": ["茅台", "行情"],
        }
    )

    with patch("app.agent.intent._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response
        from app.agent.intent import recognize_intent

        result = recognize_intent("贵州茅台最近一周的行情怎么样？")
        assert result["category"] == "行情查询"
        assert "贵州茅台" in result["entities"]["stock_names"]


def test_recognize_intent_invalid_json():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "这不是JSON"

    with patch("app.agent.intent._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response
        from app.agent.intent import recognize_intent

        result = recognize_intent("随便说点什么")
        assert result["category"] == "其他"
        assert result["entities"]["stock_names"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_intent.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/agent/intent.py`:

```python
import json

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        from app.config import Settings

        settings = Settings()
        _client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    return _client


INTENT_PROMPT = """你是一个金融问题分类器。分析用户问题，输出JSON：
{
  "category": "行情查询" | "概念解释" | "闲聊" | "其他",
  "entities": {
    "stock_names": ["提到的股票名称"],
    "time_range": "提到的时间范围或null",
    "indicators": ["提到的指标如PE、PB等"]
  },
  "keywords": ["用于知识库检索的关键词"]
}
只输出JSON，不要其他内容。"""

_FALLBACK = {
    "category": "其他",
    "entities": {"stock_names": [], "time_range": None, "indicators": []},
    "keywords": [],
}


def recognize_intent(message: str) -> dict:
    client = _get_client()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
        max_tokens=300,
    )
    content = response.choices[0].message.content or ""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return dict(_FALLBACK)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_intent.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/agent/intent.py tests/test_intent.py
git commit -m "feat: add intent recognition module"
```

---

### Task 14: Context Assembly

**Files:**
- Create: `app/agent/context.py`
- Create: `tests/test_context.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_context.py`:

```python
from unittest.mock import patch, MagicMock
from app.session.manager import SessionManager
from app.knowledge.loader import KnowledgeLoader, KnowledgeDoc
import tempfile


def _make_loader_with_docs():
    """Create a KnowledgeLoader with test docs."""
    tmp = tempfile.mkdtemp()
    import os
    from pathlib import Path

    ind_dir = Path(tmp) / "indicators"
    ind_dir.mkdir()
    (ind_dir / "pe.md").write_text("# PE\n\ntags: PE, 市盈率\n\n---\n\nPE解释内容")
    return KnowledgeLoader(tmp), tmp


def test_assemble_context_basic():
    sm = SessionManager()
    sid = sm.create_session()
    loader, _ = _make_loader_with_docs()

    mock_intent = {
        "category": "行情查询",
        "entities": {"stock_names": ["平安银行"], "time_range": None, "indicators": []},
        "keywords": [],
    }

    with patch("app.agent.context.recognize_intent", return_value=mock_intent):
        with patch("app.agent.context.resolve_stock_name", return_value="000001.SZ"):
            from app.agent.context import assemble_context

            system_prompt, messages = assemble_context(
                "平安银行今天怎么样", sid, sm, loader
            )
            assert "平安银行" in system_prompt
            assert "000001.SZ" in system_prompt
            assert messages[-1]["content"] == "平安银行今天怎么样"


def test_assemble_context_with_knowledge():
    sm = SessionManager()
    sid = sm.create_session()
    loader, _ = _make_loader_with_docs()

    mock_intent = {
        "category": "概念解释",
        "entities": {"stock_names": [], "time_range": None, "indicators": ["PE"]},
        "keywords": ["PE"],
    }

    with patch("app.agent.context.recognize_intent", return_value=mock_intent):
        from app.agent.context import assemble_context

        system_prompt, messages = assemble_context(
            "什么是PE？", sid, sm, loader
        )
        assert "PE解释内容" in system_prompt


def test_assemble_context_with_history():
    sm = SessionManager()
    sid = sm.create_session()
    sm.add_message(sid, "user", "你好")
    sm.add_message(sid, "assistant", "你好！")
    loader, _ = _make_loader_with_docs()

    mock_intent = {
        "category": "闲聊",
        "entities": {"stock_names": [], "time_range": None, "indicators": []},
        "keywords": [],
    }

    with patch("app.agent.context.recognize_intent", return_value=mock_intent):
        from app.agent.context import assemble_context

        system_prompt, messages = assemble_context(
            "今天天气怎么样", sid, sm, loader
        )
        assert len(messages) == 3  # 2 history + 1 new
        assert messages[0]["content"] == "你好"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_context.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/agent/context.py`:

```python
from app.agent.intent import recognize_intent
from app.knowledge.loader import KnowledgeLoader
from app.session.manager import SessionManager


def resolve_stock_name(name: str) -> str | None:
    """Try to resolve a stock name to its code using Tushare."""
    try:
        from app.tools.utils_tool import get_stock_basic

        result = get_stock_basic(name=name)
        if result.get("data"):
            return result["data"][0]["ts_code"]
    except Exception:
        pass
    return None


def assemble_context(
    message: str,
    session_id: str,
    session_manager: SessionManager,
    knowledge_loader: KnowledgeLoader,
) -> tuple[str, list[dict]]:
    """Assemble system prompt and messages for the agent.

    Returns:
        (system_prompt, messages) where messages includes history + new user message.
    """
    # 1. Intent recognition
    intent = recognize_intent(message)

    # 2. Resolve stock names to codes
    stock_codes = {}
    for name in intent.get("entities", {}).get("stock_names", []):
        code = resolve_stock_name(name)
        if code:
            stock_codes[name] = code

    # 3. Knowledge retrieval
    keywords = intent.get("keywords", [])
    knowledge_docs = knowledge_loader.search(keywords)

    # 4. Build system prompt
    system_parts = [
        "你是一个专业的金融数据分析助手。用户会问你关于股票、指数等金融数据的问题。",
        "你可以调用工具获取实时数据来回答问题。回答要准确、简洁。",
        "当用户提到股票名称时，先用 get_stock_basic 工具查找股票代码，再用代码查询数据。",
    ]

    if stock_codes:
        codes_info = "、".join(f"{n}({c})" for n, c in stock_codes.items())
        system_parts.append(f"\n已识别的股票：{codes_info}")

    if knowledge_docs:
        system_parts.append("\n相关知识：")
        for doc in knowledge_docs:
            system_parts.append(f"\n### {doc.title}\n{doc.content}")

    system_prompt = "\n".join(system_parts)

    # 5. Conversation history + new message
    history = session_manager.get_history(session_id)
    messages = list(history) + [{"role": "user", "content": message}]

    return system_prompt, messages
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_context.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add app/agent/context.py tests/test_context.py
git commit -m "feat: add context assembly with intent + knowledge + history"
```

---

### Task 15: Agent Core (DeepSeek Function Calling)

**Files:**
- Create: `app/agent/core.py`
- Create: `tests/test_agent_core.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_agent_core.py`:

```python
from unittest.mock import patch, MagicMock


def _make_text_response(text: str):
    """Create a mock response with just text (no tool calls)."""
    msg = MagicMock()
    msg.tool_calls = None
    msg.content = text
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_tool_call_response(tool_name: str, arguments: str, call_id: str = "call_1"):
    """Create a mock response with a tool call."""
    tool_call = MagicMock()
    tool_call.id = call_id
    tool_call.function.name = tool_name
    tool_call.function.arguments = arguments

    msg = MagicMock()
    msg.tool_calls = [tool_call]
    msg.content = None
    msg.model_dump.return_value = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {"name": tool_name, "arguments": arguments},
            }
        ],
    }

    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def test_agent_simple_response():
    """Agent returns text directly when no tool calls needed."""
    with patch("app.agent.core._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = _make_text_response(
            "你好！有什么可以帮你的吗？"
        )
        from app.agent.core import run_agent

        result = run_agent("你是助手", [{"role": "user", "content": "你好"}])
        assert result == "你好！有什么可以帮你的吗？"


def test_agent_with_tool_call():
    """Agent calls a tool and then returns final text."""
    tool_response = _make_tool_call_response(
        "calculate_metric", '{"operation": "average", "values": [10, 20, 30]}'
    )
    final_response = _make_text_response("平均值是20。")

    with patch("app.agent.core._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.side_effect = [
            tool_response,
            final_response,
        ]
        with patch("app.agent.core.execute_tool", return_value='{"result": 20.0}'):
            from app.agent.core import run_agent

            result = run_agent("你是助手", [{"role": "user", "content": "计算10,20,30的平均值"}])
            assert result == "平均值是20。"


def test_agent_max_iterations():
    """Agent stops after max iterations."""
    tool_response = _make_tool_call_response(
        "calculate_metric", '{"operation": "sum", "values": [1]}'
    )

    with patch("app.agent.core._get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = tool_response
        with patch("app.agent.core.execute_tool", return_value='{"result": 1}'):
            from app.agent.core import run_agent

            result = run_agent(
                "你是助手",
                [{"role": "user", "content": "test"}],
                max_iterations=2,
            )
            assert "超时" in result or "重试" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_agent_core.py -v
```

Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `app/agent/core.py`:

```python
from app.tools.registry import get_tool_schemas, execute_tool

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        from app.config import Settings

        settings = Settings()
        _client = OpenAI(
            api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url
        )
    return _client


def run_agent(
    system_prompt: str, messages: list[dict], max_iterations: int = 10
) -> str:
    """Run the agent loop with DeepSeek function calling.

    Sends messages to DeepSeek, executes any tool calls, and loops
    until a final text response is produced or max iterations reached.
    """
    from app.config import Settings

    settings = Settings()
    client = _get_client()
    tool_schemas = get_tool_schemas()

    all_messages = [{"role": "system", "content": system_prompt}] + messages

    for _ in range(max_iterations):
        kwargs = {
            "model": settings.deepseek_model,
            "messages": all_messages,
            "temperature": 0.3,
        }
        if tool_schemas:
            kwargs["tools"] = tool_schemas

        response = client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or ""

        # Append assistant message with tool calls
        all_messages.append(message.model_dump())

        # Execute each tool call and append results
        for tool_call in message.tool_calls:
            result = execute_tool(
                tool_call.function.name, tool_call.function.arguments
            )
            all_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    return "抱歉，处理超时，请稍后重试。"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_agent_core.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add app/agent/core.py tests/test_agent_core.py
git commit -m "feat: add agent core with DeepSeek function calling loop"
```

---

## Chunk 5: API & Frontend

### Task 16: Chat API

**Files:**
- Create: `app/api/chat.py`
- Modify: `app/main.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_api.py`:

```python
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@patch("app.api.chat.run_agent", return_value="测试回答")
@patch("app.api.chat.assemble_context", return_value=("system", [{"role": "user", "content": "test"}]))
def test_chat_endpoint(mock_ctx, mock_agent):
    from app.main import app

    client = TestClient(app)

    # Create session first
    resp = client.post("/api/session/new")
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # Send message
    resp = client.post(
        "/api/chat",
        json={"session_id": session_id, "message": "你好"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "测试回答"
    assert data["session_id"] == session_id


def test_new_session():
    from app.main import app

    client = TestClient(app)
    resp = client.post("/api/session/new")
    assert resp.status_code == 200
    assert "session_id" in resp.json()


def test_delete_session():
    from app.main import app

    client = TestClient(app)

    # Create then delete
    resp = client.post("/api/session/new")
    session_id = resp.json()["session_id"]

    resp = client.delete(f"/api/session/{session_id}")
    assert resp.status_code == 200
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_api.py -v
```

Expected: FAIL

- [ ] **Step 3: Write Chat API implementation**

Create `app/api/chat.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.core import run_agent
from app.agent.context import assemble_context
from app.session.manager import SessionManager
from app.knowledge.loader import KnowledgeLoader

router = APIRouter()

session_manager = SessionManager()
knowledge_loader = KnowledgeLoader("app/knowledge/docs")


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str


# Use sync def (not async def) so FastAPI runs it in a threadpool.
# run_agent and assemble_context make blocking HTTP calls to DeepSeek/Tushare.
@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    system_prompt, messages = assemble_context(
        req.message, req.session_id, session_manager, knowledge_loader
    )
    reply = run_agent(system_prompt, messages)

    # Save to session history
    session_manager.add_message(req.session_id, "user", req.message)
    session_manager.add_message(req.session_id, "assistant", reply)

    return ChatResponse(reply=reply, session_id=req.session_id)


@router.post("/api/session/new")
def new_session():
    session_id = session_manager.create_session()
    return SessionResponse(session_id=session_id)


@router.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    session_manager.delete_session(session_id)
    return {"status": "ok"}
```

- [ ] **Step 4: Update main.py to mount router and static files**

Update `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.chat import router

app = FastAPI(title="HQwenda", description="金融行情数据智能问答系统")
app.include_router(router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Static files (mount last so API routes take priority)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_api.py -v
```

Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add app/api/chat.py app/main.py tests/test_api.py
git commit -m "feat: add chat API endpoints and wire up FastAPI app"
```

---

### Task 17: Frontend - HTML

**Files:**
- Create: `static/index.html`

- [ ] **Step 1: Create the HTML page**

Create `static/index.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HQwenda - 金融行情问答</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>HQwenda</h1>
            <p class="subtitle">金融行情数据智能问答</p>
            <button id="new-session-btn" title="新建会话">+ 新会话</button>
        </header>

        <div id="chat-area">
            <div id="messages"></div>
        </div>

        <div class="input-area">
            <textarea
                id="user-input"
                placeholder="输入你的问题，如：贵州茅台最近的行情怎么样？"
                rows="2"
            ></textarea>
            <button id="send-btn">发送</button>
        </div>
    </div>

    <script src="/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify HTML is served**

```bash
python -c "
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
r = c.get('/')
assert r.status_code == 200
assert 'HQwenda' in r.text
print('OK: index.html served')
"
```

Expected: `OK: index.html served`

- [ ] **Step 3: Commit**

```bash
git add static/index.html
git commit -m "feat: add frontend HTML"
```

---

### Task 18: Frontend - CSS

**Files:**
- Create: `static/style.css`

- [ ] **Step 1: Create the stylesheet**

Create `static/style.css`:

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f5;
    color: #333;
    height: 100vh;
    display: flex;
    justify-content: center;
}

.container {
    width: 100%;
    max-width: 800px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #fff;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

header {
    padding: 16px 20px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    gap: 12px;
}

header h1 {
    font-size: 20px;
    color: #1a73e8;
}

.subtitle {
    color: #666;
    font-size: 14px;
    flex: 1;
}

#new-session-btn {
    padding: 6px 14px;
    background: #1a73e8;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
}

#new-session-btn:hover {
    background: #1557b0;
}

#chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

#messages {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.message {
    max-width: 85%;
    padding: 12px 16px;
    border-radius: 12px;
    line-height: 1.6;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
}

.message.user {
    align-self: flex-end;
    background: #1a73e8;
    color: #fff;
    border-bottom-right-radius: 4px;
}

.message.assistant {
    align-self: flex-start;
    background: #f0f0f0;
    color: #333;
    border-bottom-left-radius: 4px;
}

.message.assistant table {
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 13px;
    width: 100%;
}

.message.assistant th,
.message.assistant td {
    border: 1px solid #ddd;
    padding: 4px 8px;
    text-align: right;
}

.message.assistant th {
    background: #e8e8e8;
    text-align: center;
}

.message.loading::after {
    content: "...";
    animation: dots 1.5s infinite;
}

@keyframes dots {
    0%, 20% { content: "."; }
    40% { content: ".."; }
    60%, 100% { content: "..."; }
}

.input-area {
    padding: 16px 20px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    gap: 10px;
}

#user-input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    resize: none;
    font-family: inherit;
    outline: none;
}

#user-input:focus {
    border-color: #1a73e8;
}

#send-btn {
    padding: 10px 20px;
    background: #1a73e8;
    color: #fff;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    align-self: flex-end;
}

#send-btn:hover {
    background: #1557b0;
}

#send-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}
```

- [ ] **Step 2: Verify CSS is served**

```bash
python -c "
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
r = c.get('/style.css')
assert r.status_code == 200
print('OK: style.css served')
"
```

Expected: `OK: style.css served`

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: add frontend CSS"
```

---

### Task 19: Frontend - JavaScript

**Files:**
- Create: `static/app.js`

- [ ] **Step 1: Create the JavaScript**

Create `static/app.js`:

```javascript
const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newSessionBtn = document.getElementById("new-session-btn");

let sessionId = null;

async function createSession() {
  const resp = await fetch("/api/session/new", { method: "POST" });
  const data = await resp.json();
  sessionId = data.session_id;
  messagesEl.innerHTML = "";
}

function addMessage(role, content) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = renderMarkdown(content);
  messagesEl.appendChild(div);
  messagesEl.parentElement.scrollTop = messagesEl.parentElement.scrollHeight;
  return div;
}

function renderMarkdown(text) {
  // Simple markdown: bold, tables, code blocks
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");

  // Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Simple table detection (lines with |)
  const lines = html.split("\n");
  let inTable = false;
  const result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith("|") && line.endsWith("|")) {
      if (!inTable) {
        result.push("<table>");
        inTable = true;
        // Header row
        const cells = line.split("|").filter((c) => c.trim());
        result.push("<tr>" + cells.map((c) => `<th>${c.trim()}</th>`).join("") + "</tr>");
      } else if (line.replace(/[|\-\s:]/g, "") === "") {
        // Separator row, skip
        continue;
      } else {
        const cells = line.split("|").filter((c) => c.trim());
        result.push("<tr>" + cells.map((c) => `<td>${c.trim()}</td>`).join("") + "</tr>");
      }
    } else {
      if (inTable) {
        result.push("</table>");
        inTable = false;
      }
      result.push(line);
    }
  }
  if (inTable) result.push("</table>");

  return result.join("\n");
}

async function sendMessage() {
  const message = inputEl.value.trim();
  if (!message) return;

  if (!sessionId) await createSession();

  addMessage("user", message);
  inputEl.value = "";
  sendBtn.disabled = true;

  const loadingDiv = addMessage("assistant", "思考中");
  loadingDiv.classList.add("loading");

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    const data = await resp.json();
    loadingDiv.classList.remove("loading");
    loadingDiv.innerHTML = renderMarkdown(data.reply);
  } catch (err) {
    loadingDiv.classList.remove("loading");
    loadingDiv.textContent = "请求失败，请稍后重试。";
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

sendBtn.addEventListener("click", sendMessage);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

newSessionBtn.addEventListener("click", createSession);

// Initialize
createSession();
```

- [ ] **Step 2: Verify JS is served**

```bash
python -c "
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
r = c.get('/app.js')
assert r.status_code == 200
assert 'createSession' in r.text
print('OK: app.js served')
"
```

Expected: `OK: app.js served`

- [ ] **Step 3: Commit**

```bash
git add static/app.js
git commit -m "feat: add frontend JavaScript"
```

---

### Task 20: Integration Smoke Test

- [ ] **Step 1: Run all unit tests**

```bash
pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 2: Verify app starts**

Create `.env` with real API keys (or test keys):

```bash
cp .env.example .env
# Edit .env with your real keys
```

```bash
uvicorn app.main:app --reload &
sleep 2

# Test health
curl http://localhost:8000/api/health

# Test session creation
curl -X POST http://localhost:8000/api/session/new

# Test frontend loads
curl -s http://localhost:8000/ | head -5

kill %1
```

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: integration verification complete"
```

---

## Summary

| Chunk | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-4 | Project setup, config, tool registry, FastAPI skeleton |
| 2 | 5-10 | All Tushare tool implementations (utils, quotes, index, fundamental, concept) |
| 3 | 11-12 | Session manager, knowledge base |
| 4 | 13-15 | Intent recognition, context assembly, agent core |
| 5 | 16-20 | Chat API, frontend (HTML/CSS/JS), integration test |

Total: 20 tasks, ~80 steps
