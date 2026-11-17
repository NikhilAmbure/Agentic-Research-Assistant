# get_graph() builds the graph with the Postgres checkpointer, 
# and research_status() reads the checkpoint

import os
from functools import lru_cache

from django.core.cache import cache
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .graph import build_graph

def thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": str(thread_id)}, "max_concurrency": 10}


_pool = None


@lru_cache(maxsize=1)
def get_graph():
    # Created lazily so each Celery worker process opens its own pool.
    global _pool
    _pool = ConnectionPool(
        conninfo=os.environ["CHECKPOINT_DB_URI"],
        max_size=10,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
    )
    saver = PostgresSaver(_pool)
    saver.setup()   # creates checkpoint tables, safe to repeat
    return build_graph(saver)

def close_pool():
    if _pool is not None:
        _pool.close()


def research_status(thread_id: str) -> dict | None:
    snap = get_graph().get_state(thread_config(thread_id))
    values = snap.values or {}
    if not values and not snap.next:
        return {"status": "queued"} if cache.get(f"research:{thread_id}") else None
    if snap.next:
        for task in snap.tasks:
            if task.interrupts:
                return {"status": "awaiting_review", **task.interrupts[0].value}
        return {"status": "running", "step": list(snap.next)}
    if values.get("blocked"):
        return {"status": "blocked", "reason": values["blocked"]}
    return {
        "status": "approved" if values.get("approved") else "finished",
        "report": values.get("draft"),
        "warnings": values.get("warnings", []),
    }