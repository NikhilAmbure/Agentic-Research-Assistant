from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class AgentState(BaseModel):
    # topic: str
    # research_tasks: str
    # sources: str
    # findings: list
    messages: Annotated[
        Sequence[BaseMessage],
        add_messages
    ]