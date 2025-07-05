#!/usr/bin/env python3
"""
快速评测脚本 - 只运行几个简单的测试用例
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.langgraph_orchestrator import process_query_with_langgraph
from src.config import OPENAI_API_KEY

async def test_single_query(query: str, description: str = ""):
    """测试单个查询"""
    print(f"\n🧪 测试: {description}")
    print(f"📋 查询: {query}")
    print("-" * 40)
    
    try:
        result = await process_query_with_langgraph(query)
        
        if result["success"]:
            print("✅ 成功!")
            print(f"📊 解析结果: {result['parsed_intent']}")
            if "result" in result:
                print(f"📈 提取结果: {result['result']}")
        else:
            print("❌ 失败!")
            print(f"🔍 错误: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

async def main():
    """主函数"""
    print("🚀 LangGraph快速评测")
    print("=" * 50)
    
    # 检查API密钥
    if not OPENAI_API_KEY:
        print("❌ 缺少OPENAI_API_KEY环境变量")
        print("请在.env文件中设置OPENAI_API_KEY")
        return
    
    print("✅ API密钥已设置")
    
    # 简单测试用例 - 使用更早的年份数据
    test_cases = [
        ("苹果公司2022年的收入是多少？", "中文查询 - 苹果收入"),
        ("MSFT 2022 net income", "英文查询 - 微软净利润"),
        ("什么是区块链技术？", "无效查询测试"),
        ("IBM 2022 revenue", "不支持的股票代码测试")
    ]
    
    # 运行测试
    for query, description in test_cases:
        await test_single_query(query, description)
        await asyncio.sleep(1)  # 添加延迟
    
    print("\n" + "=" * 50)
    print("🎯 快速评测完成!")

if __name__ == "__main__":
    asyncio.run(main()) 