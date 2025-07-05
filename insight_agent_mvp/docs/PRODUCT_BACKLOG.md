# 产品待办列表 (Product Backlog)
# InsightAgent MVP - 下一阶段开发规划

## 开发策略说明

### 渐进式发展路线
系统采用渐进式发展策略，每个阶段都专注于解决特定的核心问题：

1. **第一阶段**（当前MVP）
   - 核心目标：确保数据提取的准确性和可靠性
   - 关键指标：查询准确率、数据可溯源性
   - 完成标准：单点查询准确率达到95%以上

2. **第二阶段**（即将开始）
   - 核心目标：引入基础对话能力
   - 关键指标：多轮对话成功率、上下文保持准确度
   - 完成标准：基础对话场景覆盖率80%以上

3. **第三阶段**（规划中）
   - 核心目标：实现深度财报分析
   - 关键指标：分析准确性、推理合理性
   - 完成标准：复杂分析场景支持率70%以上

## P0: 关键任务 (Highest Priority - 必须解决，否则产品不可靠)

### 任务1：建立公司映射知识库 (Company Mapping Database) ⭐⭐⭐⭐
**问题描述:** 当前在`config.py`中硬编码了8家公司的CIK映射，无法扩展。SEC提供了官方的完整公司映射文件，包含所有上市公司。

**开发需求:**
1. **创建公司映射模块**: 新建`src/company_mapper.py`
2. **实现数据下载功能**: 
   - 从`https://www.sec.gov/files/company_tickers.json`下载官方数据
   - 解析JSON，提取`cik_str`、`ticker`、`title`字段
   - 生成本地`data/company_mappings.json`文件
3. **实现核心查询接口**: 
   - `get_cik_by_ticker(ticker: str) -> int`: 根据ticker获取CIK号
   - `get_company_name_by_ticker(ticker: str) -> str`: 根据ticker获取公司名称
   - `get_ticker_by_cik(cik: int) -> str`: 根据CIK获取ticker（可选）
4. **集成到系统**: 修改`langgraph_orchestrator.py`，移除硬编码映射
5. **添加更新机制**: 提供`update_company_mappings()`函数，支持手动更新

**验收标准:**
- [ ] 支持查询任意SEC注册公司的CIK和名称
- [ ] 查询响应时间 < 100ms（本地JSON查询）
- [ ] 向后兼容现有的8家公司
- [ ] 提供数据更新功能
- [ ] 添加单元测试覆盖主要查询场景

---

### 任务2：外部化指标知识库 (Externalize Metrics Knowledge Base) ⭐⭐⭐
**问题描述:** 当前`METRIC_TAG_MAPPING`硬编码在`langgraph_orchestrator.py`中，映射不完整导致数据提取失败。需要建立可维护的指标知识库。

**开发需求:**
1. **创建指标知识库文件**: 新建`data/metrics_knowledge_base.json`
2. **设计知识库结构，仅作为参考，不一定正确，鼓励更robust的设计**: 
```json
{
  "Revenues": {
    "description": "公司营业收入",
    "tags": [
      "us-gaap:Revenues",
      "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
      "us-gaap:NetSales",
      "us-gaap:SalesRevenueNet"
    ],
    "time_type": "duration"
  },
  "NetIncome": {
    "description": "净利润",
    "tags": [
      "us-gaap:NetIncomeLoss",
      "us-gaap:ProfitLoss",
      "us-gaap:NetIncomeLossAvailableToCommonStockholders"
    ],
    "time_type": "duration"
  }
}
```
3. **创建知识库管理器**: 新建`src/metrics_manager.py`
   - `get_tags_for_metric(metric_name: str) -> List[str]`: 获取指标的所有可能标签
   - `get_time_type(metric_name: str) -> str`: 获取指标的时间类型
4. **集成到系统**: 修改`langgraph_orchestrator.py`，移除硬编码的映射，改为调用知识库管理器
5. **添加扩展接口**: 提供`add_metric_mapping()`函数，支持运行时添加新映射

**验收标准:**
- [ ] 支持至少10个核心财务指标的映射
- [ ] 每个指标至少包含3个常见XBRL标签
- [ ] 向后兼容现有功能
- [ ] 提供映射添加和查询的单元测试

**注意**: 这是一个需要持续维护的知识库，后续会根据实际使用情况不断补充新的标签映射。

---

### 任务3：实现上下文精确匹配 (Contextual Match) ✅ 已完成
**问题描述:** 已解决。当前`xbrl_extractor.py`使用`soup.find()`只返回第一个匹配项，无法区分不同年份数据。

**解决方案:** 已实现`find_all` + 上下文精确匹配
- 使用`soup.find_all()`获取所有匹配的XBRL标签
- 解析每个标签的`contextRef`，找到对应的`<xbrli:context>`
- 从context中提取`<xbrli:period>`的时间信息
- 严格匹配用户查询的年份，只返回正确年份的数据
- 支持`instant`（瞬时点）和`duration`（时间段）两种时间类型

**验收标准:** ✅ 已通过
- [x] 能够正确区分同一公司不同年份的相同指标
- [x] Context解析准确率达到100%
- [x] 正确处理instant和duration两种时间类型
- [x] 添加了完整的单元测试

---

### 任务4：实现数值规整化 (Value Normalization) ⭐⭐
**问题描述:** 当前返回原始文本值如`"1,234"`，未处理单位（如"in millions"）和负数格式（如`(123)`）。

**开发需求:**
1. **创建数据验证模块**: 新建`src/data_validator.py`
2. **实现数值清洗函数**: 
   - `clean_numeric_value(value: str) -> float`: 处理千分位逗号、负数括号
   - 输入：`"(1,234)"` → 输出：`-1234.0`
   - 输入：`"1,234"` → 输出：`1234.0`
3. **实现单位解析函数**:
   - `parse_unit_multiplier(html_content: str, context_ref: str) -> int`: 查找单位说明
   - 支持"in millions"、"in thousands"、"in billions"等
   - 返回相应的乘数（1000000、1000、1000000000）
4. **集成到工作流**: 在`extract_xbrl_data_node`后添加`validate_data_node`
5. **处理边界情况**: 处理无单位说明、格式异常等情况

**验收标准:**
- [ ] 正确处理负数格式：`(123)` → `-123`
- [ ] 正确处理千分位逗号：`1,234` → `1234`
- [ ] 正确处理单位换算：`123 (in millions)` → `123000000`
- [ ] 处理无单位说明时返回原值
- [ ] 添加数值验证的单元测试

---

### 任务5：重构测试系统 (Test System Overhaul) ⭐⭐⭐⭐
**问题描述:** 当前测试主要是模块导入测试和基本的网络测试，缺乏有效的单元测试。需要重新设计测试策略。

**开发需求:**
1. **创建真实数据测试集**: 新建`tests/fixtures/real_xbrl_samples.json`
   - 从实际SEC文件中提取小片段（<1KB）
   - 包含多种场景：正常数据、负数、多年份、不同标签
   - 每个样本包含：HTML片段、期望结果、测试说明
2. **重新实现核心测试文件**:
   - `test_xbrl_extractor.py`: 使用真实数据测试提取功能
   - `test_context_matching.py`: 专门测试年份匹配（已完成）
   - `test_data_validation.py`: 测试数值清洗和单位换算
   - `test_company_mapper.py`: 测试公司映射功能
   - `test_metrics_manager.py`: 测试指标知识库功能
3. **Mock测试策略**:
   - Mock SEC API响应，避免网络依赖
   - Mock OpenAI API响应，测试意图解析
   - 确保所有测试可离线运行

**验收标准:**
- [ ] 测试覆盖率达到80%以上
- [ ] 所有测试可以离线运行
- [ ] 包含至少10个真实数据测试用例
- [ ] 测试执行时间 < 30秒
- [ ] 每个核心模块都有对应的测试文件

---

### 任务6：优化财年匹配逻辑 (Fiscal Year Matching) ⭐⭐⭐
**问题描述:** 当前`sec_retriever.py`使用`filingDate`（提交日期）匹配年份，在财年与日历年不一致时会出错。

**开发需求:**
1. **修改年份匹配逻辑**: 在`_search_filings_in_data`函数中
   - 优先使用`periodOfReport`字段确定财报所属年份
   - 如果`periodOfReport`不存在，再使用`filingDate`
   - 添加财年处理逻辑，支持非标准财年公司
2. **处理季度报告**: 
   - 正确识别Q1/Q2/Q3/Q4的财年归属
   - 处理跨年度的季度报告
3. **添加财年验证**: 确保提取的年份与用户查询一致

**验收标准:**
- [ ] 优先使用`periodOfReport`进行年份匹配
- [ ] 正确处理财年不等于日历年的情况
- [ ] 支持Q1/Q2/Q3/Q4季度报告的正确匹配
- [ ] 添加至少5个财年测试用例
- [ ] 向后兼容现有的`filingDate`逻辑

---

## P1: 高优先级任务 (High Priority - 提升可维护性和准确性)

### 任务7：增强错误处理和日志 (Enhanced Error Handling) ⭐⭐⭐
**问题描述:** 当前错误处理简单，不便于调试和监控生产环境问题。

**开发需求:**
1. **实现结构化日志**: 
   - 添加`logging`配置，记录关键步骤
   - 记录API调用成功/失败状态和执行时间
   - 记录数据提取的详细过程
2. **细化错误类型**:
   - `SECRetrievalError`: SEC数据获取失败
   - `XBRLExtractionError`: XBRL提取失败
   - `IntentParsingError`: 意图解析失败
   - `ValidationError`: 数据验证失败
3. **实现重试机制**:
   - SEC API调用失败时的指数退避重试（最多3次）
   - OpenAI API的重试逻辑
   - 在LangGraph中添加重试节点

**验收标准:**
- [ ] 完善的日志记录系统，包含时间戳和错误详情
- [ ] 结构化的错误信息，便于问题定位
- [ ] 自动重试机制，提高系统稳定性
- [ ] 错误统计和监控功能

---

## 开发里程碑 (Milestones)

### Sprint 1 (2周): 基础设施和核心功能
- [ ] 任务2: 外部化指标知识库
- [ ] 任务4: 实现数值规整化
- [ ] 任务6: 优化财年匹配逻辑

**目标**: 建立知识库基础，解决数据准确性问题

### Sprint 2 (1.5周): 系统完善
- [ ] 任务1: 建立公司映射知识库
- [ ] 任务5: 重构测试系统
- [ ] 任务7: 增强错误处理和日志

**目标**: 完善系统架构，提升可维护性和稳定性

---

## 质量门禁 (Quality Gates)

### 代码质量要求
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试覆盖率 ≥ 60%
- [ ] 代码审查通过率 100%
- [ ] 无高危安全漏洞

### 性能要求
- [ ] 查询响应时间 ≤ 5秒 (95分位)
- [ ] 系统可用率 ≥ 99%
- [ ] API成功率 ≥ 95%

### 功能要求
- [ ] 支持所有预定义的财务指标
- [ ] 错误信息清晰易懂
- [ ] 数据准确性 ≥ 95%

---

## 风险评估 (Risk Assessment)

### 高风险项目
1. **指标映射维护成本**: 需要持续维护和更新映射关系
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

---

## 参考资料

### SEC官方数据源
- **公司映射**: `https://www.sec.gov/files/company_tickers.json`
- **XBRL分类帐**: FASB US-GAAP Financial Reporting Taxonomy
- **EDGAR API**: `https://data.sec.gov/submissions/`

### 技术文档
- **XBRL规范**: XBRL 2.1 Specification
- **iXBRL规范**: Inline XBRL 1.1 Specification
- **SEC EDGAR**: Electronic Data Gathering, Analysis, and Retrieval System