"""
测试API编排器 src/orchestrator.py
"""

import os
import sys
import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入FastAPI应用
from orchestrator import app

# 创建测试客户端
client = TestClient(app)

class TestBasicEndpoints:
    """测试基本API端点"""
    
    def test_root_endpoint(self):
        """测试根路径端点"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert data["name"] == "InsightAgent MVP"
        assert "endpoints" in data
    
    def test_info_endpoint(self):
        """测试信息端点"""
        response = client.get("/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "supported_tickers" in data
        assert "supported_metrics" in data
        assert "supported_form_types" in data
        
        # 检查支持的股票代码
        tickers = data["supported_tickers"]["list"]
        assert "AAPL" in tickers
        assert "MSFT" in tickers
        
        # 检查支持的指标
        metrics = data["supported_metrics"]["mapping"]
        assert "Revenues" in metrics
        assert "NetIncome" in metrics
    
    def test_supported_tickers_endpoint(self):
        """测试支持的股票代码端点"""
        response = client.get("/supported-tickers")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert "AAPL" in data
        assert "MSFT" in data
    
    def test_supported_metrics_endpoint(self):
        """测试支持的指标端点"""
        response = client.get("/supported-metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "Revenues" in data
        assert "NetIncome" in data

class TestStructuredQueries:
    """测试结构化查询"""
    
    @patch('orchestrator.get_filing_html')
    @patch('orchestrator.extract_metric_from_html')
    def test_get_metric_success(self, mock_extract, mock_get_filing):
        """测试成功的指标查询"""
        # 模拟SEC检索
        mock_get_filing.return_value = "<html>Mock HTML content</html>"
        
        # 模拟XBRL提取
        mock_extract.return_value = ("383285000000", "USD")
        
        response = client.get("/get-metric", params={
            "ticker": "AAPL",
            "metric": "Revenues",
            "year": 2023
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticker"] == "AAPL"
        assert data["metric"] == "Revenues"
        assert data["year"] == 2023
        assert data["value"] == "383285000000"
        assert data["unit"] == "USD"
    
    def test_get_metric_invalid_ticker(self):
        """测试无效股票代码"""
        response = client.get("/get-metric", params={
            "ticker": "INVALID",
            "metric": "Revenues",
            "year": 2023
        })
        
        assert response.status_code == 404
    
    def test_get_metric_missing_params(self):
        """测试缺少必需参数"""
        response = client.get("/get-metric", params={
            "ticker": "AAPL"
            # 缺少metric和year
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('orchestrator.get_latest_10k_html')
    @patch('orchestrator.extract_revenue_from_html')
    def test_get_revenue_legacy(self, mock_extract, mock_get_html):
        """测试遗留的收入查询端点"""
        # 模拟数据
        mock_get_html.return_value = "<html>Mock HTML</html>"
        mock_extract.return_value = ("383285000000", "USD")
        
        response = client.get("/get-revenue", params={"ticker": "AAPL"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticker"] == "AAPL"
        assert data["revenue"] == "383285000000"

class TestNaturalLanguageQueries:
    """测试自然语言查询"""
    
    @patch('orchestrator.openai.ChatCompletion.create')
    @patch('orchestrator.get_metric_for_ticker')
    def test_query_endpoint_success(self, mock_get_metric, mock_openai):
        """测试成功的自然语言查询"""
        # 模拟OpenAI响应
        mock_openai.return_value = Mock(
            choices=[Mock(
                message=Mock(
                    tool_calls=[Mock(
                        function=Mock(
                            name="get_financial_metric",
                            arguments='{"ticker": "AAPL", "metric": "Revenues", "year": 2023}'
                        )
                    )]
                )
            )]
        )
        
        # 模拟指标检索结果
        mock_get_metric.return_value = {
            "ticker": "AAPL",
            "metric": "Revenues",
            "value": "383285000000",
            "unit": "USD"
        }
        
        response = client.post("/query", json={
            "text": "苹果公司2023年的收入是多少？"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "parsed_intent" in data
        assert "result" in data
        
        parsed = data["parsed_intent"]
        assert parsed["ticker"] == "AAPL"
        assert parsed["metric"] == "Revenues"
        assert parsed["year"] == 2023
    
    @patch('orchestrator.openai.ChatCompletion.create')
    def test_query_endpoint_no_tool_call(self, mock_openai):
        """测试LLM没有调用工具的情况"""
        # 模拟OpenAI响应（没有工具调用）
        mock_openai.return_value = Mock(
            choices=[Mock(
                message=Mock(tool_calls=None)
            )]
        )
        
        response = client.post("/query", json={
            "text": "今天天气怎么样？"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
    
    def test_query_endpoint_no_openai_key(self):
        """测试没有OpenAI API密钥的情况"""
        with patch('orchestrator.OPENAI_API_KEY', None):
            response = client.post("/query", json={
                "text": "苹果公司收入"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
    
    def test_query_endpoint_invalid_request(self):
        """测试无效请求格式"""
        response = client.post("/query", json={
            # 缺少text字段
        })
        
        assert response.status_code == 422

class TestErrorHandling:
    """测试错误处理"""
    
    @patch('orchestrator.get_filing_html')
    def test_sec_retrieval_error(self, mock_get_filing):
        """测试SEC检索错误"""
        mock_get_filing.side_effect = ValueError("Filing not found")
        
        response = client.get("/get-metric", params={
            "ticker": "AAPL",
            "metric": "Revenues",
            "year": 2023
        })
        
        assert response.status_code == 404
    
    @patch('orchestrator.get_filing_html')
    @patch('orchestrator.extract_metric_from_html')
    def test_xbrl_extraction_error(self, mock_extract, mock_get_filing):
        """测试XBRL提取错误"""
        mock_get_filing.return_value = "<html>Mock HTML</html>"
        mock_extract.return_value = None  # 提取失败
        
        response = client.get("/get-metric", params={
            "ticker": "AAPL",
            "metric": "Revenues",
            "year": 2023
        })
        
        assert response.status_code == 404

class TestAPIDocumentation:
    """测试API文档"""
    
    def test_openapi_schema(self):
        """测试OpenAPI模式"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "InsightAgent MVP"
    
    def test_docs_endpoint(self):
        """测试文档端点"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 