#!/usr/bin/env python3
"""
InsightAgent MVP 完整功能演示脚本
展示智能Intent-Parser和评测系统
"""

import requests
import json
import time
import os
from datetime import datetime

class InsightAgentDemo:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        
    def print_header(self, title):
        """打印标题"""
        print("\n" + "="*60)
        print(f"🎯 {title}")
        print("="*60)
    
    def check_server(self):
        """检查服务器状态"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ 服务器连接正常")
                return True
            else:
                print("❌ 服务器响应异常")
                return False
        except:
            print("❌ 无法连接到服务器")
            print("💡 请先启动服务器: uvicorn src.orchestrator:app --reload")
            return False
    
    def demo_api_info(self):
        """演示API信息查询"""
        self.print_header("API信息查询")
        
        try:
            response = requests.get(f"{self.base_url}/info")
            if response.status_code == 200:
                info = response.json()
                print(f"📊 支持的股票: {len(info['supported_tickers']['list'])}个")
                print(f"📈 支持的指标: {len(info['supported_metrics']['mapping'])}个")
                print(f"📋 支持的财报类型: {len(info['supported_form_types'])}个")
                
                print("\n🏢 支持的公司:")
                for ticker, name in info['supported_tickers']['companies'].items():
                    print(f"   • {ticker}: {name}")
                
                print("\n📊 支持的财务指标:")
                for metric, desc in info['supported_metrics']['descriptions'].items():
                    print(f"   • {metric}: {desc}")
                    
                return True
        except Exception as e:
            print(f"❌ 获取API信息失败: {e}")
            return False
    
    def demo_structured_query(self):
        """演示结构化查询"""
        self.print_header("结构化查询演示")
        
        # 测试用例
        test_cases = [
            {"ticker": "AAPL", "metric": "Revenues", "year": 2023},
            {"ticker": "MSFT", "metric": "NetIncome", "year": 2022},
        ]
        
        for case in test_cases:
            print(f"\n🔍 查询: {case['ticker']} {case['metric']} {case['year']}")
            
            try:
                response = requests.get(
                    f"{self.base_url}/get-metric",
                    params=case,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 成功: {result['value']} {result.get('unit', '')}")
                    print(f"   XBRL标签: {result['xbrl_tag']}")
                else:
                    print(f"❌ 失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 请求失败: {e}")
    
    def demo_natural_language_query(self):
        """演示自然语言查询"""
        self.print_header("自然语言查询演示")
        
        # 测试查询
        queries = [
            "苹果公司2023年的收入是多少？",
            "Show me Microsoft's net income for 2022",
            "What were Tesla's total assets in 2023?",
            "Amazon quarterly revenue for 2023",
            "What is the weather like today?"  # 负面测试
        ]
        
        print("🧠 使用GPT-4进行智能解析...")
        print("⚠️  注意: 需要设置OPENAI_API_KEY环境变量")
        
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ 未设置OpenAI API密钥，跳过自然语言查询演示")
            return False
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. 查询: {query}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/query",
                    json={"text": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        parsed = result.get("parsed_intent", {})
                        financial_result = result.get("result", {})
                        
                        print(f"✅ 解析成功:")
                        print(f"   • 公司: {parsed.get('ticker')}")
                        print(f"   • 指标: {parsed.get('metric')}")
                        print(f"   • 年份: {parsed.get('year')}")
                        print(f"   • 类型: {parsed.get('form_type')}")
                        print(f"   • 结果: {financial_result.get('value')} {financial_result.get('unit', '')}")
                    else:
                        print(f"❌ 解析失败: {result.get('error')}")
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {e}")
            
            # 避免API频率限制
            time.sleep(1)
    
    def demo_evaluation_system(self):
        """演示评测系统"""
        self.print_header("智能评测系统演示")
        
        print("📋 检查评测数据集...")
        
        if not os.path.exists("eval_dataset.json"):
            print("❌ 评测数据集不存在")
            return False
        
        # 读取数据集信息
        try:
            with open("eval_dataset.json", 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            print(f"✅ 加载了 {len(dataset)} 个测试用例")
            
            # 显示测试用例示例
            print("\n📝 测试用例示例:")
            for i, case in enumerate(dataset[:3], 1):
                print(f"{i}. {case['query']}")
                print(f"   期望: {case.get('expected_params', {}).get('ticker')} "
                      f"{case.get('expected_params', {}).get('metric')} "
                      f"{case.get('expected_params', {}).get('year')}")
            
            if len(dataset) > 3:
                print(f"   ... 还有 {len(dataset) - 3} 个测试用例")
            
            print(f"\n💡 运行完整评测: python run_eval.py")
            
            return True
            
        except Exception as e:
            print(f"❌ 读取数据集失败: {e}")
            return False
    
    def demo_performance_test(self):
        """演示性能测试"""
        self.print_header("性能测试演示")
        
        # 简单的性能测试
        test_query = {"ticker": "AAPL", "metric": "Revenues", "year": 2023}
        num_requests = 5
        
        print(f"🚀 执行 {num_requests} 次结构化查询...")
        
        response_times = []
        success_count = 0
        
        for i in range(num_requests):
            start_time = time.time()
            
            try:
                response = requests.get(
                    f"{self.base_url}/get-metric",
                    params=test_query,
                    timeout=10
                )
                
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  {i+1}. ✅ {response_time:.2f}s")
                else:
                    print(f"  {i+1}. ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                response_time = time.time() - start_time
                print(f"  {i+1}. ❌ 错误: {e}")
        
        # 统计结果
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\n📊 性能统计:")
            print(f"   • 成功率: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
            print(f"   • 平均响应时间: {avg_time:.2f}秒")
            print(f"   • 最快响应: {min_time:.2f}秒")
            print(f"   • 最慢响应: {max_time:.2f}秒")
    
    def run_full_demo(self):
        """运行完整演示"""
        print("🎬 InsightAgent MVP 完整功能演示")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查服务器
        if not self.check_server():
            return False
        
        # 1. API信息演示
        self.demo_api_info()
        
        # 2. 结构化查询演示  
        self.demo_structured_query()
        
        # 3. 自然语言查询演示
        self.demo_natural_language_query()
        
        # 4. 评测系统演示
        self.demo_evaluation_system()
        
        # 5. 性能测试演示
        self.demo_performance_test()
        
        # 总结
        self.print_header("演示完成")
        print("🎉 InsightAgent MVP 所有功能演示完成!")
        print("\n📚 后续步骤:")
        print("   1. 设置 OPENAI_API_KEY 环境变量")
        print("   2. 运行完整评测: python run_eval.py")
        print("   3. 查看API文档: http://127.0.0.1:8000/docs")
        print("   4. 开始使用自然语言查询功能!")
        
        return True

def main():
    """主函数"""
    demo = InsightAgentDemo()
    demo.run_full_demo()

if __name__ == "__main__":
    main() 