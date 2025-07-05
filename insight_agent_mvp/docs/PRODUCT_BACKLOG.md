# 产品待办列表 (Product Backlog)
# InsightAgent MVP - 下一阶段开发规划

## P0: 关键任务 (Highest Priority - 必须解决，否则产品不可靠)

### 任务1：建立公司映射知识库 (Company Mapping Database)
**问题描述:** 当前在`langgraph_orchestrator.py`中硬编码了8家公司的CIK映射，这种方式无法扩展，且需要手动维护。根据参考资料，SEC提供了官方的完整公司映射文件。

**开发需求:**
1. **创建公司映射模块**: 新建`src/company_mapper.py`模块
2. **实现自动下载功能**: 
   - 从SEC官方下载`company_tickers.json`文件
   - 地址：`https://www.sec.gov/files/company_tickers.json`
   - 解析JSON并生成本地的`data/company_mappings.json`
3. **实现查询接口**: 
   - 提供`get_cik_by_ticker(ticker)`函数
   - 提供`get_company_name_by_ticker(ticker)`函数
   - 支持模糊匹配和大小写不敏感查询
4. **集成到系统**: 修改`langgraph_orchestrator.py`，移除硬编码的公司映射，改为调用新的公司映射模块
5. **添加更新机制**: 支持定期更新公司映射数据

**验收标准:**
- [ ] 支持所有SEC注册的上市公司（3000+家）
- [ ] 自动从官方源获取最新数据
- [ ] 提供离线查询功能
- [ ] 向后兼容现有的8家公司
- [ ] 添加公司映射测试用例

---

### 任务2：外部化指标知识库 (Externalize Metrics Knowledge Base)
**问题描述:** 当前的`METRIC_TAG_MAPPING`硬编码在`langgraph_orchestrator.py`中，不利于维护和扩展。根据参考资料，指标与XBRL标签的映射是一个需要持续维护的"知识库"。

**开发需求:**
1. **创建指标知识库**: 新建`data/metrics_knowledge_base.json`文件
2. **设计知识库结构**: 
```json
{
  "metrics": {
    "Revenues": {
      "description": "公司营业收入",
      "tags": [
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
      ],
      "preferred_tag": "us-gaap:Revenues",
      "aliases": ["Revenue", "营业收入", "销售收入", "总收入"],
      "time_type": "duration",
      "typical_context": "年度/季度累计"
    },
    "NetIncome": {
      "description": "净利润",
      "tags": ["us-gaap:NetIncomeLoss"],
      "preferred_tag": "us-gaap:NetIncomeLoss",
      "aliases": ["Net Income", "净利润", "净收益", "归属净利润"],
      "time_type": "duration",
      "typical_context": "年度/季度累计"
    },
    "Assets": {
      "description": "总资产",
      "tags": ["us-gaap:Assets"],
      "preferred_tag": "us-gaap:Assets",
      "aliases": ["Total Assets", "总资产", "资产总额"],
      "time_type": "instant",
      "typical_context": "期末余额"
    }
  }
}
```
3. **创建知识库管理器**: 新建`src/metrics_manager.py`模块
   - 提供`get_tags_for_metric(metric_name)`函数
   - 支持别名匹配和模糊查询
   - 提供指标元数据查询功能
4. **集成到系统**: 修改`langgraph_orchestrator.py`，移除硬编码的映射，改为调用知识库管理器
5. **添加扩展机制**: 支持运行时添加新的指标标签映射

**验收标准:**
- [ ] 知识库文件可以独立维护和更新
- [ ] 支持指标别名和模糊匹配
- [ ] 包含时间类型（instant/duration）元数据
- [ ] 向后兼容现有功能
- [ ] 添加知识库验证和测试机制

---

### 任务3：实现上下文精确匹配 (Contextual Match)
**问题描述:** 当前的`xbrl_extractor.py`使用`soup.find()`，这只会返回第一个匹配项，无法区分不同年份的数据，是导致数据不准确的**最大风险**。

**开发需求:**
1. **升级`xbrl_extractor.py`**: 将`soup.find`改为`soup.find_all`
2. **实现Context解析**: 对于每个找到的标签，必须提取其`contextRef`属性，并去文档中找到对应的`<xbrli:context>`定义
3. **匹配时间**: 从`context`中解析出`<xbrli:period>`，并与用户查询的`year`进行严格匹配。只有年份匹配的那个标签的值，才是我们需要的正确答案
4. **处理时间类型**: 利用任务2中的指标知识库，正确处理instant（瞬时点）和duration（时间段）两种不同的时间类型。财报中的资产负债表项目（如总资产、总负债）是瞬时点数据，而利润表项目（如收入、净利润）是时间段数据，需要分别处理这两种不同的时间语义

**验收标准:**
- [ ] 能够正确区分同一公司不同年份的相同指标
- [ ] Context解析准确率达到100%
- [ ] 正确处理instant和duration两种时间类型的数据
- [ ] 结合指标知识库进行智能匹配
- [ ] 添加相应的单元测试

---

### 任务4：实现数值规整化 (Value Normalization)
**问题描述:** 当前返回的是原始文本值，如`"1,234"`，没有处理单位（如"in millions"）和负数格式（如`(123)`）。这会导致返回的数值在量级和正负上是错误的。

**开发需求:**
1. **创建`Data-Validator`模块**: 新建一个`src/data_validator.py`模块
2. **实现数值清洗**: 创建一个函数，负责将输入的文本值（如`"(1,234)"`）转换为标准的数字（`-1234.0`）
3. **实现单位解析**: 创建另一个函数，负责在提取到数值后，搜索其HTML上下文，查找"in millions"或"in thousands"等关键词，并对数值进行相应的乘法运算
4. **在工作流中集成**: 在LangGraph的`extract_xbrl_data_node`之后，增加一个新的`validate_data_node`来调用这些新功能

**验收标准:**
- [ ] 正确处理负数格式：`(123)` → `-123`
- [ ] 正确处理千分位逗号：`1,234` → `1234`
- [ ] 正确处理单位换算：`123 (in millions)` → `123000000`
- [ ] 添加数值验证测试用例

---

### 任务5：重构测试系统 (Test System Overhaul)
**问题描述:** 删除了不准确的`sample_10k.html`后，当前缺乏有效的单元测试。需要重新设计测试策略，使用真实数据片段或Mock方式。

**开发需求:**

#### 5.1 创建真实数据测试集
1. **生成真实测试数据**: 从实际SEC文件中提取小片段，创建`tests/fixtures/real_xbrl_samples.json`
2. **包含多种场景**:
   - 正常的收入数据（苹果公司）
   - 负数形式的净利润
   - 包含单位说明的数据
   - 多年份数据（测试上下文匹配）
   - 不同标签格式

#### 5.2 重新实现测试文件
1. **`test_xbrl_extractor.py`**: 
   - 使用真实数据片段测试XBRL提取功能
   - 测试上下文精确匹配
   - 测试数值规整化
   
2. **`test_context_matching.py`**: 
   - 专门测试年份上下文匹配功能
   - 验证多年份数据的正确提取

3. **`test_data_validation.py`**: 
   - 测试数值清洗和单位换算
   - 测试各种数值格式的处理

4. **`test_company_mapper.py`**: 
   - 测试公司映射功能
   - 测试CIK查询和公司名称查询

5. **`test_metrics_manager.py`**: 
   - 测试指标知识库功能
   - 测试别名匹配和模糊查询

#### 5.3 Mock测试策略 优先度低
1. **Mock SEC API**: 使用`unittest.mock`模拟SEC API响应
2. **Mock OpenAI API**: 模拟LLM响应，测试意图解析
3. **离线测试**: 确保测试不依赖外部API

**验收标准:**
- [ ] 测试覆盖率达到85%以上
- [ ] 所有测试可以离线运行
- [ ] 包含正负两种测试用例
- [ ] 测试执行时间<30秒

---

## P1: 高优先级任务 (High Priority - 提升可维护性和准确性)

### 任务6：优化财年匹配逻辑 (Fiscal Year Matching)
**问题描述:** 当前的`sec_retriever.py`仍在使用`filingDate`（提交日期）来匹配年份，这在财年与日历年不一致时会出错。

**开发需求:**
1. 修改`sec_retriever.py`中的`_search_filings_in_data`函数
2. 查找逻辑必须**优先使用`periodOfReport`字段**来确定财报的所属年份，而不是`filingDate`
3. 添加财年处理逻辑，支持非标准财年的公司

**验收标准:**
- [ ] 正确处理财年不等于日历年的情况
- [ ] 优先使用`periodOfReport`进行年份匹配
- [ ] 支持Q1/Q2/Q3/Q4季度报告的正确匹配
- [ ] 添加财年测试用例

---

### 任务7：增强错误处理和日志 (Enhanced Error Handling)
**问题描述:** 当前的错误处理较为简单，不便于调试和监控生产环境问题。

**开发需求:**
1. **实现结构化日志**: 
   - 添加`logging`配置
   - 记录关键步骤的执行时间
   - 记录API调用的成功/失败状态

2. **细化错误类型**:
   - `SECRetrievalError`: SEC数据获取失败
   - `XBRLExtractionError`: XBRL提取失败
   - `IntentParsingError`: 意图解析失败
   - `ValidationError`: 数据验证失败

3. **实现重试机制**:
   - SEC API调用失败时的指数退避重试
   - OpenAI API的重试逻辑
   - 在LangGraph中添加重试节点

**验收标准:**
- [ ] 完善的日志记录系统
- [ ] 结构化的错误信息
- [ ] 自动重试机制
- [ ] 错误统计和监控

---

## P2: 中优先级任务 (Medium Priority - 功能增强)

### 任务8：扩展公司支持 (Expand Company Coverage)
**开发需求:**
1. 基于任务1的公司映射知识库，系统已支持所有SEC注册公司
2. 研究和添加更多行业的主要公司的特殊XBRL标签到指标知识库
3. 处理不同行业的特殊财务指标和标签映射

---

### 任务9：缓存机制 (Caching System)
**开发需求:**
1. 实现SEC文件的本地缓存
2. 添加查询结果缓存
3. 实现缓存过期和清理机制

---

### 任务10：API接口优化 (API Enhancement)
**开发需求:**
1. 添加批量查询支持
2. 实现异步处理
3. 添加查询历史记录

---

## P3: 低优先级任务 (Low Priority - 长期改进)

### 任务11：多语言支持 (Multi-language Support)


### 任务12：数据可视化 (Data Visualization)


### 任务13：历史趋势分析 (Trend Analysis)


---

## 开发里程碑 (Milestones)

### Sprint 1 (2周): 基础设施建设
- [ ] 任务1: 建立公司映射知识库
- [ ] 任务2: 外部化指标知识库
- [ ] 任务3: 实现上下文精确匹配

**目标**: 建立完整的知识库基础设施，解决核心数据匹配问题

### Sprint 2 (1.5周): 数据处理优化
- [ ] 任务4: 实现数值规整化
- [ ] 任务5: 重构测试系统
- [ ] 任务6: 优化财年匹配逻辑

**目标**: 确保数据提取的100%准确性和完整测试覆盖

### Sprint 3 (2周): 系统稳定性提升
- [ ] 任务7: 增强错误处理和日志
- [ ] 任务8: 扩展公司支持
- [ ] 任务9: 缓存机制

**目标**: 提升系统可维护性、稳定性和性能

---

## 质量门禁 (Quality Gates)

### 代码质量要求
- [ ] 单元测试覆盖率 ≥ 85%
- [ ] 集成测试覆盖率 ≥ 70%
- [ ] 代码审查通过率 100%
- [ ] 无高危安全漏洞

### 性能要求
- [ ] 查询响应时间 ≤ 3秒 (95分位)
- [ ] 系统可用率 ≥ 99.5%
- [ ] API成功率 ≥ 99%

### 功能要求
- [ ] 评测系统成功率 100%
- [ ] 支持所有预定义的财务指标
- [ ] 错误信息清晰易懂

---

## 风险评估 (Risk Assessment)

### 高风险项目
1. **上下文匹配实现复杂度**: 可能需要深入理解XBRL规范
2. **SEC API变更**: 外部依赖可能影响开发进度
3. **测试数据质量**: 真实数据的获取和维护成本

### 风险缓解策略
1. **技术风险**: 
   - 分阶段实现，先做MVP再优化
   - 建立技术专家咨询机制
   
2. **外部依赖风险**:
   - 实现Mock和离线测试
   - 监控API变更和公告
   
3. **数据质量风险**:
   - 建立数据验证机制
   - 多源数据交叉验证




参考：
好的，这个问题非常关键，直接关系到我们能否系统化、规模化地进行精确的数据提取。你的想法完全正确：我们需要将这些“映射关系”固化成一个独立的文件，而不是在代码里零散地维护。

好消息是，SEC官方确实为此提供了可供下载的、权威的原始数据。

### **1. 公司与CIK的Mapping**

对于公司标识（Ticker Symbol to CIK），SEC提供了一个非常方便、完整的JSON文件，包含了所有上市公司的数据。

  * **官方文件**: `company_tickers.json`
  * **下载地址**: [https://www.sec.gov/files/company\_tickers.json](https://www.google.com/search?q=https://www.sec.gov/files/company_tickers.json)
  * **文件内容示例**:
    ```json
    {
      "0": {
        "cik_str": 320193,
        "ticker": "AAPL",
        "title": "Apple Inc."
      },
      "1": {
        "cik_str": 789019,
        "ticker": "MSFT",
        "title": "MICROSOFT CORP"
      },
      ...
    }
    ```
  * **如何使用**:
    你可以写一个简单的脚本，每天或每周自动下载这个JSON文件。然后，遍历这个文件，提取出`cik_str`和`ticker`，生成一个你自己的、随时保持最新的`TICKER_TO_CIK`字典。这样就无需手动维护了。

### **2. 指标与XBRL标签的Mapping**

这个问题要复杂得多。**SEC或FASB（财务会计准则委员会）并不提供一个像你例子中那样简单的、一对多的“友好名称到XBRL标签”的JSON或CSV文件。**

官方提供的是一套完整的、非常复杂的\*\*XBRL分类帐（Taxonomy）\*\*文件。这套文件定义了每一个会计概念、它们之间的关系以及它们的标准标签。

  * **官方文件**: US-GAAP Financial Reporting Taxonomy（通常每年更新）
  * **下载地址**: 你可以在FASB的官方网站上找到，例如（链接可能会变化）：[https://www.fasb.org/page/show/xbrl-us-gaap-financial-reporting-taxonomy](https://www.google.com/search?q=https://www.fasb.org/page/show/xbrl-us-gaap-financial-reporting-taxonomy)
  * **你需要关注的文件**: 在下载的分类帐压缩包里，对我们最有用的文件是以 `-lab.xml` 结尾的 **Label Files**。这些XML文件定义了XBRL标签（如 `us-gaap:Revenues`）和它对应的不同类型的、人类可读的名称（如 "Revenues"、"Revenue, Net" 等）。

**为什么一个指标会对应多个XBRL标签？**

你给出的例子 `("Revenues": ["us-gaap:Revenues", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"])` 非常好，它揭示了问题的核心：

  * **会计准则的演进**: 随着会计准则（如ASC 606收入确认）的更新，新的、更具体的XBRL标签会被引入。例如，`RevenueFromContractWithCustomer...` 就是一个更现代、更精确的收入标签。
  * **公司的选择**: 公司在报备时，可能会根据自己的业务情况，选择使用一个更宽泛的旧标签，或者一个更具体的新标签。
  * **层级关系**: XBRL分类帐是树状结构的。`Revenues`可能是一个顶层概念，下面有多个子概念。

**结论与实践建议**

1.  **没有现成的简单映射文件**: 你无法从官方直接下载一个即用型的`METRIC_TAG_MAPPING`。
2.  **创建和维护你自己的Mapping文件是必要且正确的**: 你在`orchestrator.py`里定义的那个`METRIC_TAG_MAPPING`字典，正是解决这个问题的最佳工程实践。它是一个\*\*“策略层”\*\*，将业务逻辑（我们认为“净利润”是什么）和底层技术（XBRL标签）解耦。
3.  **如何构建和扩展你的Mapping文件**:
      * **以官方Label文件为基础**: 你可以写一个脚本来解析`-lab.xml`文件，生成一个基础的、巨大的XBRL标签到其标准名称的映射表，作为参考。
      * **手动维护一个核心列表**: 对于最常用、最重要的几十个指标（如你已经列出的营收、净利润、资产等），手动创建和维护一个映射列表。这个列表需要包含一个指标可能对应的所有常见XBRL标签。
      * **从实践中学习和补充**: 在你的Agent处理大量真实财报的过程中，当遇到`Extractor`找不到数据的情况时，很可能就是因为该公司使用了一个你的映射列表里没有的新标签。你需要记录下这些失败案例，分析财报原文，然后将新的标签补充到你的映射文件中。这是一个持续迭代和完善的过程。

**总结**:

  * **公司映射**: 直接下载官方`company_tickers.json`并定期更新。
  * **指标映射**: 创建并**持续维护**你自己的`METRIC_TAG_MAPPING.json`文件是核心工作之一。这个文件是你的“知识库”，它会随着你处理的财报越来越多而变得越来越完善和强大。