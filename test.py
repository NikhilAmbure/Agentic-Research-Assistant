import time
import uuid

from pprint import pprint
from langgraph.types import Command
from agent.graph import graph

start = time.time()
print(f'Start time: {start}')


print("======================================================================================")
config = {"configurable": {"thread_id": str(uuid.uuid4())}, "max_concurrency": 10}
out = graph.invoke({"topic": "Impact of AI agents on software engineering jobs"}, config)

if out.get("blocked"):
    print("BLOCKED:", out["blocked"])

while "__interrupt__" in out:
    payload = out["__interrupt__"][0].value
    print("======================================================================================")
    print("\n", payload["draft"])
    print("======================================================================================")

    print("\nWARNINGS:", payload["warnings"])
    print("======================================================================================")

    print("\nUNRESOLVED ISSUES:")
    for i in payload["unresolved_issues"]:
        print(f"  [{i['citation']}] {i['sentence'][:90]}... -> {i['problem'] or 'no reason given'}")
    print("======================================================================================")

    if input("\napprove / reject? ").strip().lower() == "approve":
        resume = {"action": "approve"}
    else:
        resume = {"action": "reject", "feedback": input("Feedback: ")}
    out = graph.invoke(Command(resume=resume), config)

print("APPROVED:", out.get("approved"))
print("======================================================================================")

end = time.time()
print(f'Elapsed: {end - start:.2f} seconds')














