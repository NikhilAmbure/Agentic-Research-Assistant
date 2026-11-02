from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from langgraph.types import Send
from .state import AppState
from collections import defaultdict
from .tools import search_web
from langchain_groq import ChatGroq

load_dotenv()
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_output_tokens=8192)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

class Plan(BaseModel):
    subtasks: list[str] = Field(
        description="4-6 distinct, specific, searchable research questions"
    )

class InsightItem(BaseModel):
    claim: str = Field(description="One specific, self-contained factual claim")
    source_url: str = Field(description="Exactly one of the provided source URLs")

class Analysis(BaseModel):
    insights: list[InsightItem] = Field(description="At most 8 key insights")


analyst_llm = llm.with_structured_output(Analysis)


def fan_out(state: AppState):
    return [Send("researcher", {"subtask": st}) for st in state["subtasks"]]


def orchestrator(state: AppState) -> dict:
    planner = llm.with_structured_output(Plan)
    plan = planner.invoke(
        f"Break this topic into 4-6 distinct research subtasks:\n{state['topic']}"
    )
    return {"subtasks": plan.subtasks}


def researcher(payload: dict) -> dict:
    subtask = payload["subtask"]
    return {"sources": [{"subtask": subtask, **r} for r in search_web(subtask)]}


def analyst(state: AppState) -> dict:
    by_subtask = defaultdict(list)
    for s in state["sources"]:
        by_subtask[s["subtask"]].append(s)

    subtasks = list(by_subtask)
    prompts = []
    for st in subtasks:
        ctx = "\n\n".join(f"URL: {s['url']}\n{s['content']}" for s in by_subtask[st])
        prompts.append(
            f"Research question: {st}\n\n"
            "Extract at most 8 key factual claims that help answer it. Each claim "
            "must be specific, self-contained, and stated in the source you cite. "
            "Skip fluff.\n\n" + ctx
        )

    results = analyst_llm.batch(
        prompts, config={"max_concurrency": 3}, return_exceptions=True
    )

    insights = []
    for st, res in zip(subtasks, results):
        if isinstance(res, Exception):
            print(f"[analyst] skipped subtask after error: {st[:60]}... ({res})")
            continue
        valid_urls = {s["url"] for s in by_subtask[st]}
        for item in res.insights:
            if item.source_url in valid_urls:
                insights.append(
                    {"subtask": st, "claim": item.claim, "source_url": item.source_url}
                )
    return {"insights": insights}


def writer(state: AppState) -> dict:
    urls = list(dict.fromkeys(i["source_url"] for i in state["insights"]))
    idx = {u: n for n, u in enumerate(urls, 1)}
    facts = "\n".join(
        f"- ({i['subtask']}) {i['claim']} [{idx[i['source_url']]}]"
        for i in state["insights"]
    )
    refs = "\n".join(f"[{n}] {u}" for u, n in idx.items())
    prompt = (
        f"Write a structured research report on: {state['topic']}\n\n"
        "Use ONLY the facts below. Include a title, executive summary, one "
        "section per theme, and keep the [n] citation after each claim. "
        "End with a References section.\n\n"
        f"FACTS:\n{facts}\n\nREFERENCES:\n{refs}"
    )
    return {"draft": llm.invoke(prompt).content}



builder = StateGraph(AppState)
builder.add_node("orchestrator", orchestrator)
builder.add_node("researcher", researcher)
builder.add_node("analyst", analyst)
builder.add_node("writer", writer)

builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", fan_out, ["researcher"])
builder.add_edge("researcher", "analyst")
builder.add_edge("analyst", "writer")
builder.add_edge("writer", END)

graph = builder.compile()