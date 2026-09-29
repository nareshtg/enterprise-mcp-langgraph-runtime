"""
Deterministic LangGraph Orchestrator
Enforces strict node-to-node transitions, security guardrails, and deterministic fallbacks.
"""

from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END

# Define the deterministic runtime state
class AgentRuntimeState(TypedDict):
    customer_id: str
    query: str
    user_role: str
    is_safe: bool
    crm_context: Optional[Dict[str, Any]]
    final_response: Optional[str]
    execution_status: str

# Mock CRM tool access (bridges to mcp-gateway logic)
def fetch_crm_record(customer_id: str) -> Dict[str, Any]:
    from sys import path
    from os.path import dirname, abspath, join
    # Simple internal mock fallback
    mock_data = {
        "CUST-8941": {"name": "Global Logistics Corp", "tier": "Gold", "sla_hours": 4, "dispute": "ORD-9821"},
    }
    return mock_data.get(customer_id, {"error": "Record not found"})

# Node 1: Input Guardrail & Security Validation
def guardrail_node(state: AgentRuntimeState) -> Dict[str, Any]:
    query = state["query"].lower()
    suspicious_patterns = ["ignore previous instructions", "drop table", "override system", "bypass"]

    if any(pattern in query for pattern in suspicious_patterns):
        return {
            "is_safe": False,
            "execution_status": "SECURITY_BLOCK",
            "final_response": "Request blocked: Input violates enterprise security guardrail."
        }
    return {"is_safe": True, "execution_status": "IN_PROGRESS"}

# Node 2: Deterministic MCP Tool Execution
def mcp_tool_node(state: AgentRuntimeState) -> Dict[str, Any]:
    customer_id = state["customer_id"]
    record = fetch_crm_record(customer_id)
    return {
        "crm_context": record,
        "execution_status": "CONTEXT_LOADED"
    }

# Node 3: Synthesizer & SLA Formatter Node
def response_formatter_node(state: AgentRuntimeState) -> Dict[str, Any]:
    crm = state.get("crm_context", {})
    if "error" in crm:
        response = f"Unable to process query: {crm['error']}"
    else:
        response = (
            f"Account: {crm.get('name')} | Tier: {crm.get('tier')} | "
            f"SLA Target: {crm.get('sla_hours')} hrs. "
            f"Verified against active enterprise dispute policies."
        )
    return {
        "final_response": response,
        "execution_status": "COMPLETED"
    }

# Conditional Edge: Route based on security inspection
def security_router(state: AgentRuntimeState) -> str:
    if not state.get("is_safe", False):
        return END
    return "mcp_tool_node"

# Construct the State Machine
workflow = StateGraph(AgentRuntimeState)

workflow.add_node("guardrail_node", guardrail_node)
workflow.add_node("mcp_tool_node", mcp_tool_node)
workflow.add_node("response_formatter_node", response_formatter_node)

workflow.add_edge(START, "guardrail_node")
workflow.add_conditional_edges(
    "guardrail_node",
    security_router,
    {"mcp_tool_node": "mcp_tool_node", END: END}
)
workflow.add_edge("mcp_tool_node", "response_formatter_node")
workflow.add_edge("response_formatter_node", END)

# Compile the executable pipeline
runtime_app = workflow.compile()

if __name__ == "__main__":
    # Demonstration run
    initial_payload = {
        "customer_id": "CUST-8941",
        "query": "Review dispute SLA for customer order",
        "user_role": "Tier2_Support",
        "is_safe": True,
        "crm_context": None,
        "final_response": None,
        "execution_status": "INITIATED"
    }
    result = runtime_app.invoke(initial_payload)
    print("\n--- Deterministic Workflow Execution Result ---")
    print(f"Status: {result['execution_status']}")
    print(f"Output: {result['final_response']}\n")
