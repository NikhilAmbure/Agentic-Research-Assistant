from agent.graph import graph
import pprint

out = graph.invoke({"topic": "Impact of AI agents on software engineering jobs"})
pprint.pprint("SUBTASKS:", *out["subtasks"], sep="\n- ")
pprint.pprint("\n", out["draft"])
pprint.pprint(out["insights"])