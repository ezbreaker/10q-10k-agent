# InsightAgent MVP

一个基于LangGraph的智能财报分析系统，专注于从SEC EDGAR数据库中精确提取财务数据。系统采用渐进式发展策略，当前版本（MVP 1.0）致力于通过自然语言查询实现高精度的数据提取，为后续的对话式分析功能打下坚实基础。

## 🚀 核心特性

- 🎯 **精确数据提取**: 基于XBRL标准标签，确保财务数据提取的准确性
- 🔍 **自然语言查询**: 支持中文和英文自然语言查询具体财务指标
- 📊 **多指标支持**: 支持收入、净利润、总资产等核心财务指标
- ⚙️ **配置化管理**: 集中的超参数和配置管理
- 🧪 **完整测试覆盖**: 包含模块测试和集成测试

## 发展路线

### 当前阶段（MVP 1.0）
- ✓ 精确的财务数据提取
- ✓ 自然语言查询转换
- ✓ 基础指标支持
- ✓ 数据可溯源性

### 下一阶段（规划中）
- 基础对话能力
- 多轮查询支持
- 指标计算和比较
- 扩展指标覆盖

### 远期规划
- 深度财报分析
- 跨期数据比较
- 财务健康评估
- 异常指标解释

## 支持的财务指标

### 当前支持的指标映射
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
│   ├── config.py                 # 配置管理
│   ├── sec_retriever.py          # SEC数据检索模块
│   ├── xbrl_extractor.py         # XBRL数据提取模块
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
│   ├── TECHNICAL_DOCUMENTATION.md # 技术文档
│   └── PRODUCT_BACKLOG.md      # 产品待办列表
├── run_tests.py                 # 测试运行器
├── requirements.txt             # 依赖包列表
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目主文档
└── README_USAGE.md             # 使用指南
```

## 安装和运行

### 环境要求
- Python 3.8+
- 网络连接（访问SEC EDGAR和OpenAI API）

### 快速启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd insight_agent_mvp

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置API密钥
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 5. 运行测试
python run_tests.py

# 6. 启动系统
python scripts/quick_start.py
```

### 手动启动
```bash
# 启动LangGraph工作流
python -c "import asyncio; from src.langgraph_orchestrator import process_query_with_langgraph; print('LangGraph工作流已加载')"
```

## 使用示例

### 自然语言查询
```python
import asyncio
from src.langgraph_orchestrator import process_query_with_langgraph

async def main():
    # 查询Apple 2023年收入
    result = await process_query_with_langgraph("苹果公司2023年的收入是多少？")
    print(result)
    
    # 查询Microsoft 2022年净利润
    result = await process_query_with_langgraph("MSFT 2022 net income")
    print(result)

asyncio.run(main())
```

## 配置管理

所有配置都在 `src/config.py` 文件中集中管理：

- **OpenAI配置**: API密钥、模型、温度参数
- **SEC API配置**: URLs、用户代理、请求限速
- **公司映射**: 支持的股票代码和CIK映射
- **XBRL配置**: 默认标签和解析器设置

## 测试覆盖

项目包含完整的测试套件：

### 单元测试
- **test_basic_functionality.py**: 模块导入测试、配置验证、基本XBRL提取测试
- **test_sec_retriever.py**: SEC数据检索测试（包含Mock和网络测试）
- **test_langgraph_orchestrator.py**: LangGraph工作流测试

### 集成测试
- **test_integration.py**: 端到端集成测试
- **test_orchestrator.py**: API编排器测试

### 评测系统
- **evaluation/**: 完整的评测系统，使用真实SEC API进行测试

## 系统能力评估

### ✅ 目前能做到的功能

#### 1. 自然语言理解
- **LLM解析**: 使用GPT-3.5-turbo解析自然语言查询，提取结构化意图
- **支持语言**: 中文和英文查询
- **意图提取**: 能够识别ticker、metric、year、form_type等关键信息

#### 2. SEC数据获取
- **多年度支持**: 支持按年份检索历史10-K和10-Q财报
- **文件定位**: 通过SEC API准确定位特定年份的财报文件
- **数据下载**: 获取完整的iXBRL格式财报文件

#### 3. XBRL数据提取
- **标签解析**: 使用BeautifulSoup解析iXBRL标签
- **多标签支持**: 支持多种XBRL标签的映射和提取
- **基础提取**: 能够提取财务数值和单位信息

#### 4. 工作流编排
- **LangGraph架构**: 使用LangGraph进行工作流编排
- **状态管理**: 完整的工作流状态管理
- **错误处理**: 基本的错误处理和流程控制

### ❌ 当前局限性和问题

#### 1. 数据准确性问题
- **年份匹配**: 当前使用`soup.find()`只返回第一个匹配项，无法区分不同年份数据
- **标签映射**: 硬编码的指标映射不完整，导致某些公司数据提取失败
- **数值处理**: 未处理单位换算和负数格式

#### 2. 系统健壮性问题
- **错误处理**: 错误处理较为简单，缺乏详细的日志和监控
- **重试机制**: 缺乏自动重试和恢复机制
- **缓存机制**: 无数据缓存，每次查询都实时获取

#### 3. 扩展性问题
- **公司支持**: 只支持8家硬编码的公司
- **指标支持**: 指标映射需要手动维护
- **测试覆盖**: 缺乏真实数据的单元测试

## 注意事项

1. **SEC API限制**: 遵循SEC的10请求/秒限制
2. **数据依赖**: 提取结果依赖于10-K/10-Q文件中iXBRL标签的存在
3. **准确性限制**: 系统返回的数据仅供参考，不保证100%准确性
4. **API依赖**: 需要有效的OpenAI API密钥才能使用自然语言查询功能

## 扩展开发

### 添加新股票代码
在 `src/config.py` 的 `TICKER_TO_CIK` 字典中添加映射。

### 添加新指标映射
在 `src/langgraph_orchestrator.py` 的 `METRIC_TAG_MAPPING` 字典中添加映射。

### 评测系统使用
```bash
# 运行完整评测
python evaluation/run_eval.py

# 快速评测
python evaluation/quick_eval.py
```

## 项目文档

### 📋 技术文档
- **[技术文档](docs/TECHNICAL_DOCUMENTATION.md)**: 完整的系统架构和模块说明
- **[产品待办列表](docs/PRODUCT_BACKLOG.md)**: 下一阶段开发规划和任务优先级

### 3.2 关键状态转换
```python
WorkflowState = {
    "query": str,              # 用户原始查询
    "parsed_intent": dict,     # 解析后的结构化意图
    "html_content": str,       # SEC iXBRL内容
    "extracted_value": dict,   # 提取的财务数据
    "error": str,              # 错误信息
    "success": bool            # 执行状态
}
```

### 3.3 当前指标映射机制
系统实现了基础的指标映射，但存在局限性：
```python
METRIC_TAG_MAPPING = {
    "Revenues": ["us-gaap:Revenues", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"],
    "NetIncome": ["us-gaap:NetIncomeLoss"],
    "TotalAssets": ["us-gaap:Assets"],
    "TotalLiabilities": ["us-gaap:Liabilities"],
    "StockholdersEquity": ["us-gaap:StockholdersEquity"],
}
```

**问题**: 映射不完整，某些公司使用不同的XBRL标签（如`us-gaap:NetSales`），导致数据提取失败。

## 4. 当前测试覆盖情况

### 4.1 现有测试内容
1. **test_basic_functionality.py**: 模块导入测试、配置验证、基本XBRL提取测试
2. **test_sec_retriever.py**: SEC数据检索测试（包含Mock和网络测试）
3. **test_langgraph_orchestrator.py**: LangGraph工作流测试
4. **test_integration.py**: 端到端集成测试
5. **test_orchestrator.py**: API编排器测试

### 4.2 测试特点
- 主要测试模块导入和基本功能
- 包含网络测试（需要SEC API连接）
- 使用Mock模拟部分外部依赖
- 缺乏真实XBRL数据的单元测试

### 4.3 需要改进的地方
1. 增加真实XBRL数据片段的测试用例
2. 提高Mock测试覆盖率
3. 添加更多边界情况测试
4. 实现离线测试能力

## 5. 当前面临的主要问题

### 5.1 数据准确性问题
1. **年份匹配问题**: 当前使用`soup.find()`只返回第一个匹配项，无法区分不同年份数据
2. **标签映射问题**: 硬编码的指标映射不完整，导致某些公司数据提取失败
3. **数值处理问题**: 未处理单位换算和负数格式

### 5.2 系统健壮性问题
1. **错误处理**: 错误处理较为简单，缺乏详细的日志和监控
2. **重试机制**: 缺乏自动重试和恢复机制
3. **缓存机制**: 无数据缓存，每次查询都实时获取

### 5.3 扩展性问题
1. **公司支持**: 只支持8家硬编码的公司
2. **指标支持**: 指标映射需要手动维护
3. **测试覆盖**: 缺乏真实数据的单元测试

## 6. 未来改进方向

### 6.1 短期改进（提升准确性）
1. **实现上下文精确匹配**: 使用`find_all` + 上下文解析，确保年份匹配
2. **外部化指标知识库**: 建立可维护的指标映射知识库
3. **实现数值规整化**: 处理单位换算和负数格式

### 6.2 中期改进（提升健壮性）
1. **建立公司映射知识库**: 支持所有SEC注册公司
2. **重构测试系统**: 使用真实数据片段进行测试
3. **优化财年匹配逻辑**: 正确处理非标准财年

### 6.3 长期改进（提升扩展性）
1. **增强错误处理和日志**: 完善的日志记录和错误恢复
2. **缓存机制**: 实现数据缓存，提高性能
3. **API接口优化**: 支持批量查询和异步处理

## 7. 部署和运维

### 7.1 环境要求
- Python 3.8+
- OpenAI API密钥
- 网络访问SEC EDGAR数据库

### 7.2 快速启动
```bash
# 1. 环境配置
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. 配置API密钥
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 3. 运行测试
python run_tests.py

# 4. 功能演示
python scripts/demo.py
```

### 7.3 配置管理
- 环境变量：`OPENAI_API_KEY`
- 配置文件：`src/config.py`
- 评测数据：`evaluation/eval_dataset.json`

## 8. 性能和限制

### 8.1 当前性能
- **查询处理时间**: 2-4秒（财务查询）
- **SEC API限制**: 10请求/秒
- **支持范围**: 8家公司，5类指标

### 8.2 已知限制
- 财年与日历年不一致的处理
- 数值单位规整化
- 上下文精确匹配
- 指标映射的完整性和准确性

