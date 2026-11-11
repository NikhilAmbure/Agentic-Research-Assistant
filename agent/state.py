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

class Issue(TypedDict):
    sentence: str
    citation: int
    problem: str

class AppState(TypedDict, total=False):
    topic: str
    subtasks: list[str]
    sources: Annotated[list[Source], operator.add]
    insights: list[Insight]
    draft: str
    references: list[str]   # URL order behind the [n] citations
    issues: list[Issue]     # latest fact-check findings
    revisions: int          # number of drafts written so far
    blocked: str            # non-empty = request rejected, with the reason
    warnings: list[str]     # output-guard findings
    patch_rounds: int       # reviser rounds since the last full draft
    human_feedback: str     # reviewer's rejection note
    approved: bool