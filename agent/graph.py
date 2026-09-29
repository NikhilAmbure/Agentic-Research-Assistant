import os

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import AgentState
from .tools import tools

RESEARCHER_SYSTEM_PROMPT = """
You are a research agent.

Your responsibility is to investigate a research topic using
the web_search tool.

You should:
1. Identify what information is needed.
2. Search for relevant sources.
3. Examine the search results.
4. Perform additional searches when the evidence is insufficient.
5. Prefer reliable and relevant sources.
6. Separate factual findings from assumptions.
7. Produce concise research notes with source URLs.

Do not write the final polished report.
Your job is to gather evidence for downstream agents.
"""

def _get_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=os.getenv("GEMINI_API_KEY", ""),
        temperature=0,
        max_retries=2,
    )

    return llm.bind_tools(tools)

# Nodes
def agent_node(state: AgentState):
    """Call the LLM with bound tools."""
    llm = _get_llm()
    messages = [
        SystemMessage(content=RESEARCHER_SYSTEM_PROMPT)
    ] + list(state.messages)

    response = llm.invoke(messages)
    return {"messages": [response]}


# Router
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
        {
            "tools": "tools",
            END: END
        },
    )
    graph.add_edge("tools", "agent")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)

agent_graph = build_graph()