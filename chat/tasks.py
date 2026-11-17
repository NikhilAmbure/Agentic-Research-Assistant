from celery import shared_task
from langgraph.types import Command

from agent.service import get_graph, thread_config


@shared_task
def run_research(thread_id: str, topic: str):
    get_graph().invoke({"topic": topic}, thread_config(thread_id))


@shared_task
def resume_research(thread_id: str, action: str, feedback: str = ""):
    resume = {"action": action, "feedback": feedback}
    get_graph().invoke(Command(resume=resume), thread_config(thread_id))