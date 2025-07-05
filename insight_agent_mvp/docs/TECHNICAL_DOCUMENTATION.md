# 技术文档：InsightAgent MVP v1.0

## 1. 系统概述

### 目标
本项目旨在创建一个AI助手，能够通过自然语言交互，从SEC的10-K和10-Q财报中准确提取财务数据。

### 核心架构
系统采用"编排器 + 微服务工具集"的模式，基于LangGraph框架构建。该架构将自然语言理解、数据获取、数据提取等功能解耦为独立的、可控的节点，由一个状态图（StateGraph）进行统一编排和调度。

### 技术栈
- **Python 3.8+**: 核心开发语言
- **LangGraph**: 工作流编排框架
- **OpenAI GPT-3.5-turbo**: 自然语言理解
- **BeautifulSoup**: iXBRL/XML解析
- **Requests**: HTTP客户端
- **FastAPI**: API服务框架（可选）

## 2. 模块详解

### a. `config.py` (配置文件)

#### 功能(What)
集中管理项目所有的配置项和常量，如API密钥、URL、支持的公司列表（TICKER_TO_CIK）等。

#### 实现方式(How)
通过定义一系列大写的Python变量来实现，主要包括：
- **OpenAI配置**: API密钥、模型、温度参数
- **SEC API配置**: 基础URL、用户代理、请求延迟
- **公司映射**: TICKER_TO_CIK字典，将股票代码映射到SEC的CIK号
- **XBRL配置**: 默认标签和解析器设置

#### 设计原因(Why)
将配置与业务逻辑代码分离，便于在不同环境（开发、测试、生产）中轻松切换配置，且修改配置时无需触碰核心代码，提高了系统的可维护性。

### b. `sec_retriever.py` (SEC文件获取器)

#### 功能(What)
负责与SEC EDGAR数据库的所有交互。其核心函数`get_filing_html`能够根据指定的公司ticker、年份和财报类型，获取到对应的原始iXBRL文件（inline XBRL - 嵌入在HTML中的XBRL数据）。

#### 数据获取链路详解
**第一步：从SEC EDGAR API获取文件索引**
- **数据源**: SEC EDGAR是美国证券交易委员会的官方文件数据库
- **API端点**: `https://data.sec.gov/submissions/CIK{cik}.json`
- **返回格式**: JSON格式的公司提交历史，包含所有10-K、10-Q等财报的元数据

**第二步：定位具体财报文件**
- **从JSON中提取**: `accessionNumber`（文件访问号）和`primaryDocument`（主文档文件名）
- **匹配逻辑**: 根据用户查询的年份和财报类型（10-K/10-Q）进行筛选

**第三步：下载实际财报文件**
- **构造URL**: `https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_document}`
- **文件格式**: iXBRL格式（HTML文档中嵌入XBRL标签）
- **文件特点**: 人类可读的HTML + 机器可读的XBRL标签

#### 为什么使用XML/XBRL/iXBRL？
1. **数据源决定格式**: SEC强制要求上市公司以iXBRL格式提交财报，我们别无选择
2. **XBRL标准化**: 使用标准化的us-gaap标签体系，确保不同公司的财务数据具有一致的语义
3. **XML结构化**: 提供机器可读的严格结构，避免了自然语言处理的不确定性
4. **iXBRL双重优势**: 既保持了财报的人类可读性，又提供了结构化的数据提取能力

#### 实现方式(How)
1. 通过`TICKER_TO_CIK`映射找到公司的CIK号
2. 调用`https://data.sec.gov/submissions/CIK{cik}.json`端点获取公司的文件提交历史
3. 在返回的JSON中，遍历查找与指定年份和财报类型匹配的文件，并提取其`accession_number`和`primary_document`
4. 拼接成最终的财报URL并下载iXBRL内容
5. 代码中包含了对SEC速率限制的考量（`time.sleep`）

#### 设计原因(Why)
将数据源的获取逻辑封装在一个独立的模块中。未来如果需要增加新的数据源（如其他国家的交易所），我们只需增加一个新的`retriever`模块，而无需改动主工作流。这种设计使系统完全依赖于官方数据源的格式标准，保证了数据的权威性和准确性。

### c. `xbrl_extractor.py` (XBRL数据提取器)

#### 功能(What)
这是系统的核心"执行工具"。它负责从iXBRL文件中，根据指定的XBRL标签（如`us-gaap:Revenues`），精准地提取出财务数值和单位。

#### 实现方式(How)
1. 使用`BeautifulSoup`库（指定`xml`解析器）来解析iXBRL文档中的XBRL标签
2. 利用`soup.find('ix:nonFraction', {'name': metric_tag})`方法，通过标签名和`name`属性来定位到具体的XBRL数据点
3. 提取标签的文本内容作为`value`，提取`unitRef`属性作为`unit`

#### 设计原因(Why)
这是我们"确定性RAG"架构的基石。通过直接解析机器可读的XBRL标签而非进行语义猜测，我们最大程度上保证了数据提取的准确性。将它独立出来，便于未来针对这个核心算法进行持续的优化和测试。

#### 数据格式说明

**完整的数据流转链路:**
```
SEC EDGAR → JSON元数据 → iXBRL文件 → XML解析 → 财务数据
```


**iXBRL文件格式（我们的核心数据源）**
- **XML格式**: 可扩展标记语言，具有严格的结构化语法，便于机器解析
- **XBRL格式**: 基于XML的财务报告标准，使用标准化的标签体系（如us-gaap）来标识财务数据
- **iXBRL格式**: 将XBRL数据嵌入HTML中，既保持了人类可读性，又保留了机器可读的结构化数据
- **标签示例**: `<ix:nonFraction name="us-gaap:Revenues" unitRef="USD" contextRef="c1">100000</ix:nonFraction>` 表示以美元为单位的收入数据
- **上下文定义**: `<xbrli:context id="c1"><xbrli:period><xbrli:startDate>2021-01-01</xbrli:startDate><xbrli:endDate>2021-12-31</xbrli:endDate></xbrli:period></xbrli:context>` 定义时间范围

**为什么选择这种技术路线？**
1. **监管要求**: SEC强制要求上市公司以iXBRL格式提交财报，这是唯一的官方数据源
2. **标准化优势**: us-gaap标签体系确保了跨公司的数据一致性，避免了自然语言的歧义
3. **精确性保证**: 直接解析结构化标签，比AI解析PDF文本更加准确可靠
4. **权威性**: 来自SEC官方数据库，数据具有法律效力和权威性

### d. `langgraph_orchestrator.py` (LangGraph编排器)

#### 功能(What)
作为系统的"大脑"，定义和控制整个业务流程。它将NLU、数据获取、数据提取等步骤定义为图中的节点，并管理它们之间的流转逻辑。

#### 实现方式(How)
1. 定义了一个`WorkflowState`来管理整个流程中的数据状态
2. 创建了`parse_intent_node`, `retrieve_sec_data_node`, `extract_xbrl_data_node`三个核心节点
3. **`parse_intent_node`** - 系统的"翻译官"：这是自然语言交互的唯一入口，负责将用户的自然语言查询转换为系统可理解的结构化JSON格式。它通过调用LLM（OpenAI）来实现这一关键的"语言到数据"的转换过程
4. `retrieve_sec_data_node`和`extract_xbrl_data_node`分别调用`sec_retriever`和`xbrl_extractor`来执行具体任务
5. 使用`should_continue`条件边来控制工作流，如果任何一步失败，流程会提前终止

#### 设计原因(Why)
使用LangGraph而不是简单的顺序函数调用，为系统提供了极佳的健壮性和可扩展性。未来增加`Fallback`（后备方案）或`Reflection`（反思）等复杂逻辑时，我们只需在图中增加新的节点和边，而无需重构整个代码，这对于构建复杂的Agent至关重要。

## 3. 工作流程详解

### 3.1 整体流程
```
用户查询 → 意图解析 → SEC数据检索 → XBRL数据提取 → 结果返回
```

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

### 3.3 多标签映射机制（短期）
系统实现了智能的多标签映射，能够处理不同公司使用不同XBRL标签的情况：
```python
METRIC_TAG_MAPPING = {
    "Revenues": [
        "us-gaap:Revenues", 
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    ],
    "NetIncome": ["us-gaap:NetIncomeLoss"],
    # ...
}
```

## 4. 评测系统

### 4.1 评测架构
- **evaluation/run_eval.py**: 主评测脚本
- **evaluation/quick_eval.py**: 快速评测脚本
- **evaluation/eval_dataset.json**: 标准测试数据集

### 4.2 评测指标 （仍需补充）
- **NLU准确率**: 意图解析的准确性
- **端到端准确率**: 完整流程的成功率
- **响应时间**: 查询处理的时间效率

### 4.3 当前性能
- **成功率**: 100% (10/10测试用例)
- **支持公司**: 8家主要美国公司
- **支持指标**: 5类主要财务指标

## 5. 部署和运维

### 5.1 环境要求
- Python 3.8+
- OpenAI API密钥
- 网络访问SEC EDGAR数据库

### 5.2 快速启动
```bash
# 1. 环境配置
conda activate llm
python scripts/quick_start.py

# 2. 运行评测
python evaluation/run_eval.py

# 3. 功能演示
python scripts/demo.py
```

### 5.3 配置管理
- 环境变量：`OPENAI_API_KEY`
- 配置文件：`src/config.py`
- 评测数据：`evaluation/eval_dataset.json`

## 6. 性能和限制

### 6.1 当前性能
- **查询处理时间**: 2-4秒（财务查询）
- **SEC API限制**: 10请求/秒
- **支持范围**: 8家公司，5类指标

### 6.2 已知限制
- 财年与日历年不一致的处理
- 数值单位规整化
- 上下文精确匹配

## 7. 扩展性设计

### 7.1 模块化架构
每个组件都可以独立扩展：
- 添加新的数据源（新的retriever）
- 支持新的文档格式（新的extractor）
- 增加新的工作流节点

### 7.2 配置化支持
- 新公司：在`config.py`中添加CIK映射
- 新指标：在多标签映射中添加标签
- 新功能：在LangGraph中添加新节点
