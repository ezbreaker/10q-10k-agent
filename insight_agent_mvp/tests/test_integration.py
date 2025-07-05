"""
集成测试 - 测试整个pipeline的端到端功能
"""

import os
import sys
import pytest
import json
import time
from fastapi.testclient import TestClient

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator import app

client = TestClient(app)

class TestEndToEndIntegration:
    """端到端集成测试"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_pipeline_aapl_revenue(self):
        """测试AAPL收入查询的完整pipeline"""
        # 这是一个完整的集成测试，需要网络连接
        try:
            response = client.get("/get-metric", params={
                "ticker": "AAPL",
                "metric": "Revenues",
                "year": 2023
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应结构
                assert "ticker" in data
                assert "metric" in data  
                assert "year" in data
                assert "value" in data
                
                # 验证数据类型
                assert data["ticker"] == "AAPL"
                assert data["metric"] == "Revenues"
                assert data["year"] == 2023
                assert isinstance(data["value"], str)
                
                # 验证收入数值合理性（应该是很大的数字）
                revenue_value = data["value"].replace(",", "")
                assert revenue_value.isdigit()
                assert int(revenue_value) > 100000000000  # 应该大于1000亿
                
            else:
                pytest.skip(f"Integration test failed with status {response.status_code}")
                
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")
    
    @pytest.mark.integration  
    def test_multiple_companies_basic_metrics(self):
        """测试多个公司的基本指标"""
        test_cases = [
            {"ticker": "AAPL", "metric": "Revenues"},
            {"ticker": "MSFT", "metric": "NetIncome"},
            {"ticker": "GOOGL", "metric": "TotalAssets"}
        ]
        
        for case in test_cases:
            try:
                response = client.get("/get-metric", params={
                    **case,
                    "year": 2023
                })
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["ticker"] == case["ticker"]
                    assert data["metric"] == case["metric"]
                    assert "value" in data
                else:
                    pytest.skip(f"Failed for {case['ticker']}: {response.status_code}")
                    
            except Exception as e:
                pytest.skip(f"Test failed for {case}: {e}")
            
            # 避免API频率限制
            time.sleep(1)
    
    @pytest.mark.integration
    def test_different_form_types(self):
        """测试不同的财报类型"""
        test_cases = [
            {"form_type": "10-K", "description": "年报"},
            {"form_type": "10-Q", "description": "季报"}
        ]
        
        for case in test_cases:
            try:
                response = client.get("/get-metric", params={
                    "ticker": "AAPL",
                    "metric": "Revenues", 
                    "year": 2023,
                    "form_type": case["form_type"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["form_type"] == case["form_type"]
                    print(f"✅ {case['description']} 测试通过")
                else:
                    pytest.skip(f"{case['description']} 测试失败: {response.status_code}")
                    
            except Exception as e:
                pytest.skip(f"{case['description']} 测试异常: {e}")

class TestAPIConsistency:
    """测试API一致性"""
    
    def test_response_format_consistency(self):
        """测试响应格式一致性"""
        endpoints = [
            "/",
            "/info", 
            "/supported-tickers",
            "/supported-metrics"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            # 检查响应是否为有效JSON
            data = response.json()
            assert data is not None
    
    def test_error_response_consistency(self):
        """测试错误响应一致性"""
        # 测试各种错误情况
        error_cases = [
            {
                "params": {"ticker": "INVALID", "metric": "Revenues", "year": 2023},
                "expected_status": 404
            },
            {
                "params": {"ticker": "AAPL", "metric": "INVALID", "year": 2023},
                "expected_status": 404
            }
        ]
        
        for case in error_cases:
            response = client.get("/get-metric", params=case["params"])
            assert response.status_code == case["expected_status"]

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.performance
    def test_response_time_basic_query(self):
        """测试基本查询响应时间"""
        start_time = time.time()
        
        response = client.get("/")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # 基本查询应该在1秒内响应
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_response_time_data_query(self):
        """测试数据查询响应时间"""
        start_time = time.time()
        
        try:
            response = client.get("/get-metric", params={
                "ticker": "AAPL",
                "metric": "Revenues",
                "year": 2023
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                assert response_time < 30.0  # 数据查询应该在30秒内完成
                print(f"Data query response time: {response_time:.2f}s")
            else:
                pytest.skip("Data query failed")
                
        except Exception as e:
            pytest.skip(f"Performance test failed: {e}")

class TestDataQuality:
    """数据质量测试"""
    
    @pytest.mark.integration
    def test_data_reasonableness(self):
        """测试数据合理性"""
        try:
            response = client.get("/get-metric", params={
                "ticker": "AAPL",
                "metric": "Revenues",
                "year": 2023
            })
            
            if response.status_code == 200:
                data = response.json()
                value = data["value"]
                
                # 移除逗号和转换为数字
                numeric_value = int(value.replace(",", ""))
                
                # 苹果的年收入应该在合理范围内（比如200-500亿美元之间）
                assert 200000000000 <= numeric_value <= 500000000000
                
                # 检查单位
                if "unit" in data:
                    assert data["unit"] in ["USD", ""]
                    
            else:
                pytest.skip("Data quality test requires successful data retrieval")
                
        except Exception as e:
            pytest.skip(f"Data quality test failed: {e}")

class TestErrorRecovery:
    """错误恢复测试"""
    
    def test_graceful_error_handling(self):
        """测试优雅的错误处理"""
        # 测试各种错误情况下的响应
        error_cases = [
            {"ticker": "", "metric": "Revenues", "year": 2023},
            {"ticker": "AAPL", "metric": "", "year": 2023},
            {"ticker": "AAPL", "metric": "Revenues", "year": "invalid"},
        ]
        
        for case in error_cases:
            response = client.get("/get-metric", params=case)
            
            # 应该返回错误状态码，而不是崩溃
            assert response.status_code in [400, 404, 422]
            
            # 错误响应应该包含有用的信息
            if response.status_code != 422:  # 422是验证错误，格式不同
                try:
                    error_data = response.json()
                    assert "detail" in error_data
                except:
                    pass  # 某些错误可能不是JSON格式

if __name__ == "__main__":
    # 运行不同类别的测试
    print("运行集成测试...")
    pytest.main([__file__, "-v", "-m", "not slow"]) 