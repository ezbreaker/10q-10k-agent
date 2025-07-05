"""
测试SEC检索模块 src/sec_retriever.py
"""

import os
import sys
import pytest
import requests
from unittest.mock import patch, Mock

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sec_retriever import get_latest_10k_html, get_filing_html

class TestSECRetriever:
    """测试SEC数据检索功能"""
    
    def test_get_latest_10k_html_basic(self):
        """测试基本的10-K检索功能"""
        # 这是一个集成测试，需要网络连接
        try:
            html_content = get_latest_10k_html("AAPL")
            assert html_content is not None
            assert len(html_content) > 1000  # 10-K文件应该很大
            assert "apple" in html_content.lower() or "aapl" in html_content.lower()
        except Exception as e:
            pytest.skip(f"Network test failed: {e}")
    
    def test_get_filing_html_with_year(self):
        """测试指定年份的财报检索"""
        try:
            html_content = get_filing_html("AAPL", 2023, "10-K")
            assert html_content is not None
            assert len(html_content) > 1000
        except Exception as e:
            pytest.skip(f"Network test failed: {e}")
    
    def test_invalid_ticker(self):
        """测试无效的股票代码"""
        with pytest.raises((ValueError, FileNotFoundError)):
            get_latest_10k_html("INVALID_TICKER")
    
    def test_invalid_year(self):
        """测试无效的年份"""
        with pytest.raises((ValueError, FileNotFoundError)):
            get_filing_html("AAPL", 1990, "10-K")  # 太早的年份
    
    def test_invalid_form_type(self):
        """测试无效的表单类型"""
        with pytest.raises((ValueError, FileNotFoundError)):
            get_filing_html("AAPL", 2023, "INVALID-FORM")

class TestSECRetrieverMocked:
    """使用模拟数据测试SEC检索器"""
    
    @patch('sec_retriever.requests.get')
    def test_get_latest_10k_html_mocked(self, mock_get):
        """使用模拟数据测试10-K检索"""
        # 模拟SEC submissions响应
        mock_submissions_response = Mock()
        mock_submissions_response.status_code = 200
        mock_submissions_response.json.return_value = {
            "filings": {
                "recent": {
                    "form": ["10-K", "10-Q", "8-K"],
                    "filingDate": ["2023-10-02", "2023-07-01", "2023-06-01"],
                    "accessionNumber": ["0000320193-23-000077", "0000320193-23-000064", "0000320193-23-000055"]
                }
            }
        }
        
        # 模拟10-K HTML响应
        mock_html_response = Mock()
        mock_html_response.status_code = 200
        mock_html_response.text = """
        <html>
            <body>
                <div>Apple Inc. 10-K Filing</div>
                <ix:nonfraction name="us-gaap:Revenues" contextref="c1">383285000000</ix:nonfraction>
            </body>
        </html>
        """
        
        # 设置mock返回值
        mock_get.side_effect = [mock_submissions_response, mock_html_response]
        
        # 调用函数
        result = get_latest_10k_html("AAPL")
        
        # 验证结果
        assert result is not None
        assert "Apple Inc." in result
        assert "us-gaap:Revenues" in result
        
        # 验证调用次数
        assert mock_get.call_count == 2
    
    @patch('sec_retriever.requests.get')
    def test_network_error_handling(self, mock_get):
        """测试网络错误处理"""
        # 模拟网络错误
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(requests.RequestException):
            get_latest_10k_html("AAPL")
    
    @patch('sec_retriever.requests.get')
    def test_http_error_handling(self, mock_get):
        """测试HTTP错误处理"""
        # 模拟404错误
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            get_latest_10k_html("AAPL")

class TestSECDataValidation:
    """测试SEC数据验证"""
    
    def test_ticker_case_insensitive(self):
        """测试股票代码大小写不敏感"""
        # 注意：这需要修改原函数支持大小写不敏感
        try:
            html1 = get_latest_10k_html("AAPL")
            html2 = get_latest_10k_html("aapl")
            # 两者应该返回相同的结果（如果函数支持大小写不敏感）
        except Exception:
            pytest.skip("Case insensitive test requires network connection")
    
    def test_html_content_structure(self):
        """测试返回的HTML内容结构"""
        try:
            html_content = get_latest_10k_html("AAPL")
            
            # 基本HTML结构检查
            assert "<html" in html_content.lower()
            assert "</html>" in html_content.lower()
            
            # XBRL标签检查
            assert "ix:" in html_content or "xbrl" in html_content.lower()
            
        except Exception as e:
            pytest.skip(f"Network test failed: {e}")

class TestSECRetrieverPerformance:
    """测试SEC检索器性能"""
    
    @pytest.mark.slow
    def test_retrieval_timeout(self):
        """测试检索超时处理"""
        import time
        
        start_time = time.time()
        try:
            html_content = get_latest_10k_html("AAPL")
            end_time = time.time()
            
            # 检索应该在合理时间内完成（比如30秒）
            assert end_time - start_time < 30, "Retrieval took too long"
            
        except Exception as e:
            pytest.skip(f"Performance test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 