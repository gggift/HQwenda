# HQwenda - 结构化行情数据Agent问答系统 设计文档

## 概述

基于 DeepSeek Function Calling 的金融行情数据智能问答系统。用户通过自然语言提问，Agent 自主调用 Tushare 数据接口获取数据，进行简单分析后以自然语言回答。支持多轮对话。

## 整体架构

```
用户 ──→ FastAPI (Web API + 简单前端)
              │
              ▼
         对话管理层
              ├── 意图识别 (LLM轻量调用)
              │     ├── 问题分类：行情查询 / 概念解释 / 闲聊 / 其他
              │     └── 实体抽取：股票名→代码、时间范围、指标类型
              │
              ├── 知识载入 (金融知识库)
              │     ├── 指标定义（PE/PB/ROE等）
              │     ├── 常见分析方法（均线分析、估值对比等）
              │     └── 检索方式：关键词匹配
              │
              └── 上下文组装
                    ├── 会话历史（内存，按session_id）
                    ├── 意图+实体信息
                    └── 相关知识片段
              │
              ▼
         Agent核心 (DeepSeek Function Calling)
              │
              ▼
         Tool层 (Tushare封装)
              │
              ▼
         Tushare API
```

### 核心流程

1. 用户发送自然语言问题
2. 意图识别：LLM 轻量调用，分类问题类型并抽取实体（股票名→代码、时间范围、指标）
3. 知识载入：根据意图/实体关键词匹配相关金融知识片段
4. 上下文组装：会话历史 + 意图信息 + 知识片段，拼装后交给 Agent
5. Agent（DeepSeek）决定调用哪些 Tool、传什么参数
6. Tool 层调用 Tushare 获取数据，返回精简结构化结果
7. Agent 根据数据生成自然语言回答
8. 如需多步查询，Agent 连续调用多个 Tool 后汇总回答

### 对话上下文

- 内存存储，按 session_id 索引消息列表
- 最大保留 20 轮，超出截断最早消息

## Tool层设计

### 行情类
- `get_daily_quotes` — 日K线数据（开高低收、成交量）
- `get_weekly_monthly` — 周K/月K数据
- `get_realtime_quote` — 最新实时行情

### 指数类
- `get_index_daily` — 指数日行情（上证、深证、创业板等）
- `get_index_weight` — 指数成分股及权重

### 基本面类
- `get_daily_basic` — 每日指标（PE、PB、PS、总市值、流通市值等）
- `get_financial_indicator` — 财务指标（ROE、ROA、毛利率等）

### 概念板块类
- `get_concept_list` — 概念板块列表
- `get_concept_stocks` — 概念板块成分股
- `get_stock_concepts` — 个股所属概念

### 辅助类
- `get_stock_basic` — 股票基础信息（名称↔代码映射、上市日期、行业）
- `get_trade_calendar` — 交易日历
- `calculate_metric` — 简单计算工具（涨跌幅、均值、排名等，本地执行）

### Tool 设计原则
- 参数由 Agent 传入（股票代码、起止日期、指标字段等）
- 返回精简结构化数据，只保留必要字段，控制 token 消耗
- 统一错误处理，返回明确错误信息让 Agent 能向用户解释

## 知识库设计

### 内容组织

```
knowledge/docs/
├── indicators/          # 指标类
│   ├── pe.md            # 市盈率
│   ├── pb.md            # 市净率
│   ├── roe.md           # 净资产收益率
│   └── ...
├── analysis_methods/    # 分析方法类
│   ├── moving_average.md    # 均线分析
│   ├── valuation.md         # 估值对比
│   └── ...
└── market_basics/       # 市场基础知识
    ├── index_intro.md       # 主要指数介绍
    ├── trading_rules.md     # 交易规则
    └── concept_sectors.md   # 概念板块知识
```

### 检索方式
- 关键词匹配：每个知识片段带 tags 元数据
- 从意图识别提取的实体/关键词匹配知识文件标签
- 命中后拼入 system prompt，单次最多 2 个片段
- 手动编写和维护

## API设计

```
POST /api/chat           # 发送消息，返回回答
  body: { session_id, message }
  response: { reply, session_id }

POST /api/session/new    # 创建新会话
DELETE /api/session/{id} # 清除会话历史
```

## 前端

- FastAPI 静态文件服务，单页对话界面
- 对话框：上方历史消息，下方输入框
- 支持 Markdown 渲染（表格数据友好展示）
- 新建会话按钮
- 原生 HTML + CSS + JS，不引入前端框架

## 项目结构

```
HQwenda/
├── app/
│   ├── main.py              # FastAPI入口
│   ├── api/
│   │   └── chat.py          # 对话API接口
│   ├── agent/
│   │   ├── core.py          # Agent核心，DeepSeek Function Calling
│   │   ├── intent.py        # 意图识别 + 实体抽取
│   │   └── context.py       # 上下文组装
│   ├── tools/
│   │   ├── registry.py      # Tool注册与定义
│   │   ├── quotes.py        # 行情类Tool
│   │   ├── index.py         # 指数类Tool
│   │   ├── fundamental.py   # 基本面类Tool
│   │   ├── concept.py       # 概念板块类Tool
│   │   └── utils.py         # 辅助类Tool
│   ├── knowledge/
│   │   ├── loader.py        # 知识库加载与检索
│   │   └── docs/            # 知识文档
│   ├── session/
│   │   └── manager.py       # 会话管理
│   └── config.py            # 配置
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
└── .env                     # API keys
```

## 技术栈

- `fastapi` + `uvicorn` — Web服务
- `openai` — 调用DeepSeek API（兼容OpenAI格式）
- `tushare` + `pandas` — 数据获取与处理

## 关键设计决策

- 意图识别与 Agent 调用分两次 LLM 请求，意图识别用轻量 prompt 控制成本
- 会话历史限制最近 20 轮，超出截断最早消息
- Tool 返回数据做精简，控制 token 消耗
- 知识片段注入做长度限制，单次最多 2 个片段
- `.env` 管理敏感配置，不入版本控制

## 不做的事情（YAGNI）

- 不做用户体系和权限
- 不做数据持久化缓存（每次实时查 Tushare）
- 不做向量数据库（关键词匹配够用）
- 不做流式输出（后续可加，前期不需要）
