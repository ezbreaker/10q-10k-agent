"""
基于LangGraph的编排器
更好的状态管理和工作流控制
"""

from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json

from .sec_retriever import get_filing_html
from .xbrl_extractor import extract_metric_from_html
from .config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, TICKER_TO_CIK

class WorkflowState(TypedDict):
    """工作流状态"""
    query: str                    # 用户查询
    parsed_intent: Optional[Dict] # 解析的意图
    html_content: Optional[str]   # SEC HTML内容
    extracted_value: Optional[Dict] # 提取的值
    error: Optional[str]          # 错误信息
    success: bool                 # 是否成功

# LLM配置
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=OPENAI_TEMPERATURE,
    openai_api_key=OPENAI_API_KEY
)

def parse_intent_node(state: WorkflowState) -> WorkflowState:
    """解析用户意图的节点"""
    query = state["query"]
    
    system_prompt = """你是一个财务数据助手。用户会用自然语言询问公司财务数据。

请解析用户查询并返回JSON格式的结构化信息：
{
    "ticker": "股票代码 (如AAPL, MSFT等)",
    "metric": "财务指标 (如Revenues, NetIncome等)",
    "year": "年份 (如2023, 2022等)",
    "form_type": "财报类型 (10-K或10-Q，默认10-K)"
}

支持的公司：Apple(AAPL), Microsoft(MSFT), Google(GOOGL), Amazon(AMZN), Tesla(TSLA), Meta(META), NVIDIA(NVDA), Netflix(NFLX)
支持的指标：Revenues(收入), NetIncome(净利润), TotalAssets(总资产), TotalLiabilities(总负债), StockholdersEquity(股东权益)

如果无法解析，返回：{"error": "无法理解查询"}
"""
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = llm.invoke(messages)
        parsed_content = response.content.strip()
        
        # 尝试解析JSON
        try:
            parsed_intent = json.loads(parsed_content)
            if "error" in parsed_intent:
                return {
                    **state,
                    "error": parsed_intent["error"],
                    "success": False
                }
            else:
                return {
                    **state,
                    "parsed_intent": parsed_intent,
                    "success": True
                }
        except json.JSONDecodeError:
            return {
                **state,
                "error": "LLM返回的不是有效JSON格式",
                "success": False
            }
            
    except Exception as e:
        return {
            **state,
            "error": f"意图解析失败: {str(e)}",
            "success": False
        }

def retrieve_sec_data_node(state: WorkflowState) -> WorkflowState:
    """检索SEC数据的节点"""
    if not state["success"] or not state["parsed_intent"]:
        return state
    
    intent = state["parsed_intent"]
    
    try:
        ticker = intent["ticker"]
        year = int(intent["year"])  # 确保年份是整数
        form_type = intent.get("form_type", "10-K")
        
        # 验证ticker
        if ticker not in TICKER_TO_CIK:
            return {
                **state,
                "error": f"不支持的股票代码: {ticker}",
                "success": False
            }
        
        # 检索SEC数据
        html_content = get_filing_html(ticker, year, form_type)
        
        return {
            **state,
            "html_content": html_content,
            "success": True
        }
        
    except Exception as e:
        return {
            **state,
            "error": f"SEC数据检索失败: {str(e)}",
            "success": False
        }

def extract_xbrl_data_node(state: WorkflowState) -> WorkflowState:
    """提取XBRL数据的节点"""
    if not state["success"] or not state["html_content"] or not state["parsed_intent"]:
        return state
    
    intent = state["parsed_intent"]
    html_content = state["html_content"]
    
    # 指标映射 - 支持多种可能的标签
    METRIC_TAG_MAPPING = {
        "Revenues": ["us-gaap:Revenues", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"],
        "Revenue": ["us-gaap:Revenues", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"], 
        "NetIncome": ["us-gaap:NetIncomeLoss"],
        "Net Income": ["us-gaap:NetIncomeLoss"],
        "TotalAssets": ["us-gaap:Assets"],
        "Total Assets": ["us-gaap:Assets"],
        "TotalLiabilities": ["us-gaap:Liabilities"],
        "Total Liabilities": ["us-gaap:Liabilities"],
        "StockholdersEquity": ["us-gaap:StockholdersEquity"],
        "Stockholders Equity": ["us-gaap:StockholdersEquity"],
    }
    
    try:
        metric = intent["metric"]
        metric_tags = METRIC_TAG_MAPPING.get(metric, [metric])
        
        # 如果是字符串，转换为列表
        if isinstance(metric_tags, str):
            metric_tags = [metric_tags]
        
        # 尝试所有可能的标签
        result = None
        used_tag = None
        
        for metric_tag in metric_tags:
            # 如果不是标准XBRL标签，尝试添加前缀
            if not metric_tag.startswith("us-gaap:"):
                if ":" not in metric_tag:
                    metric_tag = f"us-gaap:{metric_tag}"
            
            # 提取数据
            result = extract_metric_from_html(html_content, metric_tag)
            if result is not None:
                used_tag = metric_tag
                break
        
        if result is None:
            attempted_tags = ", ".join(metric_tags)
            return {
                **state,
                "error": f"无法在财报中找到指标: {metric} (尝试的XBRL标签: {attempted_tags})",
                "success": False
            }
        
        value, unit = result
        
        extracted_value = {
            "ticker": intent["ticker"],
            "metric": metric,
            "xbrl_tag": used_tag,
            "year": intent["year"],
            "form_type": intent.get("form_type", "10-K"),
            "value": value,
            "unit": unit
        }
        
        return {
            **state,
            "extracted_value": extracted_value,
            "success": True
        }
        
    except Exception as e:
        return {
            **state,
            "error": f"XBRL数据提取失败: {str(e)}",
            "success": False
        }

def should_continue(state: WorkflowState) -> str:
    """决定工作流是否继续"""
    if state["success"]:
        return "continue"
    else:
        return END

def build_workflow() -> StateGraph:
    """构建LangGraph工作流"""
    workflow = StateGraph(WorkflowState)
    
    # 添加节点
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("retrieve_sec_data", retrieve_sec_data_node)
    workflow.add_node("extract_xbrl_data", extract_xbrl_data_node)
    
    # 定义边
    workflow.set_entry_point("parse_intent")
    
    workflow.add_conditional_edges(
        "parse_intent",
        should_continue,
        {
            "continue": "retrieve_sec_data",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "retrieve_sec_data", 
        should_continue,
        {
            "continue": "extract_xbrl_data",
            END: END
        }
    )
    
    workflow.add_edge("extract_xbrl_data", END)
    
    return workflow.compile()

# 创建编译后的工作流
compiled_workflow = build_workflow()

async def process_query_with_langgraph(query: str) -> Dict[str, Any]:
    """使用LangGraph处理查询"""
    initial_state = WorkflowState(
        query=query,
        parsed_intent=None,
        html_content=None,
        extracted_value=None,
        error=None,
        success=False
    )
    
    try:
        # 执行工作流
        result = await compiled_workflow.ainvoke(initial_state)
        
        if result["success"]:
            return {
                "query": query,
                "parsed_intent": result["parsed_intent"],
                "result": result["extracted_value"],
                "success": True
            }
        else:
            return {
                "query": query,
                "error": result["error"],
                "success": False
            }
            
    except Exception as e:
        return {
            "query": query,
            "error": f"工作流执行失败: {str(e)}",
            "success": False
        } 