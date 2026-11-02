import operator
from typing import Annotated, TypedDict


class Source(TypedDict):
    subtask: str
    url: str
    title: str
    content: str


class Insight(TypedDict):
    subtask: str
    claim: str
    source_url: str

class AppState(TypedDict, total=False):
    topic: str
    subtasks: list[str]
    sources: Annotated[list[Source], operator.add]
    insights: list[Insight]
    draft: str

