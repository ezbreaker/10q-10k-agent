# InsightAgent MVP

一个简单而强大的FastAPI应用程序，用于从SEC EDGAR数据库检索财务报告并提取特定财务指标数据。

## 🚀 新功能特性

- 🔍 **多年度支持**: 按年份检索历史10-K和10-Q财报
- 📊 **灵活指标提取**: 支持多种财务指标，不仅限于收入
- 🎯 **智能标签映射**: 自动将常用指标名称映射到XBRL标签
- 🚀 **RESTful API**: 提供完整的Web服务接口
- ⚙️ **配置化管理**: 集中的超参数和配置管理
- 🧪 **完整测试覆盖**: 包含多个测试用例

## 支持的财务指标

### 预定义指标映射
- **Revenues** / **Revenue** → `us-gaap:Revenues`
- **NetIncome** / **Net Income** → `us-gaap:NetIncomeLoss`
- **TotalAssets** / **Total Assets** → `us-gaap:Assets`
- **TotalLiabilities** / **Total Liabilities** → `us-gaap:Liabilities`
- **StockholdersEquity** / **Stockholders Equity** → `us-gaap:StockholdersEquity`

### 自定义XBRL标签
您也可以直接使用任何XBRL标签，如 `us-gaap:OperatingIncomeLoss`

## 支持的股票代码

- AAPL (Apple Inc.)
- MSFT (Microsoft Corporation)
- GOOGL (Alphabet Inc.)
- AMZN (Amazon.com Inc.)
- TSLA (Tesla Inc.)
- META (Meta Platforms Inc.)
- NVDA (NVIDIA Corporation)
- NFLX (Netflix Inc.)

## 项目结构

```
insight_agent_mvp/
├── src/                          # 核心代码模块
│   ├── __init__.py
│   ├── config.py                 # 配置管理（超参数和常量）
│   ├── sec_retriever.py          # SEC数据检索模块（支持多年度）
│   ├── xbrl_extractor.py         # XBRL数据提取模块（支持多指标）
│   └── langgraph_orchestrator.py # LangGraph工作流编排器
├── tests/                        # 测试套件
│   ├── __init__.py
│   ├── test_basic_functionality.py # 基本功能测试
│   ├── test_sec_retriever.py       # SEC检索器测试
│   ├── test_langgraph_orchestrator.py # LangGraph测试
│   ├── test_orchestrator.py        # 编排器测试
│   └── test_integration.py         # 集成测试
├── evaluation/                   # 评测系统
│   ├── __init__.py
│   ├── run_eval.py              # 主评测脚本
│   ├── quick_eval.py            # 快速评测
│   ├── eval_dataset.json        # 测试数据集
│   └── reports/                 # 评测报告目录
├── scripts/                     # 演示和启动脚本
│   ├── README.md               # 脚本说明文档
│   ├── demo.py                 # 完整功能演示
│   └── quick_start.py          # 快速启动脚本
├── docs/                       # 项目文档
│   ├── TECHNICAL_DOCUMENTATION.md # 技术文档（团队交接用）
│   └── PRODUCT_BACKLOG.md      # 产品待办列表
├── run_tests.py                 # 测试运行器
├── requirements.txt             # 依赖包列表
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目主文档
└── README_USAGE.md             # 使用指南
```

## 安装和运行

### 快速启动（推荐）
```bash
conda activate llm
python scripts/quick_start.py
```

### 手动安装

#### 1. 激活conda环境
```bash
conda activate llm
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置API密钥
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

#### 4. 运行测试
```bash
python run_tests.py
# 或使用 pytest
python -m pytest tests/ -v
```

#### 5. 启动系统
```bash
# 使用LangGraph工作流
python -m src.langgraph_orchestrator
```

### 功能演示
```bash
python scripts/demo.py
```

服务器将在 `http://localhost:8000` 启动。

## API端点详解

### 🆕 1. 获取特定指标数据（主要端点）
```
GET /get-metric?ticker=AAPL&metric=Revenues&year=2023&form_type=10-K
```

**参数说明:**
- `ticker`: 公司股票代码（必需）
- `metric`: 财务指标名称（必需）
- `year`: 财报年份（必需）
- `form_type`: 财报类型，默认"10-K"，也可选择"10-Q"

**示例响应:**
```json
{
    "ticker": "AAPL",
    "metric": "Revenues",
    "xbrl_tag": "us-gaap:Revenues",
    "year": 2023,
    "form_type": "10-K",
    "value": "383,285",
    "unit": "usd"
}
```

### 2. 获取收入数据（向后兼容）
```
GET /get-revenue?ticker=AAPL
```

获取最新10-K中的收入数据（保持向后兼容性）。

### 🆕 3. 获取支持的指标
```
GET /supported-metrics
```

返回所有预定义的财务指标及其XBRL标签映射。

### 4. 获取支持的股票代码
```
GET /supported-tickers
```

返回所有支持的公司股票代码列表。

### 5. API文档
```
GET /docs
```

自动生成的Swagger UI文档页面。

## 使用示例

### 获取Apple 2023年收入
```bash
curl "http://localhost:8000/get-metric?ticker=AAPL&metric=Revenues&year=2023"
```

### 获取Microsoft 2022年净利润
```bash
curl "http://localhost:8000/get-metric?ticker=MSFT&metric=NetIncome&year=2022"
```

### 获取Tesla 2023年第三季度收入（10-Q）
```bash
curl "http://localhost:8000/get-metric?ticker=TSLA&metric=Revenues&year=2023&form_type=10-Q"
```

### 使用自定义XBRL标签
```bash
curl "http://localhost:8000/get-metric?ticker=GOOGL&metric=us-gaap:OperatingIncomeLoss&year=2023"
```

## 配置管理

所有超参数都在 `src/config.py` 文件中集中管理：

- **SEC API配置**: URLs、用户代理、请求限速
- **股票映射**: 支持的股票代码和CIK映射
- **XBRL配置**: 默认标签和解析器设置
- **API元数据**: 标题、版本、描述

## 测试覆盖

项目包含完整的测试套件：

### 单元测试
- **test_basic_functionality.py**: 基本功能和模块导入测试
- **test_sec_retriever.py**: SEC数据检索测试
- **test_langgraph_orchestrator.py**: LangGraph工作流测试

### 集成测试
- **test_integration.py**: 端到端集成测试
- **test_orchestrator.py**: API编排器测试

### 评测系统
- **evaluation/**: 完整的评测系统，使用真实SEC API进行测试


## 系统能力评估

### ✅ 目前能做到的功能

#### 1. 能返回字段，但不能保证正确性
- **主流程完整**: 系统实现了从自然语言查询到财务数据提取的完整链路
  - 使用 LLM（GPT-3.5-turbo）解析自然语言查询，抽取结构化意图（ticker、metric、year、form_type）
  - 根据意图从 SEC 官网抓取指定公司的年报/季报 HTML
  - 使用 XBRL 解析器从 HTML 中提取指定财务指标的值和单位
  - 返回结构化结果（包括 ticker、metric、year、form_type、value、unit、xbrl_tag）

- **字段完整性**: 只要 SEC 数据源有内容，系统就能返回完整的字段结构
- **局限性**: 
  - LLM 解析意图有一定概率出错（如 ticker、metric、year 识别错误）
  - XBRL 标签映射和 HTML 解析有一定概率找不到或提取错误
  - 没有对结果的"正确性"做二次校验，完全依赖 LLM 和 XBRL 解析的第一手输出

#### 2. 能连接到服务器
- **服务器稳定性**: FastAPI/uvicorn 服务器可正常启动，API端点可用
- **脚本集成**: demo.py、quick_start.py 脚本都能检测服务器状态并与之交互
- **API端点完整**: 提供结构化查询、自然语言查询、信息查询等完整接口

#### 3. 评测与演示系统
- **自动化评测**: evaluation/run_eval.py 可批量评测系统的 NLU 和端到端准确率
- **报告生成**: 自动生成详细的评测报告，包含准确率、响应时间等指标
- **功能演示**: scripts/demo.py 可演示 API 信息、结构化查询、自然语言查询、评测系统、性能测试等

### ❌ 不能做到的/局限性

#### 1. 不能保证字段的"正确性"
- **无校验机制**: 只要能抓到 SEC 报告并解析出字段，就会返回，不管值是否真实准确
- **黑盒解析**: 没有对 LLM 解析意图的二次校验，也没有对 XBRL 解析结果的人工或规则校验
- **有限支持**: 只支持有限的 ticker/metric，超出范围会报错

#### 2. 对 SEC 数据依赖强，易受外部因素影响
- **网络依赖**: SEC 数据结构有变动或网络不通时，系统会报错或返回空字段
- **格式敏感**: 对 SEC 的 HTML 结构和 XBRL 标签格式变化敏感
- **限流影响**: 受 SEC 的请求频率限制影响

#### 3. 解析器属于"黑盒"模式
- **LLM 解析**: 解析意图时可能会出错（如年份、公司名、指标名识别错误）
- **XBRL 解析**: 只做了简单的标签映射，没有复杂的多表格/多币种/多单位处理
- **无兜底机制**: 解析失败时缺乏有效的错误恢复和兜底策略

#### 4. 缺乏健壮性设计
- **无缓存机制**: 每次查询都实时抓取 SEC，效率较低，易受限流影响
- **错误处理简单**: 错误信息只做了简单返回，没有详细日志和溯源
- **无数据验证**: 缺乏对提取数据的合理性验证和异常检测

### 🔧 代码结构特点

#### 1. 主流程全部真实调用，无 mock/硬编码
- **真实链路**: demo.py、run_eval.py 都是通过 HTTP 或直接调用主流程，未见 mock 数据或硬编码返回
- **完整集成**: 只要 SEC 数据和 OpenAI API 可用，流程都是真实链路

#### 2. 配置和依赖管理清晰
- **统一配置**: config.py 统一管理 API KEY、支持公司、指标、XBRL 配置等
- **依赖完整**: requirements.txt 依赖齐全，支持一键安装

### 📊 适用场景

#### ✅ 适合的场景
- **原型演示**: 展示金融数据智能问答的技术可行性
- **技术验证**: 验证 LLM + XBRL 解析的技术路线
- **概念验证**: 为更复杂的金融数据系统提供基础框架
- **学习研究**: 学习 LangGraph、FastAPI、XBRL 等技术栈

#### ❌ 不适合的场景
- **生产环境**: 对结果准确性有高要求的商业应用
- **实时交易**: 需要高可靠性和低延迟的金融交易场景
- **合规报告**: 需要严格数据验证的合规性报告
- **大规模部署**: 需要处理大量并发请求的企业级应用

### 🚀 改进建议

#### 短期改进（提升准确性）
- **增加校验机制**: 对意图解析和结果进行二次校验（正则、规则、人工审核等）
- **多源比对**: 增加 SEC 数据的多源比对和异常兜底
- **错误恢复**: 实现解析失败时的重试和兜底策略

#### 长期改进（提升健壮性）
- **缓存系统**: 实现数据缓存，减少重复请求
- **日志监控**: 增加详细的日志记录和性能监控
- **数据验证**: 实现提取数据的合理性验证和异常检测
- **扩展支持**: 支持更多公司、指标和报表类型

## 注意事项

1. **SEC API限制**: 遵循SEC的10请求/秒限制
2. **数据依赖**: 提取结果依赖于10-K/10-Q文件中iXBRL标签的存在
3. **年份范围**: 支持的年份范围取决于SEC数据库中的可用数据
4. **准确性限制**: 系统返回的数据仅供参考，不保证100%准确性
5. **API依赖**: 需要有效的 OpenAI API 密钥才能使用自然语言查询功能

## 扩展开发

### 添加新股票代码
在 `src/config.py` 的 `TICKER_TO_CIK` 字典中添加映射。

### 添加新指标映射
在 `src/xbrl_extractor.py` 的 `METRIC_TAG_MAPPING` 字典中添加映射。

### 支持新的财报类型
修改 `form_type` 参数的验证逻辑以支持8-K等其他财报类型。

### 评测系统使用
```bash
# 运行完整评测
python evaluation/run_eval.py

# 快速评测
python evaluation/quick_eval.py
```

## 项目文档

### 📋 技术文档
- **[技术文档](docs/TECHNICAL_DOCUMENTATION.md)**: 完整的系统架构和模块说明，用于团队交接
- **[产品待办列表](docs/PRODUCT_BACKLOG.md)**: 下一阶段开发规划和任务优先级

