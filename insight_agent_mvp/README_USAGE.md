# InsightAgent MVP 使用指南

## 🚀 快速开始

### 方式1：一键启动（推荐）
```bash
# 激活conda环境
conda activate llm

# 运行快速启动脚本
python scripts/quick_start.py
```

### 方式2：手动配置
#### 1. 环境配置
```bash
# 激活conda环境
conda activate llm

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

#### 2. 运行测试
```bash
# 运行基本测试
python -m pytest tests/test_basic_functionality.py -v

# 运行所有测试
python run_tests.py
```

#### 3. 启动LangGraph工作流
```bash
python -m src.langgraph_orchestrator
```

## 🎯 功能演示

### 完整功能演示
```bash
python scripts/demo.py
```

### 评测系统
```bash
# 运行完整评测
python evaluation/run_eval.py

# 快速评测  
python evaluation/quick_eval.py
```

## 📋 API端点

### 基本端点
- `GET /` - API信息
- `GET /info` - 支持的股票和指标信息

### 数据查询端点  
- `GET /get-metric` - 结构化查询
- `POST /query` - 自然语言查询

### 示例使用

#### 结构化查询
```bash
curl "http://localhost:8000/get-metric?ticker=AAPL&metric=Revenues&year=2023"
```

#### 自然语言查询
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "苹果公司2023年的收入是多少？"}'
```

## 🏗️ 架构说明

### 核心架构 (LangGraph)
- **`src/langgraph_orchestrator.py`**: 主要的工作流编排器
- 图形化工作流管理
- 更好的状态管理和错误处理
- 支持复杂的决策流程
- 可扩展性更强

### 核心组件
- **`src/config.py`**: 配置管理
- **`src/sec_retriever.py`**: SEC数据检索
- **`src/xbrl_extractor.py`**: XBRL数据提取

## 🔧 故障排除

### 常见问题

1. **模块导入错误**
   ```
   解决方案：确保在项目根目录运行，检查__init__.py文件是否存在
   ```

2. **OpenAI API错误**
   ```
   解决方案：检查.env文件中的OPENAI_API_KEY是否正确设置
   ```

3. **SEC数据检索失败**
   ```
   解决方案：检查网络连接，确保SEC API可访问
   ```

## 📊 支持的功能

### 支持的公司
- AAPL (Apple Inc.)
- MSFT (Microsoft Corporation)
- GOOGL (Alphabet Inc.)
- AMZN (Amazon.com Inc.)
- TSLA (Tesla Inc.)
- META (Meta Platforms Inc.)
- NVDA (NVIDIA Corporation)
- NFLX (Netflix Inc.)

### 支持的财务指标
- Revenues (营业收入)
- NetIncome (净利润)
- TotalAssets (总资产)
- TotalLiabilities (总负债)
- StockholdersEquity (股东权益)

### 支持的财报类型
- 10-K (年度财报)
- 10-Q (季度财报)

## 🧪 测试说明

项目包含完整的测试套件：

### 单元测试
- `test_basic_functionality.py` - 基本功能和导入测试
- `test_sec_retriever.py` - SEC数据检索测试
- `test_langgraph_orchestrator.py` - LangGraph工作流测试

### 集成测试
- `test_orchestrator.py` - API编排器测试
- `test_integration.py` - 集成测试

### 真实API测试
- `evaluation/` - 完整的评测系统，使用真实SEC API
  - 包含10个测试用例，覆盖主要功能
  - 支持中英文查询
  - 测试8家公司的财务数据
  - 100%成功率验证

运行特定测试：
```bash
python -m pytest tests/test_basic_functionality.py -v
```

## 📁 项目结构

```
insight_agent_mvp/
├── src/                          # 核心代码模块
│   ├── langgraph_orchestrator.py # LangGraph工作流编排器
│   ├── config.py                 # 配置管理
│   ├── sec_retriever.py          # SEC数据检索
│   └── xbrl_extractor.py         # XBRL数据提取
├── tests/                        # 测试套件
│   └── test_*.py                 # 各种测试文件
├── evaluation/                   # 评测系统
│   ├── run_eval.py               # 主评测脚本
│   ├── quick_eval.py             # 快速评测
│   └── eval_dataset.json         # 测试数据集
├── scripts/                      # 演示和启动脚本
│   ├── quick_start.py            # 快速启动
│   └── demo.py                   # 功能演示
└── run_tests.py                  # 测试运行器
```

## 🔮 下一步开发

### 优先级1: 核心功能完善
- [x] LangGraph架构实现
- [x] 完整评测系统
- [ ] 缓存机制添加
- [ ] 更多财务指标支持

### 优先级2: 性能优化
- [ ] 异步处理优化
- [ ] 错误处理增强
- [ ] 状态持久化

### 优先级3: 扩展功能
- [ ] 更多公司支持
- [ ] 历史数据趋势分析
- [ ] 数据可视化 