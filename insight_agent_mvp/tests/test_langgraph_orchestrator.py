"""
测试LangGraph编排器模块
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.langgraph_orchestrator import (
    WorkflowState, 
    parse_intent_node,
    retrieve_sec_data_node,
    extract_xbrl_data_node,
    should_continue,
    build_workflow,
    process_query_with_langgraph
)
from langgraph.graph import END

class TestLangGraphOrchestrator:
    """测试LangGraph编排器"""
    
    def test_workflow_state_creation(self):
        """测试工作流状态创建"""
        state = WorkflowState(
            query="test query",
            parsed_intent=None,
            html_content=None,
            extracted_value=None,
            error=None,
            success=False
        )
        
        assert state["query"] == "test query"
        assert state["parsed_intent"] is None
        assert state["success"] is False
    
    def test_should_continue_logic(self):
        """测试工作流继续逻辑"""
        # 成功状态
        success_state = WorkflowState(
            query="test",
            parsed_intent=None,
            html_content=None,
            extracted_value=None,
            error=None,
            success=True
        )
        
        result = should_continue(success_state)
        assert result == "continue"
        
        # 失败状态
        failure_state = WorkflowState(
            query="test",
            parsed_intent=None,
            html_content=None,
            extracted_value=None,
            error="some error",
            success=False
        )
        
        result = should_continue(failure_state)
        assert result == END
    
    def test_build_workflow(self):
        """测试工作流构建"""
        workflow = build_workflow()
        assert workflow is not None
        # 检查是否是编译后的工作流
        assert hasattr(workflow, 'invoke')
        assert hasattr(workflow, 'ainvoke')
    
    @patch('src.langgraph_orchestrator.llm')
    def test_parse_intent_node_success(self, mock_llm):
        """测试意图解析节点成功情况"""
        # 模拟LLM返回
        mock_response = Mock()
        mock_response.content = '{"ticker": "AAPL", "metric": "Revenues", "year": 2023, "form_type": "10-K"}'
        mock_llm.return_value = mock_response
        
        initial_state = WorkflowState(
            query="Apple 2023年的收入是多少？",
            parsed_intent=None,
            html_content=None,
            extracted_value=None,
            error=None,
            success=False
        )
        
        result = parse_intent_node(initial_state)
        
        assert result["success"] is True
        assert result["parsed_intent"]["ticker"] == "AAPL"
        assert result["parsed_intent"]["metric"] == "Revenues"
        assert result["parsed_intent"]["year"] == 2023
        assert result["error"] is None
    
    @patch('src.langgraph_orchestrator.llm')
    def test_parse_intent_node_failure(self, mock_llm):
        """测试意图解析节点失败情况"""
        # 模拟LLM返回错误
        mock_response = Mock()
        mock_response.content = '{"error": "无法理解查询"}'
        mock_llm.return_value = mock_response
        
        initial_state = WorkflowState(
            query="无法理解的查询",
            parsed_intent=None,
            html_content=None,
            extracted_value=None,
            error=None,
            success=False
        )
        
        result = parse_intent_node(initial_state)
        
        assert result["success"] is False
        assert result["error"] == "无法理解查询"
        assert result["parsed_intent"] is None
    
    @patch('src.langgraph_orchestrator.get_filing_html')
    def test_retrieve_sec_data_node_success(self, mock_get_filing_html):
        """测试SEC数据检索节点成功情况"""
        # 模拟SEC数据检索
        mock_html = "<html><body>Mock SEC filing data</body></html>"
        mock_get_filing_html.return_value = mock_html
        
        state_with_intent = WorkflowState(
            query="test",
            parsed_intent={"ticker": "AAPL", "year": 2023, "form_type": "10-K"},
            html_content=None,
            extracted_value=None,
            error=None,
            success=True
        )
        
        result = retrieve_sec_data_node(state_with_intent)
        
        assert result["success"] is True
        assert result["html_content"] == mock_html
        assert result["error"] is None
        mock_get_filing_html.assert_called_once_with("AAPL", 2023, "10-K")
    
    def test_retrieve_sec_data_node_invalid_ticker(self):
        """测试SEC数据检索节点无效股票代码"""
        state_with_invalid_ticker = WorkflowState(
            query="test",
            parsed_intent={"ticker": "INVALID", "year": 2023, "form_type": "10-K"},
            html_content=None,
            extracted_value=None,
            error=None,
            success=True
        )
        
        result = retrieve_sec_data_node(state_with_invalid_ticker)
        
        assert result["success"] is False
        assert "不支持的股票代码" in result["error"]
    
    @patch('src.langgraph_orchestrator.extract_metric_from_html')
    def test_extract_xbrl_data_node_success(self, mock_extract_metric):
        """测试XBRL数据提取节点成功情况"""
        # 模拟XBRL数据提取
        mock_extract_metric.return_value = ("383285000000", "usd")
        
        state_with_html = WorkflowState(
            query="test",
            parsed_intent={"ticker": "AAPL", "metric": "Revenues", "year": 2023, "form_type": "10-K"},
            html_content="<html>mock html</html>",
            extracted_value=None,
            error=None,
            success=True
        )
        
        result = extract_xbrl_data_node(state_with_html)
        
        assert result["success"] is True
        assert result["extracted_value"]["ticker"] == "AAPL"
        assert result["extracted_value"]["metric"] == "Revenues"
        assert result["extracted_value"]["value"] == "383285000000"
        assert result["extracted_value"]["unit"] == "usd"
        assert result["error"] is None
        mock_extract_metric.assert_called_once_with("<html>mock html</html>", "us-gaap:Revenues")
    
    @patch('src.langgraph_orchestrator.extract_metric_from_html')
    def test_extract_xbrl_data_node_not_found(self, mock_extract_metric):
        """测试XBRL数据提取节点找不到数据"""
        # 模拟找不到数据
        mock_extract_metric.return_value = None
        
        state_with_html = WorkflowState(
            query="test",
            parsed_intent={"ticker": "AAPL", "metric": "Revenues", "year": 2023, "form_type": "10-K"},
            html_content="<html>mock html</html>",
            extracted_value=None,
            error=None,
            success=True
        )
        
        result = extract_xbrl_data_node(state_with_html)
        
        assert result["success"] is False
        assert "无法在财报中找到指标" in result["error"]

@pytest.mark.asyncio
class TestLangGraphWorkflow:
    """测试LangGraph完整工作流"""
    
    @patch('src.langgraph_orchestrator.llm')
    @patch('src.langgraph_orchestrator.get_filing_html')
    @patch('src.langgraph_orchestrator.extract_metric_from_html')
    async def test_end_to_end_workflow_success(self, mock_extract_metric, mock_get_filing_html, mock_llm):
        """测试端到端工作流成功情况"""
        # 模拟所有步骤
        mock_response = Mock()
        mock_response.content = '{"ticker": "AAPL", "metric": "Revenues", "year": 2023, "form_type": "10-K"}'
        mock_llm.return_value = mock_response
        
        mock_get_filing_html.return_value = "<html>mock SEC data</html>"
        mock_extract_metric.return_value = ("383285000000", "usd")
        
        # 测试完整工作流
        result = await process_query_with_langgraph("Apple 2023年的收入是多少？")
        
        assert result["success"] is True
        assert result["query"] == "Apple 2023年的收入是多少？"
        assert result["parsed_intent"]["ticker"] == "AAPL"
        assert result["result"]["value"] == "383285000000"
        assert result["result"]["unit"] == "usd"
    
    @patch('src.langgraph_orchestrator.llm')
    async def test_end_to_end_workflow_parse_failure(self, mock_llm):
        """测试端到端工作流解析失败"""
        # 模拟解析失败
        mock_response = Mock()
        mock_response.content = '{"error": "无法理解查询"}'
        mock_llm.return_value = mock_response
        
        result = await process_query_with_langgraph("无法理解的查询")
        
        assert result["success"] is False
        assert "无法理解查询" in result["error"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 