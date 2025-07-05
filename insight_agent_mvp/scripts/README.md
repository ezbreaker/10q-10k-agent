# Scripts 文件夹

这个文件夹包含了InsightAgent MVP项目的演示和启动脚本。

## 脚本说明

### 🚀 quick_start.py
**快速启动脚本** - 一键配置和启动系统

功能：
- 自动检查环境配置
- 安装项目依赖
- 设置OpenAI API密钥
- 测试基本功能
- 启动FastAPI服务器

使用方法：
```bash
python scripts/quick_start.py
```

### 🎯 demo.py  
**完整功能演示脚本** - 展示系统的各项功能

功能：
- API信息查询演示
- 结构化查询演示
- 自然语言查询演示
- 评测系统演示
- 性能测试演示

使用方法：
```bash
python scripts/demo.py
```

**注意**: 运行demo.py前请确保：
1. FastAPI服务器已启动: `uvicorn src.orchestrator:app --reload`
2. 已配置OpenAI API密钥

## 使用场景

- **新用户**: 使用 `quick_start.py` 快速部署和验证环境
- **功能展示**: 使用 `demo.py` 演示系统能力
- **开发调试**: 两个脚本都可以用于测试和验证系统状态 