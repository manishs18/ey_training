from typing import Annotated, Literal
from typing_extensions import TypedDict
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.graph_edge import add_messages
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from tools import TOOL_BELT, TOOL_MAP

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    action_approved: bool  # Flag mutated by the human gate intervention checkpoint

# 2. Resilient LLM Layer with Caching Strategy
@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def call_llm_with_retry(messages):
    """Invokes Model. System message anchor provides fixed context optimization for prompt caching."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm.bind_tools(TOOL_BELT)(messages)

# 3. Nodes and Routing Logics
def agent_router(state: AgentState) -> Literal["human_approval_gate", "execute_tools", "__end__"]:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "issue_refund":
            return "human_approval_gate"
            
    return "execute_tools"

def call_agent_node(state: AgentState):
    system_anchor = SystemMessage(
        content="You are a senior automated customer routing agent. You have real-time capabilities to query logs, "
                "save structured long-term insights via memory vectors, and handle heavy data transformations asynchronously."
    )
    response = call_llm_with_retry([system_anchor] + state["messages"])
    return {"messages": [response], "action_approved": False}

def human_approval_gate_node(state: AgentState):
    """No-op execution point. Programmatic graph execution halts BEFORE processing this node."""
    pass

def execute_tools_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    tool_outputs = []
    
    for tool_call in last_message.tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        
        # Intercept if human safety validation failed
        if name == "issue_refund" and not state.get("action_approved", False):
            output_msg = ToolMessage(
                content="Rejected: Operational action denied due to insufficient supervisor clearance parameters.",
                tool_call_id=tool_call["id"]
            )
        else:
            executed_result = TOOL_MAP[name].invoke(args)
            output_msg = ToolMessage(content=str(executed_result), tool_call_id=tool_call["id"])
            
        tool_outputs.append(output_msg)
        
    return {"messages": tool_outputs}

# 4. Constructing State Machine Pipeline
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_agent_node)
workflow.add_node("human_approval_gate", human_approval_gate_node)
workflow.add_node("execute_tools", execute_tools_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    agent_router,
    {
        "human_approval_gate": "human_approval_gate",
        "execute_tools": "execute_tools",
        END: END
    }
)
workflow.add_edge("execute_tools", "agent")
workflow.add_edge("human_approval_gate", "execute_tools")

# Compile with a persistence framework checkpoint to enable manual interventions
agent_application = workflow.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human_approval_gate"]
)