"""
基本功能测试 - 测试各个模块能否正常导入和基本功能
"""

import os
import sys
import pytest

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

class TestImports:
    """测试模块导入"""
    
    def test_config_import(self):
        """测试配置模块导入"""
        from src.config import TICKER_TO_CIK, OPENAI_MODEL, OPENAI_TEMPERATURE
        
        assert TICKER_TO_CIK is not None
        assert len(TICKER_TO_CIK) > 0
        assert OPENAI_MODEL == "gpt-3.5-turbo"
        assert OPENAI_TEMPERATURE == 0.0
    
    def test_sec_retriever_import(self):
        """测试SEC检索器导入"""
        from src.sec_retriever import get_latest_10k_html, get_filing_html
        
        # 测试函数是否可调用
        assert callable(get_latest_10k_html)
        assert callable(get_filing_html)
    
    def test_xbrl_extractor_import(self):
        """测试XBRL提取器导入"""
        from src.xbrl_extractor import extract_revenue_from_html, extract_metric_from_html
        
        assert callable(extract_revenue_from_html)
        assert callable(extract_metric_from_html)
    
    def test_orchestrator_import(self):
        """测试编排器导入"""
        from src.orchestrator import app, METRIC_TAG_MAPPING
        
        assert app is not None
        assert METRIC_TAG_MAPPING is not None
        assert len(METRIC_TAG_MAPPING) > 0

class TestConfigValidation:
    """测试配置验证"""
    
    def test_ticker_to_cik_mapping(self):
        """测试股票代码到CIK的映射"""
        from src.config import TICKER_TO_CIK
        
        # 检查必需的股票代码
        required_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        
        for ticker in required_tickers:
            assert ticker in TICKER_TO_CIK
            cik = TICKER_TO_CIK[ticker]
            assert len(cik) == 10
            assert cik.isdigit()
    
    def test_openai_config(self):
        """测试OpenAI配置"""
        from src.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
        
        # API密钥可能为None（如果未设置环境变量）
        # 但模型和温度应该有默认值
        assert OPENAI_MODEL == "gpt-3.5-turbo"
        assert OPENAI_TEMPERATURE == 0.0

class TestXBRLExtractor:
    """测试XBRL提取器基本功能"""
    
    def test_extract_metric_from_sample_html(self):
        """测试从示例HTML提取指标"""
        from src.xbrl_extractor import extract_metric_from_html
        
        # 示例XBRL HTML内容
        sample_html = """
        <html>
            <body>
                <ix:nonfraction name="us-gaap:Revenues" contextref="c1" unitref="usd">383285000000</ix:nonfraction>
                <ix:nonfraction name="us-gaap:NetIncomeLoss" contextref="c1" unitref="usd">99803000000</ix:nonfraction>
            </body>
        </html>
        """
        
        # 测试收入提取
        result = extract_metric_from_html(sample_html, "us-gaap:Revenues")
        assert result is not None
        value, unit = result
        assert value == "383285000000"
        assert unit == "usd"
        
        # 测试净利润提取
        result = extract_metric_from_html(sample_html, "us-gaap:NetIncomeLoss")
        assert result is not None
        value, unit = result
        assert value == "99803000000"
        assert unit == "usd"
        
        # 测试不存在的指标
        result = extract_metric_from_html(sample_html, "us-gaap:NonExistentMetric")
        assert result is None

class TestOrchestratorBasic:
    """测试编排器基本功能"""
    
    def test_metric_tag_mapping(self):
        """测试指标标签映射"""
        from src.orchestrator import METRIC_TAG_MAPPING
        
        # 检查必需的映射
        assert "Revenues" in METRIC_TAG_MAPPING
        assert "NetIncome" in METRIC_TAG_MAPPING
        assert METRIC_TAG_MAPPING["Revenues"] == "us-gaap:Revenues"
        assert METRIC_TAG_MAPPING["NetIncome"] == "us-gaap:NetIncomeLoss"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 