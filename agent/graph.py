import os

from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq

from .state import AgentState
from .tools import tools

# graph.py

SYSTEM_PROMPT = """You are a helpful AI assistant with access to these tools:

- web_search: Search the internet for real-time information
- calculator: Evaluate mathematical expressions  
- python_executor: Run Python code
- file_reader: Read local text files

Always use the appropriate tool when needed. /no_think
"""

def _get_llm():
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        api_key=os.getenv("GROQ_API_KEY", ""),
        temperature=0,
        max_retries=2,
    )
    return llm.bind_tools(tools)


# Nodes 

def agent_node(state: AgentState):
    """Call the LLM with bound tools."""
    llm = _get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state.messages)
    response = llm.invoke(messages)
    return {"messages": [response]}


#Router 

def should_continue(state: AgentState) -> str:
    """Route to tool node if LLM made a tool call, otherwise end."""
    last = state.messages[-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


# Graph

def build_graph():
    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    # ReAct loop: agent → (tools → agent)* → END
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )
    graph.add_edge("tools", "agent")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# Compiled once at import time
agent_graph = build_graph()