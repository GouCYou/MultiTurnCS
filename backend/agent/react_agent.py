# agent/react_agent.py
import json
from typing import List, Dict, Any, Tuple, Union

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

from backend.tools.order_tools import (
    lookup_order,
    get_tracking,
    check_return_eligibility,
    create_after_sale,
    create_ticket,
    issue_coupon
)
from backend.tools.product_tools import (
    search_products_by_name,
    get_product_detail
)

# ====== 核心提示词：让它像“真实客服 SOP” ======
REACT_PROMPT = """你是一个专业、耐心、流程清晰的电商客服智能体。你必须遵循SOP：
1) 先确认用户诉求（查订单/查物流/退货退款/催件/投诉/商品查询/其他）。
2) 如信息不足，先追问必要信息（订单号、手机号尾号、收件人、商品名称关键词等）。
3) 涉及事实信息（订单状态、物流轨迹、是否可退、商品信息）必须调用工具获取，禁止凭空编造。
4) 当用户询问商品相关信息时，应使用search_products_by_name工具根据商品名称关键词进行查询。
5) 回复模板必须包含：当前进展/结论 + 下一步建议 + 如需补充信息则明确追问。
6) 对投诉/着急等情绪，先致歉+安抚，再给出动作（如创建工单、发补偿券）。

你可以使用以下工具:
{tools}

工具使用规范（必须严格输出格式）：
Thought: 你的思考
Action: 工具名称（必须是 {tool_names} 之一）
Action Input: 工具输入（必须是JSON对象字符串）
Observation: 工具返回结果
...（如需多次调用工具可重复以上步骤）
Final Answer: 给用户的最终回复（中文，客服口吻，按模板）

重要提醒：
- Action Input 必须是 JSON 对象字符串，例如：订单查询时传入键 order_id，可能还需要 phone_tail 或 receiver。
- 如果缺少必要信息，先在 Final Answer 里追问，不要强行调用工具。

现在开始！

对话历史：
{history}

用户输入：
{input}

{agent_scratchpad}
"""


def _parse_json(s: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """把 Action Input 解析成 dict。兼容：已经是dict / JSON字符串 / 非法字符串。"""
    if isinstance(s, dict):
        return s
    if not isinstance(s, str):
        return {}
    s = s.strip()
    if not s:
        return {}
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def build_agent(llm) -> AgentExecutor:
    tools = [
        Tool(
            name="lookup_order",
            func=lambda s: lookup_order(**_parse_json(s)),
            description="查询订单。输入JSON键：order_id（必填），phone_tail/receiver（可选用于校验）。返回订单信息或失败原因。"
        ),
        Tool(
            name="get_tracking",
            func=lambda s: get_tracking(**_parse_json(s)),
            description="查询物流轨迹。输入JSON键：tracking_no（必填）。返回物流节点列表（模拟）。"
        ),
        Tool(
            name="check_return_eligibility",
            func=lambda s: check_return_eligibility(**_parse_json(s)),
            description="判断是否可退。输入JSON键：order_id（必填）。返回eligible与reason。"
        ),
        Tool(
            name="create_after_sale",
            func=lambda s: create_after_sale(**_parse_json(s)),
            description="创建售后单。输入JSON键：order_id（必填），after_sale_type（可选），reason（可选）。返回售后单号与下一步。"
        ),
        Tool(
            name="create_ticket",
            func=lambda s: create_ticket(**_parse_json(s)),
            description="创建工单（投诉/催件/异常升级）。输入JSON键：ticket_type（必填），detail（必填），order_id/priority（可选）。返回工单号。"
        ),
        Tool(
            name="issue_coupon",
            func=lambda s: issue_coupon(**_parse_json(s)),
            description="发放补偿券。输入JSON键：receiver（必填），amount/reason（可选）。返回券码。"
        ),
        Tool(
            name="search_products_by_name",
            func=lambda s: search_products_by_name(**_parse_json(s)),
            description="根据商品名称模糊查询商品。输入JSON键：name（必填，商品名称关键词），max_results（可选，返回的最大结果数）。返回查询结果列表。"
        ),
        Tool(
            name="get_product_detail",
            func=lambda s: get_product_detail(**_parse_json(s)),
            description="根据商品ID查询商品详情。输入JSON键：product_id（必填）。返回商品详细信息。"
        ),
    ]

    prompt = PromptTemplate.from_template(REACT_PROMPT)

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=6
    )
    return executor


def run_agent(executor: AgentExecutor, user_msg: str, history: List[Dict[str, str]]) -> Tuple[str, List[Any]]:
    # 历史合并（给模型看）
    hist_lines = []
    for m in history[-10:]:
        role = m.get("role", "")
        content = m.get("content", "")
        hist_lines.append(f"{role}: {content}")
    hist_text = "\n".join(hist_lines)

    merged_input = {
        "input": user_msg,
        "history": hist_text
    }

    result = executor.invoke(merged_input)
    answer = result.get("output", "")
    steps = result.get("intermediate_steps", [])
    return answer, steps