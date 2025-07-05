#!/usr/bin/env python3
"""
LangGraph评测脚本
评估自然语言理解准确率、端到端准确率、响应时间等指标
"""

import json
import asyncio
import time
import sys
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.langgraph_orchestrator import process_query_with_langgraph
from src.config import OPENAI_API_KEY

@dataclass
class EvalResult:
    """评测结果数据类"""
    test_id: str
    query: str
    expected_intent: Dict[str, Any]
    actual_result: Dict[str, Any]
    nlu_correct: bool
    end_to_end_correct: bool
    response_time: float
    error_message: str = ""
    category: str = ""
    description: str = ""

class LangGraphEvaluator:
    """LangGraph评测器"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.results: List[EvalResult] = []
        self.start_time = None
        self.end_time = None
        
    def load_dataset(self) -> List[Dict]:
        """加载测试数据集"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载数据集失败: {e}")
            return []
    
    def check_nlu_accuracy(self, expected_intent: Dict, actual_result: Dict) -> bool:
        """检查自然语言理解准确率"""
        if not actual_result.get("success", False):
            # 如果实际结果失败，检查是否是预期的错误
            if "error" in expected_intent:
                return True
            return False
        
        if "error" in expected_intent:
            # 预期错误但实际成功
            return False
        
        actual_intent = actual_result.get("parsed_intent", {})
        
        # 检查关键字段
        key_fields = ["ticker", "metric", "year", "form_type"]
        for field in key_fields:
            if field in expected_intent:
                actual_val = actual_intent.get(field)
                expected_val = expected_intent[field]
                
                # 特殊处理年份：允许字符串和整数互相匹配
                if field == "year":
                    try:
                        if int(actual_val) != int(expected_val):
                            return False
                    except (ValueError, TypeError):
                        return False
                else:
                    if actual_val != expected_val:
                        return False
        
        return True
    
    def check_end_to_end_accuracy(self, expected_intent: Dict, actual_result: Dict) -> bool:
        """检查端到端准确率"""
        if not actual_result.get("success", False):
            # 如果实际结果失败，检查是否是预期的错误
            if "error" in expected_intent:
                return True
            return False
        
        if "error" in expected_intent:
            # 预期错误但实际成功
            return False
        
        # 检查是否有提取的结果
        result = actual_result.get("result")
        if not result:
            return False
        
        # 检查结果是否包含必要字段
        required_fields = ["ticker", "metric", "year", "value", "unit"]
        for field in required_fields:
            if field not in result:
                return False
        
        # 检查ticker和metric是否匹配
        if result.get("ticker") != expected_intent.get("ticker"):
            return False
        if result.get("metric") != expected_intent.get("metric"):
            return False
        
        return True
    
    async def evaluate_single_query(self, test_case: Dict) -> EvalResult:
        """评估单个查询"""
        test_id = test_case.get("id", "unknown")
        query = test_case.get("query", "")
        expected_intent = test_case.get("expected_intent", {})
        category = test_case.get("category", "")
        description = test_case.get("description", "")
        
        print(f"📋 测试 {test_id}: {query}")
        
        # 测量响应时间
        start_time = time.time()
        
        try:
            # 使用LangGraph处理查询
            actual_result = await process_query_with_langgraph(query)
            response_time = time.time() - start_time
            
            # 检查NLU准确率
            nlu_correct = self.check_nlu_accuracy(expected_intent, actual_result)
            
            # 检查端到端准确率
            end_to_end_correct = self.check_end_to_end_accuracy(expected_intent, actual_result)
            
            # 创建结果对象
            result = EvalResult(
                test_id=test_id,
                query=query,
                expected_intent=expected_intent,
                actual_result=actual_result,
                nlu_correct=nlu_correct,
                end_to_end_correct=end_to_end_correct,
                response_time=response_time,
                category=category,
                description=description
            )
            
            # 输出结果
            status = "✅" if nlu_correct and end_to_end_correct else "❌"
            print(f"  {status} NLU: {nlu_correct}, E2E: {end_to_end_correct}, 耗时: {response_time:.2f}s")
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = str(e)
            
            result = EvalResult(
                test_id=test_id,
                query=query,
                expected_intent=expected_intent,
                actual_result={"error": error_message, "success": False},
                nlu_correct=False,
                end_to_end_correct=False,
                response_time=response_time,
                error_message=error_message,
                category=category,
                description=description
            )
            
            print(f"  ❌ 执行失败: {error_message}")
            return result
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """运行完整评测"""
        print("🧪 开始LangGraph评测")
        print("=" * 60)
        
        # 检查API密钥
        if not OPENAI_API_KEY:
            print("❌ 缺少OPENAI_API_KEY环境变量")
            return {"error": "缺少OPENAI_API_KEY环境变量"}
        
        # 加载数据集
        dataset = self.load_dataset()
        if not dataset:
            return {"error": "数据集加载失败"}
        
        print(f"📊 数据集大小: {len(dataset)}个测试用例")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # 运行所有测试用例
        for test_case in dataset:
            result = await self.evaluate_single_query(test_case)
            self.results.append(result)
            
            # 添加延迟以避免API限制
            await asyncio.sleep(0.5)
        
        self.end_time = datetime.now()
        
        # 生成报告
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成评测报告"""
        if not self.results:
            return {"error": "没有评测结果"}
        
        total_tests = len(self.results)
        nlu_correct = sum(1 for r in self.results if r.nlu_correct)
        e2e_correct = sum(1 for r in self.results if r.end_to_end_correct)
        
        nlu_accuracy = nlu_correct / total_tests * 100
        e2e_accuracy = e2e_correct / total_tests * 100
        
        avg_response_time = sum(r.response_time for r in self.results) / total_tests
        
        # 按类别统计
        category_stats = {}
        for result in self.results:
            category = result.category
            if category not in category_stats:
                category_stats[category] = {
                    "total": 0,
                    "nlu_correct": 0,
                    "e2e_correct": 0,
                    "avg_response_time": 0
                }
            
            category_stats[category]["total"] += 1
            if result.nlu_correct:
                category_stats[category]["nlu_correct"] += 1
            if result.end_to_end_correct:
                category_stats[category]["e2e_correct"] += 1
            category_stats[category]["avg_response_time"] += result.response_time
        
        # 计算每个类别的准确率
        for category, stats in category_stats.items():
            if stats["total"] > 0:
                stats["nlu_accuracy"] = stats["nlu_correct"] / stats["total"] * 100
                stats["e2e_accuracy"] = stats["e2e_correct"] / stats["total"] * 100
                stats["avg_response_time"] = stats["avg_response_time"] / stats["total"]
        
        # 生成详细报告
        report = {
            "summary": {
                "total_tests": total_tests,
                "nlu_accuracy": nlu_accuracy,
                "e2e_accuracy": e2e_accuracy,
                "avg_response_time": avg_response_time,
                "evaluation_time": str(self.end_time - self.start_time)
            },
            "category_stats": category_stats,
            "detailed_results": [
                {
                    "test_id": r.test_id,
                    "query": r.query,
                    "category": r.category,
                    "description": r.description,
                    "nlu_correct": r.nlu_correct,
                    "end_to_end_correct": r.end_to_end_correct,
                    "response_time": r.response_time,
                    "expected_intent": r.expected_intent,
                    "actual_result": r.actual_result,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """打印评测报告"""
        if "error" in report:
            print(f"❌ 评测失败: {report['error']}")
            return
        
        summary = report["summary"]
        category_stats = report["category_stats"]
        
        print("=" * 60)
        print("📊 LangGraph评测报告")
        print("=" * 60)
        
        print(f"📋 总体统计:")
        print(f"  • 总测试数: {summary['total_tests']}")
        print(f"  • NLU准确率: {summary['nlu_accuracy']:.1f}%")
        print(f"  • 端到端准确率: {summary['e2e_accuracy']:.1f}%")
        print(f"  • 平均响应时间: {summary['avg_response_time']:.2f}s")
        print(f"  • 评测耗时: {summary['evaluation_time']}")
        
        print(f"\n📈 分类统计:")
        for category, stats in category_stats.items():
            print(f"  • {category}:")
            print(f"    - 测试数: {stats['total']}")
            print(f"    - NLU准确率: {stats['nlu_accuracy']:.1f}%")
            print(f"    - 端到端准确率: {stats['e2e_accuracy']:.1f}%")
            print(f"    - 平均响应时间: {stats['avg_response_time']:.2f}s")
        
        print(f"\n❌ 失败用例:")
        failed_cases = [r for r in report["detailed_results"] if not (r["nlu_correct"] and r["end_to_end_correct"])]
        if failed_cases:
            for case in failed_cases:
                print(f"  • {case['test_id']}: {case['query']}")
                print(f"    - NLU: {case['nlu_correct']}, E2E: {case['end_to_end_correct']}")
                if case['error_message']:
                    print(f"    - 错误: {case['error_message']}")
        else:
            print("  🎉 所有测试用例都通过了！")
        
        print("=" * 60)
    
    def save_report(self, report: Dict[str, Any], output_path: str) -> None:
        """保存评测报告到文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"📝 报告已保存到: {output_path}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

async def main():
    """主函数"""
    # 设置路径
    current_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(current_dir, "eval_dataset.json")
    
    # 创建reports子文件夹
    reports_dir = os.path.join(current_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # 生成带时间戳的报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(reports_dir, f"eval_report_{timestamp}.json")
    
    # 创建评测器
    evaluator = LangGraphEvaluator(dataset_path)
    
    # 运行评测
    report = await evaluator.run_evaluation()
    
    # 打印报告
    evaluator.print_report(report)
    
    # 保存报告
    if "error" not in report:
        evaluator.save_report(report, report_path)

if __name__ == "__main__":
    asyncio.run(main()) 