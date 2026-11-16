import sys
import uuid

from langgraph.types import Command

from agent.service import close_pool, get_graph, thread_config

graph = get_graph()

if sys.argv[1] == "start":
    thread_id = str(uuid.uuid4())
    topic = "Impact of AI agents on software engineering jobs"
    out = graph.invoke({"topic": topic}, thread_config(thread_id))
    print("PAUSED. thread_id =", thread_id)
    print("warnings:", out["__interrupt__"][0].value["warnings"])
else:
    out = graph.invoke(Command(resume={"action": "approve"}), thread_config(sys.argv[2]))
    print("approved:", out.get("approved"))

close_pool()