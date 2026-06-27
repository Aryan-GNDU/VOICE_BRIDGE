"""Conversation memory support."""

from langgraph.checkpoint.memory import InMemorySaver


class AgentMemory:
    """Thread-scoped memory backed by a LangGraph checkpointer.

    InMemorySaver is simple and fast for a single process. For multi-instance
    deployments, swap this class for a Redis/Postgres checkpointer without
    changing the API or service layers.
    """

    def __init__(self) -> None:
        self.checkpointer = InMemorySaver()

    def reset_thread(self, thread_id: str) -> None:
        """Best-effort memory reset for the given thread.

        LangGraph checkpointers expose persistence operations differently across
        backends. For the in-memory implementation, clearing the storage for a
        thread keeps the public API stable while avoiding backend leakage.
        """
        storage = getattr(self.checkpointer, "storage", None)
        writes = getattr(self.checkpointer, "writes", None)
        if isinstance(storage, dict):
            storage.pop(thread_id, None)
        if isinstance(writes, dict):
            keys = [key for key in writes if key[0] == thread_id]
            for key in keys:
                writes.pop(key, None)
