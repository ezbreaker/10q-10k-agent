#!/usr/bin/env python3
"""
InsightAgent MVP 快速启动脚本
一键配置和启动系统
"""

import os
import sys
import subprocess
import time

def print_step(step, description):
    print(f"\n📋 步骤 {step}: {description}")
    print("-" * 50)

def setup_environment():
    """环境设置"""
    print_step(1, "环境设置")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}")
    
    # 检查conda环境
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'base')
    print(f"🐍 Conda环境: {conda_env}")
    
    return True

def install_dependencies():
    """安装依赖"""
    print_step(2, "安装依赖包")
    
    try:
        print("📦 安装requirements.txt中的依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def setup_openai_api():
    """设置OpenAI API"""
    print_step(3, "OpenAI API配置")
    
    # 检查现有配置
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "*" * 20 + api_key[-4:]
        print(f"✅ 已配置API密钥: {masked_key}")
        return True
    
    print("❌ 未设置OPENAI_API_KEY环境变量")
    print("\n🔧 配置方法:")
    print("方法1 - 临时设置 (推荐):")
    print("   export OPENAI_API_KEY='你的密钥'")
    print("\n方法2 - 创建.env文件:")
    print("   echo 'OPENAI_API_KEY=你的密钥' > .env")
    
    # 交互式输入
    print("\n💡 或者现在输入密钥:")
    api_key = input("请输入OpenAI API密钥 (按Enter跳过): ").strip()
    
    if api_key:
        # 临时设置
        os.environ["OPENAI_API_KEY"] = api_key
        # 保存到.env文件
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("✅ API密钥已配置")
        return True
    else:
        print("⚠️  未配置API密钥，自然语言功能将不可用")
        return False

def test_basic_import():
    """测试基本导入"""
    print_step(4, "测试模块导入")
    
    try:
        from src.orchestrator import app
        print("✅ orchestrator模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_openai_connection():
    """测试OpenAI连接"""
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  跳过OpenAI连接测试 (未配置API密钥)")
        return True
        
    print("🧪 测试OpenAI API连接...")
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # 简单测试
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=3
        )
        print("✅ OpenAI API连接成功!")
        return True
    except Exception as e:
        print(f"❌ OpenAI API连接失败: {e}")
        return False

def start_server():
    """启动服务器"""
    print_step(5, "启动服务器")
    
    print("🚀 启动FastAPI服务器...")
    print("📍 地址: http://127.0.0.1:8000")
    print("📚 文档: http://127.0.0.1:8000/docs")
    print("\n💡 按 Ctrl+C 停止服务器")
    
    try:
        # 启动服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.orchestrator:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

def show_usage_examples():
    """显示使用示例"""
    print("\n" + "="*60)
    print("📖 使用示例")
    print("="*60)
    
    print("\n1️⃣ 结构化查询:")
    print("curl 'http://127.0.0.1:8000/get-metric?ticker=AAPL&metric=Revenues&year=2023'")
    
    print("\n2️⃣ 自然语言查询:")
    print("curl -X POST 'http://127.0.0.1:8000/query' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"text\": \"苹果公司2023年的收入是多少？\"}'")
    
    print("\n3️⃣ 查看支持的功能:")
    print("curl 'http://127.0.0.1:8000/info'")
    
    print("\n4️⃣ 运行评测系统:")
    print("python run_eval.py")

def main():
    """主函数"""
    print("🚀 InsightAgent MVP 快速启动")
    print("=" * 60)
    
    success = True
    
    # 1. 环境设置
    if not setup_environment():
        success = False
        
    # 2. 安装依赖
    if success and not install_dependencies():
        success = False
        
    # 3. OpenAI配置
    if success:
        setup_openai_api()
        
    # 4. 测试导入
    if success and not test_basic_import():
        success = False
        
    # 5. 测试OpenAI
    if success:
        test_openai_connection()
    
    if success:
        # 显示使用示例
        show_usage_examples()
        
        # 询问是否启动服务器
        print("\n" + "="*60)
        response = input("🚀 是否现在启动服务器? (y/N): ").strip().lower()
        
        if response in ['y', 'yes', '是']:
            start_server()
        else:
            print("\n💡 手动启动服务器:")
            print("uvicorn src.orchestrator:app --host 127.0.0.1 --port 8000 --reload")
    else:
        print("\n❌ 配置过程中遇到问题，请检查上述错误")
        sys.exit(1)

if __name__ == "__main__":
    main() 